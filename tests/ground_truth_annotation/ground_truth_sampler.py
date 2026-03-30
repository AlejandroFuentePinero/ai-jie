"""
Ground truth sample generator.

Draws a fixed random sample of job postings from DataScientist.csv and writes
a JSONL file where each record contains the raw text fields plus empty annotation
slots ready for human labelling.

Usage:
    python -m src.evals.ground_truth_sampler

Output:
    data/ground_truth/gt_sample.jsonl   — one record per line, ready to annotate
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

SAMPLE_SEED = 7
SAMPLE_N = 50
# Excluded seeds: 42 (dev), 123 (cross-seed val), 999 (cross-seed val)

_ANNOTATION_TEMPLATE = {
    # Company
    "company_name": None,
    "company_description": None,
    "industry": None,
    "remote_policy": None,
    "employment_type": None,
    # Role
    "seniority": None,         # intern / junior / mid / senior / lead / principal / manager / director / unknown
    "job_family": None,        # data_science / data_engineering / ml_engineering / ai_engineering /
                               # software_engineering / data_analytics / research / management / other
    "years_experience_min": None,
    "years_experience_max": None,
    "key_responsibilities": [],
    "education_required": None,
    # Skills
    "skills_technical": [],
    "skills_soft": [],
    "nice_to_have": [],
    # Compensation
    "salary_min": None,
    "salary_max": None,
    "salary_currency": None,   # ISO code e.g. USD, AUD
    "salary_period": None,     # annual / monthly / hourly
}


def build_sample(
    seed: int = SAMPLE_SEED,
    n: int = SAMPLE_N,
) -> list[dict]:
    """
    Sample n rows from DataScientist.csv and return a list of annotation records.

    Each record contains:
    - gt_id:       sequential 0-based ID for this ground truth set
    - source_row:  original DataFrame index (for traceability)
    - title:       job title (read-only reference)
    - location:    location (read-only reference)
    - description: full posting text (read-only reference)
    - All annotation fields from _ANNOTATION_TEMPLATE (fill these in)
    """
    from src.config import RAW_DS_JOBS_FILE

    raw = pd.read_csv(RAW_DS_JOBS_FILE)
    raw = (
        raw[["Job Title", "Job Description", "Location"]]
        .rename(columns={"Job Title": "title", "Job Description": "description", "Location": "location"})
        .pipe(lambda d: d[d["description"].notna() & (d["description"].str.len() >= 200)])
        .reset_index(drop=True)
    )

    indices = np.random.default_rng(seed).choice(len(raw), size=n, replace=False)
    indices = sorted(indices.tolist())

    records = []
    for gt_id, source_row in enumerate(indices):
        row = raw.iloc[source_row]
        record = {
            "gt_id": gt_id,
            "source_row": source_row,
            "title": row["title"],
            "location": row["location"],
            "description": row["description"],
            **_ANNOTATION_TEMPLATE,
            # Lists must be new instances, not shared references
            "key_responsibilities": [],
            "skills_technical": [],
            "skills_soft": [],
            "nice_to_have": [],
        }
        records.append(record)

    return records


def save_sample(output_path: Path, records: list[dict]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Saved {len(records)} records → {output_path}")


if __name__ == "__main__":
    from src.config import GROUND_TRUTH_SAMPLE_FILE

    records = build_sample()
    save_sample(GROUND_TRUTH_SAMPLE_FILE, records)
    print("\nFirst record (preview):")
    print(json.dumps({k: v for k, v in records[0].items() if k != "description"}, indent=2))
