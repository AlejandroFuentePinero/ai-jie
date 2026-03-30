"""
Notebook helper for ground truth annotation.

Typical workflow in a notebook cell:

    from src.evals.ground_truth_annotator import show, annotate, status, load

    show(0)          # read the posting

    annotate(0,
        company_name        = "Walt Disney Company",
        company_description = "Disney+ is Disney's direct-to-consumer streaming service.",
        industry            = "Media & Entertainment",
        remote_policy       = "On-site",
        employment_type     = "Full-time",
        seniority           = "mid",
        job_family          = "data_science",
        years_experience_min= 3,
        years_experience_max= None,
        key_responsibilities= [
            "Build personalisation models for content recommendations",
            "Analyse user engagement data to inform product decisions",
            "Partner with engineering to deploy models to production",
        ],
        education_required  = "Bachelor's in Computer Science, Statistics, or related field",
        skills_technical    = ["Python", "SQL", "Spark", "machine learning", "A/B testing"],
        skills_soft         = ["Cross-functional collaboration", "Strong communication skills"],
        nice_to_have        = ["Scala", "Kafka"],
        salary_min          = None,
        salary_max          = None,
        salary_currency     = None,
        salary_period       = None,
    )

    status()         # check overall progress
"""

import json
import textwrap

from src.config import GROUND_TRUTH_SAMPLE_FILE

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_all() -> list[dict]:
    records = []
    with open(GROUND_TRUTH_SAMPLE_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _save_all(records: list[dict]) -> None:
    with open(GROUND_TRUTH_SAMPLE_FILE, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _is_annotated(record: dict) -> bool:
    """A record is considered annotated if at least seniority and job_family are filled."""
    return record.get("seniority") is not None and record.get("job_family") is not None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def show(gt_id: int, width: int = 100) -> None:
    """Print the job posting for gt_id in a readable format."""
    records = _load_all()
    record = next((r for r in records if r["gt_id"] == gt_id), None)
    if record is None:
        print(f"No record with gt_id={gt_id}")
        return

    annotated = _is_annotated(record)
    tag = " [DONE]" if annotated else " [TODO]"
    sep = "─" * width

    print(sep)
    print(f"  gt_id {gt_id}{tag}  |  source_row {record['source_row']}")
    print(f"  Title:    {record['title']}")
    print(f"  Location: {record['location']}")
    print(sep)
    print()
    for line in record["description"].splitlines():
        if line.strip():
            print(textwrap.fill(line.strip(), width=width, subsequent_indent="  "))
        else:
            print()
    print()

    if annotated:
        print(sep)
        print("  Current annotation:")
        _SKIP = {"gt_id", "source_row", "title", "location", "description"}
        for k, v in record.items():
            if k not in _SKIP:
                print(f"    {k}: {v}")
        print(sep)


def annotate(gt_id: int, **fields) -> None:
    """
    Write annotation fields for gt_id back to the JSONL file.

    Only the keys you pass are updated — omitted keys are left unchanged.
    Call with keyword arguments matching the annotation schema.
    """
    _VALID = {
        "company_name", "company_description", "industry", "remote_policy",
        "employment_type", "seniority", "job_family", "years_experience_min",
        "years_experience_max", "key_responsibilities", "education_required",
        "skills_technical", "skills_soft", "nice_to_have",
        "salary_min", "salary_max", "salary_currency", "salary_period",
    }
    unknown = set(fields) - _VALID
    if unknown:
        print(f"Warning: unknown fields ignored: {unknown}")
        fields = {k: v for k, v in fields.items() if k in _VALID}

    records = _load_all()
    for record in records:
        if record["gt_id"] == gt_id:
            record.update(fields)
            _save_all(records)
            done = sum(_is_annotated(r) for r in records)
            print(f"gt_id {gt_id} saved. Progress: {done}/{len(records)}")
            return

    print(f"No record with gt_id={gt_id}")


def status() -> None:
    """Print annotation progress and list remaining gt_ids."""
    records = _load_all()
    done = [r["gt_id"] for r in records if _is_annotated(r)]
    todo = [r["gt_id"] for r in records if not _is_annotated(r)]
    print(f"Progress: {len(done)}/{len(records)} annotated")
    if todo:
        print(f"Remaining ({len(todo)}): {todo}")
    else:
        print("All done!")


def load() -> list[dict]:
    """Return all records as a list of dicts (for inspection or comparison scripts)."""
    return _load_all()
