"""
Unified raw jobs loader.

Reads DataScientist.csv and DataAnalyst.csv, drops artifact index columns,
keeps all columns common to both files, replaces Glassdoor sentinel values
(-1) with NaN, tags each row with its source dataset, and resets to a clean
unique integer index.

Usage (script — saves to data/raw/jobs_unified.csv):
    python -m src.data_ingestion.loader

Usage (programmatic):
    from src.data_ingestion.loader import load_raw_jobs
    df = load_raw_jobs()
"""

from pathlib import Path

import numpy as np
import pandas as pd

# Artifact index columns present in one or both files — always dropped
_DROP_COLS = {"Unnamed: 0", "index"}

# Rename only the columns the pipeline explicitly references
_RENAME = {
    "Job Title": "title",
    "Job Description": "description",
    "Location": "location",
    "Sector": "sector",          # Glassdoor broad sector — passthrough, not extracted
}

_MIN_DESCRIPTION_LEN = 200


def load_raw_jobs(
    ds_path: Path | None = None,
    da_path: Path | None | bool = None,
    min_description_len: int = _MIN_DESCRIPTION_LEN,
) -> pd.DataFrame:
    """
    Load and unify DataScientist.csv and DataAnalyst.csv.

    Args:
        ds_path: Path to DataScientist.csv. Defaults to config.RAW_DS_JOBS_FILE.
        da_path: Path to DataAnalyst.csv. Defaults to config.RAW_DA_JOBS_FILE.
                 Pass False to skip DA entirely (lite / DS-only mode).
        min_description_len: Minimum description character length to keep a row.

    Steps:
    - Drops artifact index columns (Unnamed: 0, index).
    - Keeps all columns present in DS (and DA when included).
    - Renames pipeline-facing columns to snake_case (title, description, location).
    - Adds a 'source' column ('ds' or 'da') for provenance.
    - Replaces all -1 values (Glassdoor's missing sentinel) with NaN.
    - Drops rows where description is missing or shorter than min_description_len.
    - Resets the index to a clean 0-based unique integer (used as _row_id downstream).

    Returns:
        Unified DataFrame with a clean integer index and columns:
        title, description, location, sector, Company Name, Salary Estimate, Rating,
        Headquarters, Size, Founded, Type of ownership, Revenue, Competitors, Easy Apply, source.
    """
    from src.config import RAW_DA_JOBS_FILE, RAW_DS_JOBS_FILE

    ds_path = Path(ds_path or RAW_DS_JOBS_FILE)
    skip_da = da_path is False
    da_path = None if skip_da else Path(da_path or RAW_DA_JOBS_FILE)

    ds = pd.read_csv(ds_path).drop(columns=_DROP_COLS, errors="ignore")

    if skip_da:
        ds["source"] = "ds"
        df = pd.concat([ds], ignore_index=True)
    else:
        da = pd.read_csv(da_path).drop(columns=_DROP_COLS, errors="ignore")
        # Compute common columns before adding source to either frame
        common_cols = [c for c in ds.columns if c in da.columns]
        ds = ds[common_cols]
        da = da[common_cols]
        ds["source"] = "ds"
        da["source"] = "da"
        df = pd.concat([ds, da], ignore_index=True)

    # Replace Glassdoor's -1 sentinel with NaN across all columns (numeric and string forms)
    df = df.replace(-1, np.nan).replace("-1", np.nan)

    # Rename pipeline-facing columns
    df = df.rename(columns=_RENAME)

    # Drop rows with missing or too-short descriptions
    df = df[df["description"].notna() & (df["description"].str.len() >= min_description_len)]

    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from src.config import UNIFIED_JOBS_FILE

    df = load_raw_jobs()
    counts = df["source"].value_counts().to_dict()
    print(f"Loaded {len(df)} rows — {counts}")

    UNIFIED_JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(UNIFIED_JOBS_FILE, index=True, index_label="job_id")
    print(f"Saved → {UNIFIED_JOBS_FILE}")
