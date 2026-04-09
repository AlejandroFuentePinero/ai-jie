"""
Evaluation runner: sample → extract → judge → persist results.

Sample size rationale
─────────────────────
Default n=30.  At 12 scoring dimensions that is 360 individual scores.
• Satisfies CLT (n≥30) for reliable means and confidence intervals.
• Detects a ~0.15 point regression on the 1-3 scale with ~80% power.
• Completes in ~3-5 min and costs ~$0.15 (gpt-5.4-mini for both extraction and judging).
• For pre-release / prompt-version comparisons use n=50 for tighter intervals.

Output layout (one timestamped directory per run)
──────────────────────────────────────────────────
eval_results/
  {YYYYMMDD_HHMMSS}_{prompt_version}/
    metadata.json      — run config (n, seed, models, timestamp)
    extraction_prompt.txt — exact SYSTEM_PROMPT used by the extractor
    judge_prompt.txt      — exact JUDGE_PROMPT used (reproducibility)
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
from src.data_ingestion.parser import SYSTEM_PROMPT as EXTRACTION_PROMPT
from src.data_ingestion.parser import parse_posting_async
from src.data_ingestion.postprocess import postprocess
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
    judge: bool = True,
) -> pd.DataFrame:
    """
    Run extraction (and optionally judging) on a fixed sample.

    Args:
        df:             DataFrame with columns: title, description, location.
        output_root:    Root directory for all eval runs (e.g. PROJECT_ROOT/eval_results).
        n:              Sample size. Default 30 (dev). Use 50 for pre-release comparisons.
        seed:           Fixed seed — keep constant when comparing prompt versions.
        prompt_version: Label for this run (e.g. "v1", "v2-shorter-prompt").
        concurrency:    Max concurrent API calls. Default 3 is conservative for Tier 1
                        (500 RPM shared quota). Raise to 5-8 on Tier 2+.
        judge:          Whether to run the LLM judge. Default True. Pass False to produce
                        extractions.jsonl only (for human eval).

    Returns:
        DataFrame with input fields + extraction fields (+ score fields when judge=True).
    """
    # ── Setup output directory ─────────────────────────────────────────────
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = Path(output_root) / f"{timestamp}_{prompt_version}"
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run output → {run_dir}")

    # ── Sample ────────────────────────────────────────────────────────────
    sample = df.sample(min(n, len(df)), random_state=seed).reset_index(drop=True)
    sample.index.name = "_row_id"

    _sample_cols = [c for c in ["title", "description", "location", "sector"] if c in sample.columns]
    _write_jsonl(
        run_dir / "sample.jsonl",
        [{"_row_id": i, **row[_sample_cols].to_dict()}
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
        "judge_model": JUDGE_MODEL if judge else None,
        "concurrency": concurrency,
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
    (run_dir / "extraction_prompt.txt").write_text(EXTRACTION_PROMPT)
    saved_files = "metadata.json + extraction_prompt.txt"
    if judge:
        (run_dir / "judge_prompt.txt").write_text(JUDGE_PROMPT)
        saved_files += " + judge_prompt.txt"
    print(f"  {saved_files} saved")

    # ── Extract + Judge (concurrent) ──────────────────────────────────────
    extraction_records: list[dict] = []
    score_records: list[dict] = []
    failures: list[dict] = []

    sem = asyncio.Semaphore(concurrency)

    async def process_row(row_id: int, row: pd.Series) -> None:
        async with sem:
            # Step 1 — extraction
            try:
                _sector = row.get("sector")
                extracted = await parse_posting_async(
                    row["title"], row["description"], row["location"],
                    sector=None if pd.isna(_sector) else _sector,
                )
                extracted = postprocess(extracted)
            except Exception as exc:
                failures.append({
                    "_row_id": row_id,
                    "stage": "extraction",
                    "title": row["title"],
                    "error": str(exc),
                })
                logger.warning("Row %d extraction failed: %s", row_id, exc)
                return

            extraction_records.append({
                "_row_id": row_id,
                "prompt_version": prompt_version,
                **extracted.model_dump(),
            })

            if not judge:
                return

            # Step 2 — judge (optional)
            try:
                scores = await judge_extraction_async(
                    row["title"], row["description"], extracted,
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

            score_records.append({
                "_row_id": row_id,
                **scores.model_dump(),
            })

    label = "Extract" if not judge else "Extract + Judge"
    tasks = [process_row(i, row) for i, row in sample.iterrows()]
    await tqdm_asyncio.gather(*tasks, desc=label)

    # ── Persist results ────────────────────────────────────────────────────
    _write_jsonl(run_dir / "extractions.jsonl", extraction_records)

    if failures:
        _write_jsonl(run_dir / "failures.jsonl", failures)
        print(f"\n✗ {len(failures)} failures logged to failures.jsonl")

    extractions_df = pd.DataFrame(extraction_records)

    if not judge:
        print(f"\n  Judge skipped — extractions.jsonl ready for human eval ({len(extraction_records)} records)")
        return extractions_df

    # ── Report ─────────────────────────────────────────────────────────────
    _write_jsonl(run_dir / "scores.jsonl", score_records)
    scores_df = pd.DataFrame(score_records)

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

    from src.config import EVALS_RESULTS_DIR
    from src.data_ingestion.loader import load_raw_jobs

    df = load_raw_jobs(da_path=False)
    print(f"Loaded {len(df)} rows")

    results = asyncio.run(
        run_eval(df, output_root=EVALS_RESULTS_DIR, n=RELEASE_N, seed=42, prompt_version="v33")
    )
    print(f"\nFinal results shape: {results.shape}")
