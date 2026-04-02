"""
Batch post-processing: load preprocessed jobs from HuggingFace, apply the
deterministic responsibility-exclusion rule, push the cleaned dataset to the
postprocessed HuggingFace repo.

Pipeline position
─────────────────
  pipeline.py  →  push_to_hub(-preprocessed, strip_scaffolding=False)
                         ↓
  batch_postprocess.py  →  push_to_hub(-postprocessed, strip_scaffolding=True)

The preprocessed repo retains the chain-of-thought scaffolding fields
(responsibility_skills_found, preferred_signals_found, all_technical_skills)
so that this module can apply the responsibility-exclusion rule from HF without
needing access to the local JSONL files.

Usage (script):
    python -m src.data_ingestion.batch_postprocess           # lite (DS only)
    python -m src.data_ingestion.batch_postprocess --full    # full (DS + DA)

Usage (programmatic):
    from src.data_ingestion.batch_postprocess import run_batch_postprocess
    run_batch_postprocess(full=False)
"""

import pandas as pd

from src.data_ingestion.hub import (
    HF_REPO_FULL,
    HF_REPO_FULL_POST,
    HF_REPO_LITE,
    HF_REPO_LITE_POST,
    load_from_hub,
    push_to_hub,
)


def postprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the responsibility-exclusion rule across a DataFrame of Job records.

    Any skill that appears in both skills_preferred and responsibility_skills_found
    is moved to skills_required.  Mirrors the per-record logic in postprocess.py
    but operates directly on DataFrame columns for batch efficiency.

    Returns a copy of df with corrections applied.
    """
    if "responsibility_skills_found" not in df.columns or "skills_preferred" not in df.columns:
        return df

    df = df.copy()
    n_moved = 0

    for idx, row in df.iterrows():
        resp_skills = row["responsibility_skills_found"]
        preferred = row["skills_preferred"]

        if not resp_skills or not preferred:
            continue

        overlap = set(preferred) & set(resp_skills)
        if overlap:
            df.at[idx, "skills_preferred"] = [s for s in preferred if s not in overlap]
            existing_req = row["skills_required"] or []
            df.at[idx, "skills_required"] = list(existing_req) + sorted(overlap)
            n_moved += len(overlap)

    print(f"  Responsibility exclusion: moved {n_moved} skill token(s) across {len(df)} records.")
    return df


def run_batch_postprocess(full: bool = False) -> None:
    """Load preprocessed jobs from HF, apply postprocessing, push to postprocessed repo."""
    src_repo = HF_REPO_FULL if full else HF_REPO_LITE
    dst_repo = HF_REPO_FULL_POST if full else HF_REPO_LITE_POST

    print(f"Source : {src_repo}")
    print(f"Target : {dst_repo}")
    print()

    df = load_from_hub(src_repo)
    df = postprocess_df(df)
    push_to_hub(df, repo_id=dst_repo, strip_scaffolding=True)


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path

    from dotenv import load_dotenv

    load_dotenv(override=True)

    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    parser = argparse.ArgumentParser(
        description="Postprocess jobs from HuggingFace preprocessed repo and push to postprocessed repo."
    )
    parser.add_argument(
        "--full",
        action="store_true",
        default=False,
        help="Process full dataset (DS + DA). Default: lite (DS only).",
    )
    args = parser.parse_args()

    run_batch_postprocess(full=args.full)
