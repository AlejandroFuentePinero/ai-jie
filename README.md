# AI-JIE — Automated Job Information Extraction

An end-to-end pipeline for extracting, evaluating, and versioning structured data from raw job postings using LLMs.

---

## Overview

AI-JIE takes raw job posting text and produces structured records — company, role, skills, and compensation — ready for downstream analysis. It includes a full evaluation framework using LLM-as-a-Judge to measure and iteratively improve extraction quality.

**Stack**: Python · OpenAI (`gpt-4o-mini` for extraction, `gpt-4o` for evaluation) · `instructor` · `asyncio` · HuggingFace Hub · Pydantic

---

## Features

- Async batch extraction with rate-limit-safe concurrency and checkpoint/resume
- Structured output via `instructor` — Pydantic validation + automatic retries
- LLM-as-a-Judge evaluation across 17 dimensions with version tracking
- HuggingFace Hub integration — push and pull the processed dataset as Parquet
- Full eval results saved per run: metadata, prompt snapshot, scores, flags, report

---

## Project Structure

```
ai-jie/
├── src/
│   ├── config.py                    # Paths and constants
│   ├── data_ingestion/
│   │   ├── models.py                # Pydantic schemas (Job, EvaluationScore)
│   │   ├── parser.py                # LLM extraction (gpt-4o-mini, instructor)
│   │   ├── pipeline.py              # Async batch runner with checkpoint/resume
│   │   └── hub.py                   # HuggingFace Hub push/pull
│   └── evals/
│       ├── judge.py                 # LLM-as-a-Judge (gpt-4o, instructor)
│       ├── runner.py                # Eval orchestrator
│       └── report.py                # Score aggregation and version comparison
├── notebooks/                       # Exploration notebooks
├── data/
│   ├── raw/                         # Source CSVs (not committed)
│   └── processed/                   # Extraction checkpoint (jobs.jsonl)
├── eval_results/                    # Per-run eval output
├── docs/
│   └── technical_report.md          # Design decisions and version history
└── requirements.txt
```

---

## Setup

**Prerequisites**: Python 3.10+, an OpenAI API key, a HuggingFace token (for Hub push/pull).

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
cp .env.example .env
# Edit .env and add:
#   OPENAI_API_KEY=sk-...
#   HF_TOKEN=hf_...
```

---

## Usage

### Run the extraction pipeline

Processes all raw job postings with async concurrency and writes results to JSONL. Resumes from checkpoint if interrupted.

```bash
python -m src.data_ingestion
```

Or from Python:

```python
import asyncio, pandas as pd
from src.data_ingestion import run_pipeline
from src.config import JOBS_JSONL_FILE

df = pd.read_csv("data/raw/DataScientist.csv")
results = asyncio.run(run_pipeline(df, output_path=JOBS_JSONL_FILE))
```

### Push to / load from HuggingFace Hub

```python
from src.data_ingestion import push_to_hub, load_from_hub

push_to_hub(results_df)          # uploads as Parquet to HF Hub
df = load_from_hub()             # pulls back as DataFrame
```

### Run evaluation

Samples n records, runs extraction + judge, saves full results.

```python
import asyncio, pandas as pd
from src.evals.runner import run_eval
from src.config import JOBS_JSONL_FILE

df = pd.read_json(JOBS_JSONL_FILE, lines=True)
asyncio.run(run_eval(df, output_root="eval_results", n=50, seed=42, prompt_version="v5"))
```

### Compare eval versions

```python
from src.evals.report import compare_versions

compare_versions("eval_results/20260329_061955_v3", "eval_results/20260329_063302_v4")
```

---

## Extracted Schema

Each job posting is parsed into the following structure:

**Company**: `company_name`, `company_description`, `industry`, `remote_policy`, `employment_type`

**Role**: `title`, `seniority`, `job_family`, `location`, `years_experience_min/max`, `key_responsibilities`, `education_required`

**Skills**: `skills_technical`, `skills_soft`, `nice_to_have`

**Compensation**: `salary_min`, `salary_max`, `salary_currency`, `salary_period`

Key rules enforced by the extraction prompt:
- `seniority` follows a strict priority ladder: explicit title keyword → years of experience → responsibilities tone → `"unknown"`
- `industry` reflects the company's business sector, not the technology used (e.g. a bank hiring a data scientist → `"Financial Services"`, not `"Information Technology"`)
- `skills_technical` includes all named tools, platform categories (cloud computing, BI tools), and methodology terms (machine learning, NLP, A/B testing)
- `nice_to_have` only from text using explicit keywords: "preferred", "nice to have", "a plus", "bonus", "ideally", "desirable"

---

## Evaluation

The LLM-as-a-Judge scores each extraction on 17 dimensions (1–3 scale) across five groups:

| Group | Dimensions |
|-------|------------|
| Company | name, description, industry, remote_policy, employment_type |
| Role | seniority, job_family, years_experience, education, responsibilities |
| Skills | technical_precision, technical_recall, soft, nice_to_have |
| Compensation | salary |
| Overall | null_appropriateness, overall |

Each eval run saves to `eval_results/<timestamp>_<version>/`:
- `metadata.json` — run config and timing
- `prompt.txt` — exact system prompt used
- `sample.jsonl` — which records were sampled
- `extractions.jsonl` — raw LLM outputs
- `scores.jsonl` — per-record judge scores
- `report.json` — aggregated scores and flags

**Current baseline (v3, n=50)**: overall = 2.54, 36% of rows with at least one score of 1.

See [`docs/technical_report.md`](docs/technical_report.md) for full version history and design decisions.

---

## Data

Source data is not committed to this repository. Place the raw CSVs in `data/raw/`:
- `DataScientist.csv`
- `DataAnalyst.csv`

The processed dataset is available on HuggingFace Hub: [Alejandrofupi/ai-jie-jobs](https://huggingface.co/datasets/Alejandrofupi/ai-jie-jobs) (private).
