"""
HuggingFace Hub integration for the processed jobs dataset.

Push/pull the extracted Job records as a versioned Parquet dataset.

Why Parquet (via datasets library) over raw JSONL:
  - Columnar and compressed — ~5x smaller than JSONL at this row count
  - Native Arrow list types handle skills_required, skills_preferred, key_responsibilities etc.
    without any manual JSON serialisation/deserialisation
  - to_pandas() round-trips perfectly — no post-processing needed
  - Auto-generated dataset card with schema on the Hub

Usage:
    from src.data_ingestion.hub import push_to_hub, load_from_hub

    # After run_pipeline():
    push_to_hub(jobs_df)

    # In any notebook or downstream task:
    df = load_from_hub()
"""

import os

import pandas as pd

HF_REPO_LITE = "Alejandrofupi/ai-jie-jobs-lite-preprocessed"    # DS only  — raw LLM output
HF_REPO_FULL = "Alejandrofupi/ai-jie-jobs-full-preprocessed"    # DS + DA  — raw LLM output
HF_REPO_LITE_POST = "Alejandrofupi/ai-jie-jobs-lite-postprocessed"  # DS only  — after postprocessing
HF_REPO_FULL_POST = "Alejandrofupi/ai-jie-jobs-full-postprocessed"  # DS + DA  — after postprocessing

# Columns added by the pipeline runner — never useful to dataset consumers.
_META_COLS = {"_row_id", "prompt_version"}

# Chain-of-thought scaffolding fields — kept in the preprocessed push for
# inspection and debugging. Stripped from the postprocessed push (clean consumer-ready dataset).
_SCAFFOLDING_COLS = {"responsibility_skills_found", "preferred_signals_found", "all_technical_skills"}


def push_to_hub(
    df: pd.DataFrame,
    repo_id: str = HF_REPO_LITE,
    private: bool = False,
    strip_scaffolding: bool = False,
) -> None:
    """
    Push a processed jobs DataFrame to HuggingFace Hub as a Parquet dataset.

    Args:
        df:               DataFrame produced by run_pipeline(). Must contain Job fields.
        repo_id:          HuggingFace dataset repo in "owner/name" format.
        private:          Create as a private repo (default False).
        strip_scaffolding: If True, also drop the chain-of-thought scaffolding fields
                          (responsibility_skills_found, preferred_signals_found,
                          all_technical_skills). Use False for the preprocessed push
                          (raw output preserved for inspection). Use True for the
                          postprocessed push (clean consumer-ready dataset).
    """
    from datasets import Dataset

    token = _get_token()

    cols_to_strip = _META_COLS | (_SCAFFOLDING_COLS if strip_scaffolding else set())
    cols_to_drop = [c for c in cols_to_strip if c in df.columns]
    upload_df = df.drop(columns=cols_to_drop)

    print(f"Pushing {len(upload_df)} rows ({len(upload_df.columns)} columns) to {repo_id} ...")
    dataset = Dataset.from_pandas(upload_df, preserve_index=False)
    dataset.push_to_hub(repo_id, token=token, private=private)
    print(f"Done → https://huggingface.co/datasets/{repo_id}")


def load_from_hub(repo_id: str = HF_REPO_LITE) -> pd.DataFrame:
    """
    Load the processed jobs dataset from HuggingFace Hub as a DataFrame.

    Returns the full dataset (split="train" — HF default for single-split datasets).
    List-typed columns (skills_required, skills_preferred, key_responsibilities, etc.)
    are returned as Python lists, matching the original Job model structure.
    """
    from datasets import load_dataset

    token = _get_token()

    print(f"Loading {repo_id} from HuggingFace Hub ...")
    dataset = load_dataset(repo_id, token=token, split="train")
    df = dataset.to_pandas()
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns.")
    return df


def _get_token() -> str:
    token = os.getenv("HF_TOKEN")
    if not token:
        raise EnvironmentError(
            "HF_TOKEN not set. Add it to your .env file or export it as an environment variable."
        )
    return token
