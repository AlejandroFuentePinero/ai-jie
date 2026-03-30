"""
Async batch pipeline for processing all job postings.

Usage (script):
    python -m src.data_ingestion.pipeline

Usage (notebook / programmatic):
    import asyncio
    from src.data_ingestion.loader import load_raw_jobs
    from src.data_ingestion.pipeline import run_pipeline
    from src.config import JOBS_LITE_JSONL_FILE
    df = load_raw_jobs(da_path=False)
    results_df = asyncio.run(run_pipeline(df, output_path=JOBS_LITE_JSONL_FILE))
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
    prompt_version: str = "v9",
) -> pd.DataFrame:
    """
    Extract structured data from all rows in df using async concurrency.

    Args:
        df:             DataFrame with columns: title, description, location.
                        Must have a stable integer index (reset_index() first if needed).
        output_path:    Path to the output JSONL file. Results are appended
                        incrementally — safe to interrupt and resume.
        concurrency:    Max concurrent API calls. Default 20 is safe for
                        OpenAI Tier 1 (500 RPM). Raise to 80+ on Tier 2.
        prompt_version: Label for the extractor prompt used (e.g. "v9"). Stored
                        in each record for traceability; stripped before HF push.

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
                record = {"_row_id": row_id, "prompt_version": prompt_version, **extracted.model_dump()}
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
    import argparse
    import sys
    from pathlib import Path

    from dotenv import load_dotenv

    load_dotenv(override=True)

    # Allow project root on the path when run as a script
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        action="store_true",
        default=False,
        help="Process both DataScientist + DataAnalyst CSVs. Default: DS only (lite).",
    )
    args = parser.parse_args()
    lite = not args.full

    from src.config import JOBS_FULL_JSONL_FILE, JOBS_LITE_JSONL_FILE
    from src.data_ingestion.loader import load_raw_jobs

    if lite:
        # DS only — reads DataScientist.csv
        df = load_raw_jobs(da_path=False)
        output_path = JOBS_LITE_JSONL_FILE
        print(f"Mode: lite | {len(df)} DS rows → {output_path}")
    else:
        # Full — reads DataScientist.csv + DataAnalyst.csv
        df = load_raw_jobs()
        output_path = JOBS_FULL_JSONL_FILE
        print(f"Mode: full | {len(df)} rows ({df['source'].value_counts().to_dict()}) → {output_path}")

    asyncio.run(run_pipeline(df, output_path=output_path))
