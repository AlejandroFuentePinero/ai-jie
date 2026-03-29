"""
Async batch pipeline for processing all job postings.

Usage (script):
    python -m src.data_ingestion.pipeline

Usage (notebook / programmatic):
    import asyncio
    from src.data_ingestion.pipeline import run_pipeline
    results_df = asyncio.run(run_pipeline(df, output_path=Path("data/processed/jobs.jsonl")))
"""

import asyncio
import json
import logging
from pathlib import Path

import pandas as pd
from tqdm.asyncio import tqdm_asyncio

from .parser import parse_posting_async

logger = logging.getLogger(__name__)


async def run_pipeline(
    df: pd.DataFrame,
    output_path: Path,
    concurrency: int = 20,
) -> pd.DataFrame:
    """
    Extract structured data from all rows in df using async concurrency.

    Args:
        df:           DataFrame with columns: title, description, location.
                      Must have a stable integer index (reset_index() first if needed).
        output_path:  Path to the output JSONL file. Results are appended
                      incrementally — safe to interrupt and resume.
        concurrency:  Max concurrent API calls. Default 20 is safe for
                      OpenAI Tier 1 (500 RPM). Raise to 80+ on Tier 2.

    Returns:
        DataFrame of all successfully extracted records (including prior runs).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    failures_path = output_path.with_stem(output_path.stem + "_failures")

    # --- Load checkpoint ---
    processed_ids: set[int] = set()
    if output_path.exists():
        with open(output_path) as f:
            for line in f:
                try:
                    record = json.loads(line)
                    processed_ids.add(record["_row_id"])
                except (json.JSONDecodeError, KeyError):
                    continue
        logger.info("Checkpoint: %d rows already processed, skipping.", len(processed_ids))

    remaining = df[~df.index.isin(processed_ids)]
    total = len(df)
    skip = total - len(remaining)
    print(f"Total: {total} | Already done: {skip} | Remaining: {len(remaining)}")

    if remaining.empty:
        print("Nothing to do — all rows already processed.")
        return _load_results(output_path)

    sem = asyncio.Semaphore(concurrency)

    # File handles kept open for the duration so writes don't open/close per row.
    out_file = open(output_path, "a")
    fail_file = open(failures_path, "a")

    async def process_row(row_id: int, row: pd.Series) -> bool:
        async with sem:
            try:
                extracted = await parse_posting_async(
                    row["title"], row["description"], row["location"],
                )
                record = {"_row_id": row_id, **extracted.model_dump()}
                out_file.write(json.dumps(record, default=str) + "\n")
                out_file.flush()
                return True
            except Exception as exc:
                failure = {
                    "_row_id": row_id,
                    "title": row["title"],
                    "error": str(exc),
                }
                fail_file.write(json.dumps(failure) + "\n")
                fail_file.flush()
                logger.warning("Row %d failed: %s", row_id, exc)
                return False

    try:
        tasks = [process_row(idx, row) for idx, row in remaining.iterrows()]
        results = await tqdm_asyncio.gather(*tasks, desc="Extracting")
    finally:
        out_file.close()
        fail_file.close()

    n_ok = sum(results)
    n_fail = len(results) - n_ok
    print(f"\nDone: {n_ok} succeeded, {n_fail} failed.")
    if n_fail:
        print(f"Failures logged to: {failures_path}")

    return _load_results(output_path)


def _load_results(path: Path) -> pd.DataFrame:
    """Load the full JSONL output file into a DataFrame."""
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    records = []
    with open(path) as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    from pathlib import Path

    from dotenv import load_dotenv

    load_dotenv(override=True)

    # Allow project root on the path when run as a script
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from src.config import JOBS_JSONL_FILE, RAW_DA_JOBS_FILE, RAW_DS_JOBS_FILE

    LENGTH_THRES = 200

    frames = []
    for csv_path in [RAW_DS_JOBS_FILE, RAW_DA_JOBS_FILE]:
        raw = pd.read_csv(csv_path)
        raw = raw[["Job Title", "Job Description", "Location"]].rename(
            columns={"Job Title": "title", "Job Description": "description", "Location": "location"}
        )
        raw = raw[raw["description"].notna() & (raw["description"].str.len() >= LENGTH_THRES)]
        frames.append(raw)

    df = pd.concat(frames, ignore_index=True)
    print(f"Loaded {len(df)} rows from {len(frames)} files.")

    asyncio.run(run_pipeline(df, output_path=JOBS_JSONL_FILE))
