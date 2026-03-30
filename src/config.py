from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
RAW_DS_JOBS_FILE = RAW_DATA_DIR / "DataScientist.csv"
RAW_DA_JOBS_FILE = RAW_DATA_DIR / "DataAnalyst.csv"
UNIFIED_JOBS_FILE = RAW_DATA_DIR / "jobs_unified.csv"

# Processed data
PROCESSED_DATA_DIR = DATA_DIR / "processed"
JOBS_LITE_JSONL_FILE = PROCESSED_DATA_DIR / "jobs_lite.jsonl"   # DS only (default)
JOBS_FULL_JSONL_FILE = PROCESSED_DATA_DIR / "jobs_full.jsonl"   # DS + DA

# Evaluation results
EVALS_RESULTS_DIR = PROJECT_ROOT / "eval_results"

# HuggingFace Hub — see src/data_ingestion/hub.py for HF_REPO_LITE / HF_REPO_FULL
