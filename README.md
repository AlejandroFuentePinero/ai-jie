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
│   │   ├── pipeline.py              # Async batch runner with checkpoint/resume (lite/full modes)
│   │   ├── loader.py                # Unified CSV loader — concat, -1→NaN, clean index
│   │   └── hub.py                   # HuggingFace Hub push/pull (lite + full repos)
│   └── evals/
│       ├── judge.py                 # LLM-as-a-Judge (gpt-4o, instructor)
│       ├── runner.py                # Eval orchestrator
│       ├── report.py                # Score aggregation, group summaries, report persistence
│       ├── ground_truth_sampler.py  # Generates fixed annotation sample from DS CSV
│       └── ground_truth_annotator.py # Notebook helpers for human labelling
├── notebooks/
│   └── ground_truth_annotation.ipynb # Annotation notebook (show + annotate + status)
├── data/
│   ├── raw/                         # Source CSVs (not committed); jobs_unified.csv
│   ├── processed/                   # jobs_lite.jsonl (DS only), jobs_full.jsonl (DS+DA)
│   └── ground_truth/                # gt_sample.jsonl — 50 DS jobs for human annotation
├── eval_results/                    # Per-run eval output
├── tests/
│   └── test_industry_extraction.py  # Ground-truth industry accuracy test (Glassdoor labels)
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

Two modes — lite (DS jobs only, default) and full (DS + DA):

```bash
# Lite — DataScientist.csv only → data/processed/jobs_lite.jsonl
python -m src.data_ingestion.pipeline

# Full — DataScientist.csv + DataAnalyst.csv → data/processed/jobs_full.jsonl
python -m src.data_ingestion.pipeline --full
```

Resumes from checkpoint if interrupted. Each record is stamped with `prompt_version` for traceability.

Or from Python:

```python
import asyncio
from src.data_ingestion.loader import load_raw_jobs
from src.data_ingestion.pipeline import run_pipeline
from src.config import JOBS_LITE_JSONL_FILE

df = load_raw_jobs(da_path=False)   # DS only; omit da_path=False for full
results = asyncio.run(run_pipeline(df, output_path=JOBS_LITE_JSONL_FILE))
```

### Build the unified dataset

Merges both CSVs, drops artifact columns, replaces -1 sentinels with NaN, and saves to `data/raw/jobs_unified.csv`:

```bash
python -m src.data_ingestion.loader
```

### Push to / load from HuggingFace Hub

```python
from src.data_ingestion.hub import push_to_hub, load_from_hub, HF_REPO_LITE, HF_REPO_FULL

push_to_hub(results_df)                        # lite repo (public)
push_to_hub(results_df, repo_id=HF_REPO_FULL)  # full repo (public)
df = load_from_hub()                           # pulls lite dataset
```

### Run evaluation

Samples n records, runs extraction + judge, saves full results.

```python
import asyncio, pandas as pd
from src.evals.runner import run_eval
from src.data_ingestion.loader import load_raw_jobs
from src.config import EVALS_RESULTS_DIR

df = load_raw_jobs(da_path=False)
asyncio.run(run_eval(df, output_root=EVALS_RESULTS_DIR, n=50, seed=42, prompt_version="vN"))
```

### Compare eval versions

Use `eval_trend` — it reads all historical runs from disk and produces a trajectory CSV + plots:

```bash
python -m src.evals.eval_trend
```

Or in a notebook:

```python
from src.evals.eval_trend import build_trend, plot_trends
from src.config import EVALS_RESULTS_DIR

df = build_trend(EVALS_RESULTS_DIR)
figs = plot_trends(df, notebook_mode=True)
figs["overview"]
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
- `job_family` is title-first: a clear title keyword always overrides responsibilities-based inference. `"Data Analyst"` / `"Analytics Engineer"` → `data_analytics`
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
- `extraction_prompt.txt` — exact extractor system prompt used
- `judge_prompt.txt` — exact judge prompt used
- `sample.jsonl` — which records were sampled
- `extractions.jsonl` — raw LLM outputs
- `scores.jsonl` — per-record judge scores
- `report.json` — aggregated scores and flags

After any new run, regenerate the trajectory plots:

```bash
python -m src.evals.eval_trend
```

### Selected prompt: v9

v9 is the prompt version selected for the full batch run. The table below shows the cross-seed validation (same prompt, three independent samples):

| Run | seed | n | Overall | skills_soft | skills_technical | Notes |
|-----|------|---|---------|-------------|-----------------|-------|
| v9 | 42 | 50 | 2.92 | 2.84 | 2.98 / 2.98 | |
| v9b | 123 | 50 | 2.88 | 2.90 | 2.92 / 2.92 | |
| v9c | 999 | 50 | 2.88 | 2.94 | 2.96 / 2.96 | |
| v9d | 42 | 44 | 2.91 | 2.84 | 2.98 / 2.98 | 6 failures (TPM) |
| v9e | 123 | 47 | 2.89 | 2.89 | 2.96 / 2.96 | |
| v9f | 999 | 47 | 2.85 | 2.96 | 3.00 / 3.00 | |
| **v9g** *(fixed judge)* | **42** | **50** | **2.98** | 2.82 | 2.98 / 2.98 | **Canonical baseline** |
| v9h *(fixed judge)* | 123 | 50 | 2.94 | 2.90 | 2.98 / 2.98 | |
| v9i *(fixed judge)* | 999 | 50 | 2.88 | 2.94 | 2.98 / 2.98 | |

The **fixed judge** (v9g+) applies two corrections to `judge.py` with no change to extraction: an anti-anchoring instruction on the `overall` dimension and a forced-enumeration instruction on `skills_technical_recall`. See the technical report §8 for the full bias analysis.

**Why v9 over earlier versions:**

- `skills_soft_accuracy` jumped from 2.36 (v8b) → 2.84–2.96 across seeds. The fix was flipping `skills_soft` from a restrictive default ("null unless explicit qualifier") to an inclusive one ("err on the side of including"). This resolved a judge/extractor misalignment where the judge penalised inclusions the extractor was explicitly instructed to make.
- `job_family_accuracy` improved from 2.72 (v8b) → 2.82–2.86 by enforcing title-first priority — a clear title keyword always overrides responsibilities-based inference.
- All other dimensions held stable or improved. No regressions.
- Validated on three independent seeds — the improvements are not overfit to the development sample.

### Trajectory plots

**Overall score and flag rate across all prompt versions:**

![Eval trend overview](docs/figures/trend_overview.png)

**Score by group (company, role, skills, compensation, overall):**

![Eval trend by group](docs/figures/trend_by_group.png)

**All 17 dimensions (heatmap):**

![Eval trend all fields](docs/figures/trend_all_fields.png)

See [`docs/technical_report.md`](docs/technical_report.md) for full version history, design decisions, and the v10 Glassdoor hint experiment.

---

## Data

Source data is not committed to this repository. Place the raw CSVs in `data/raw/`:
- `DataScientist.csv` — 3,892 usable rows (DS roles)
- `DataAnalyst.csv` — 2,242 usable rows (DA roles)

Run `python -m src.data_ingestion.loader` once to generate `data/raw/jobs_unified.csv` (used for exploration; the pipeline reads raw CSVs directly).

Processed datasets on HuggingFace Hub (public):
- Lite (DS only): `Alejandrofupi/ai-jie-jobs-lite`
- Full (DS + DA): `Alejandrofupi/ai-jie-jobs-full`
