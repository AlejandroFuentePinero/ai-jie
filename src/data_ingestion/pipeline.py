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
    prompt_version: str = "v33",
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
                _sector = row.get("sector")
                extracted = await parse_posting_async(
                    row["title"], row["description"], row["location"],
                    sector=None if pd.isna(_sector) else _sector,
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
    parser.add_argument(
        "--push",
        action="store_true",
        default=False,
        help="Push to HuggingFace: raw output → preprocessed repo, then clean output → postprocessed repo. Requires HF_TOKEN.",
    )
    parser.add_argument(
        "--postprocess",
        action="store_true",
        default=False,
        help=(
            "Skip extraction. Load the local JSONL checkpoint, apply postprocess_df(), "
            "and push to the postprocessed HF repo. Use after inspecting preprocessed output "
            "and updating blocklists/normalisation in postprocess.py. Requires HF_TOKEN."
        ),
    )
    args = parser.parse_args()
    lite = not args.full

    from src.config import JOBS_FULL_JSONL_FILE, JOBS_LITE_JSONL_FILE
    from src.data_ingestion.hub import HF_REPO_FULL, HF_REPO_FULL_POST, HF_REPO_LITE, HF_REPO_LITE_POST, push_to_hub
    from src.data_ingestion.loader import load_raw_jobs
    from src.data_ingestion.postprocess import postprocess_df

    if lite:
        output_path = JOBS_LITE_JSONL_FILE
        hf_repo_pre = HF_REPO_LITE
        hf_repo_post = HF_REPO_LITE_POST
    else:
        output_path = JOBS_FULL_JSONL_FILE
        hf_repo_pre = HF_REPO_FULL
        hf_repo_post = HF_REPO_FULL_POST

    # --postprocess: skip extraction, operate on the existing local checkpoint only.
    if args.postprocess:
        print(f"Mode: postprocess-only | Loading checkpoint from {output_path}")
        results_df = _load_results(output_path)
        if results_df.empty:
            print("ERROR: No checkpoint found. Run extraction first (without --postprocess).")
            sys.exit(1)
        print(f"Loaded {len(results_df)} records.")
        print("\nApplying postprocessing and pushing to HuggingFace (postprocessed) ...")
        clean_df = postprocess_df(results_df)
        push_to_hub(clean_df, repo_id=hf_repo_post, strip_scaffolding=True)
        sys.exit(0)

    # Normal extraction path.
    if lite:
        df = load_raw_jobs(da_path=False)
        print(f"Mode: lite | {len(df)} DS rows → {output_path}")
    else:
        df = load_raw_jobs()
        print(f"Mode: full | {len(df)} rows ({df['source'].value_counts().to_dict()}) → {output_path}")

    results_df = asyncio.run(run_pipeline(df, output_path=output_path))

    if args.push:
        print("\nStep 1/2 — Pushing raw output to HuggingFace (preprocessed) ...")
        push_to_hub(results_df, repo_id=hf_repo_pre, strip_scaffolding=False)

        print("\nStep 2/2 — Applying postprocessing and pushing to HuggingFace (postprocessed) ...")
        clean_df = postprocess_df(results_df)
        push_to_hub(clean_df, repo_id=hf_repo_post, strip_scaffolding=True)
