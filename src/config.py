from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
RAW_DS_JOBS_FILE = RAW_DATA_DIR / "DataScientist.csv"
RAW_DA_JOBS_FILE = RAW_DATA_DIR / "DataAnalyst.csv"

# Processed data
PROCESSED_DATA_DIR = DATA_DIR / "processed"
JOBS_JSONL_FILE = PROCESSED_DATA_DIR / "jobs.jsonl"

# Evaluation results
EVALS_RESULTS_DIR = PROJECT_ROOT / "eval_results"

# HuggingFace Hub
HF_REPO_JOBS = "Alejandrofupi/ai-jie-jobs"
