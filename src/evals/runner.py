"""
Evaluation runner: sample → extract → judge → persist results.

Sample size rationale
─────────────────────
Default n=30.  At 18 scoring dimensions that is 540 individual scores.
• Satisfies CLT (n≥30) for reliable means and confidence intervals.
• Detects a ~0.15 point regression on the 1-3 scale with ~80% power.
• Completes in ~3-5 min and costs ~$0.15 (gpt-4o-mini extract + gpt-4o judge).
• For pre-release / prompt-version comparisons use n=50 for tighter intervals.

Output layout (one timestamped directory per run)
──────────────────────────────────────────────────
eval_results/
  {YYYYMMDD_HHMMSS}_{prompt_version}/
    metadata.json      — run config (n, seed, models, timestamp)
    prompt.txt         — exact JUDGE_PROMPT used (reproducibility)
    sample.jsonl       — raw input rows (title, description, location)
    extractions.jsonl  — parse_posting outputs (_row_id + Job fields)
    scores.jsonl       — judge outputs (_row_id + EvaluationScore fields)
    report.json        — aggregated metrics per group + flags
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from tqdm.asyncio import tqdm_asyncio

from src.data_ingestion.parser import MODEL as EXTRACTION_MODEL
from src.data_ingestion.parser import parse_posting_async
from src.evals.judge import JUDGE_MODEL, JUDGE_PROMPT, judge_extraction_async
from src.evals.report import build_report, print_summary, save_report

logger = logging.getLogger(__name__)

# ── Sample size recommendation ───────────────────────────────────────────────
RECOMMENDED_N = 30   # development-time evals
RELEASE_N = 50       # pre-release / prompt-comparison evals


async def run_eval(
    df: pd.DataFrame,
    output_root: Path,
    n: int = RECOMMENDED_N,
    seed: int = 42,
    prompt_version: str = "v1",
    concurrency: int = 3,
) -> pd.DataFrame:
    """
    Run a full evaluation cycle on a fixed sample.

    Args:
        df:             DataFrame with columns: title, description, location.
        output_root:    Root directory for all eval runs (e.g. PROJECT_ROOT/eval_results).
        n:              Sample size. Default 30 (dev). Use 50 for pre-release comparisons.
        seed:           Fixed seed — keep constant when comparing prompt versions.
        prompt_version: Label for this run (e.g. "v1", "v2-shorter-prompt").
        concurrency:    Max concurrent API calls. Default 3 avoids gpt-4o rate limits
                        (Tier 1: 500 RPM, but gpt-4o shares quota with other calls).
                        Raise to 5-8 on Tier 2+.

    Returns:
        DataFrame with input fields + extraction fields + score fields merged.
    """
    # ── Setup output directory ─────────────────────────────────────────────
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = Path(output_root) / f"{timestamp}_{prompt_version}"
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run output → {run_dir}")

    # ── Sample ────────────────────────────────────────────────────────────
    sample = df.sample(min(n, len(df)), random_state=seed).reset_index(drop=True)
    sample.index.name = "_row_id"

    _write_jsonl(
        run_dir / "sample.jsonl",
        [{"_row_id": i, **row[["title", "description", "location"]].to_dict()}
         for i, row in sample.iterrows()],
    )

    # ── Persist run metadata and prompt ───────────────────────────────────
    metadata = {
        "timestamp_utc": timestamp,
        "prompt_version": prompt_version,
        "n_requested": n,
        "n_sampled": len(sample),
        "seed": seed,
        "extraction_model": EXTRACTION_MODEL,
        "judge_model": JUDGE_MODEL,
        "concurrency": concurrency,
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
    (run_dir / "prompt.txt").write_text(JUDGE_PROMPT)
    print(f"  metadata.json + prompt.txt saved")

    # ── Extract + Judge (concurrent) ──────────────────────────────────────
    extraction_records: list[dict] = []
    score_records: list[dict] = []
    failures: list[dict] = []

    sem = asyncio.Semaphore(concurrency)

    async def process_row(row_id: int, row: pd.Series) -> None:
        async with sem:
            # Step 1 — extraction
            try:
                extracted = await parse_posting_async(
                    row["title"], row["description"], row["location"]
                )
            except Exception as exc:
                failures.append({
                    "_row_id": row_id,
                    "stage": "extraction",
                    "title": row["title"],
                    "error": str(exc),
                })
                logger.warning("Row %d extraction failed: %s", row_id, exc)
                return

            # Step 2 — judge
            try:
                scores = await judge_extraction_async(
                    row["title"], row["description"], extracted
                )
            except Exception as exc:
                failures.append({
                    "_row_id": row_id,
                    "stage": "judge",
                    "title": row["title"],
                    "error": str(exc),
                })
                logger.warning("Row %d judge failed: %s", row_id, exc)
                return

            extraction_records.append({
                "_row_id": row_id,
                "prompt_version": prompt_version,
                **extracted.model_dump(),
            })
            score_records.append({
                "_row_id": row_id,
                **scores.model_dump(),
            })

    tasks = [process_row(i, row) for i, row in sample.iterrows()]
    await tqdm_asyncio.gather(*tasks, desc="Extract + Judge")

    # ── Persist results ────────────────────────────────────────────────────
    _write_jsonl(run_dir / "extractions.jsonl", extraction_records)
    _write_jsonl(run_dir / "scores.jsonl", score_records)

    if failures:
        _write_jsonl(run_dir / "failures.jsonl", failures)
        print(f"\n✗ {len(failures)} failures logged to failures.jsonl")

    # ── Report ─────────────────────────────────────────────────────────────
    scores_df = pd.DataFrame(score_records)
    extractions_df = pd.DataFrame(extraction_records)

    print_summary(scores_df, n_failures=len(failures))
    report = build_report(scores_df)
    save_report(report, run_dir)

    # ── Merge and return ───────────────────────────────────────────────────
    if scores_df.empty or extractions_df.empty:
        print("\n⚠  No results to merge — check failures.jsonl")
        return pd.DataFrame()

    results_df = pd.merge(extractions_df, scores_df, on="_row_id", how="inner")
    return results_df


# ── Helpers ───────────────────────────────────────────────────────────────────

def _write_jsonl(path: Path, records: list[dict]) -> None:
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec, default=str) + "\n")
    print(f"  {path.name} → {path}  ({len(records)} records)")


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from pathlib import Path

    from dotenv import load_dotenv

    load_dotenv(override=True)

    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from src.config import EVALS_RESULTS_DIR, RAW_DS_JOBS_FILE

    LENGTH_THRES = 200
    raw = pd.read_csv(RAW_DS_JOBS_FILE)
    df = (
        raw[["Job Title", "Job Description", "Location"]]
        .rename(columns={"Job Title": "title", "Job Description": "description", "Location": "location"})
        .pipe(lambda d: d[d["description"].notna() & (d["description"].str.len() >= LENGTH_THRES)])
        .reset_index(drop=True)
    )
    print(f"Loaded {len(df)} rows")

    results = asyncio.run(
        run_eval(df, output_root=EVALS_RESULTS_DIR, n=RECOMMENDED_N, seed=42, prompt_version="v1")
    )
    print(f"\nFinal results shape: {results.shape}")
