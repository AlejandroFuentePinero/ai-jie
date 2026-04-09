"""
All deterministic post-processing for extracted Job records.

Why this layer exists:
  The LLM prompt and schema architecture (chain-of-thought scaffolding, preferred-first
  field ordering) solve the classification problem at scale. However, a small model has
  a ceiling on rule application consistency: the responsibility exclusion rule in
  skills_preferred — "exclude any skill that also appears in responsibility_skills_found"
  — is correctly understood but not reliably applied on every posting.

  This module is the deterministic safety net. It guarantees consistent output regardless
  of whether the model applied the rules correctly. The scaffolding fields make this
  possible: responsibility_skills_found gives us exact ground truth about what the model
  identified as responsibility-embedded — we use its own output to enforce the rule it missed.

Two entry points, same rules:
  postprocess(job)     — per-record, called by runner.py after each LLM extraction (eval path)
  postprocess_df(df)   — DataFrame, called by pipeline.py --push to produce the HF postprocessed dataset

  Additional fixes applied here as they are identified from full-batch analysis.
  See docs/technical_report.md §9.14 for the full post-processing layer design.
"""

import pandas as pd

from src.data_ingestion.models import Job

# ---------------------------------------------------------------------------
# Skill token blocklist
# Tokens that reflect a role, field, or domain rather than a concrete skill.
# These are removed from skills_required, skills_preferred, and skills_soft
# during postprocessing. Case-insensitive match on exact token.
# Add new entries here as they are identified from batch analysis.
# ---------------------------------------------------------------------------
_SKILL_BLOCKLIST: set[str] = {
    # Roles / job titles
    "data scientist",
    "data science",
    "data engineer",
    "data engineering",
    "data analyst",
    "machine learning engineer",
    "ml engineer",
    "software engineer",
    "software developer",
    "business analyst",
    "research scientist",
    "applied scientist",
    "software engineering",
    # Broad fields / disciplines
    "computer science",
    "information technology",
    "IT",  # same rationale
    "data analysis",
    "data analytics",
    "analytics",
    "quantitative",
    # Generic activity nouns (not skills)
    "problem solving",
    "critical thinking",
    "decision making",
    "communication",
    "teamwork",
    "collaboration",
    "leadership",
    "time management",
    "attention to detail",
    "analytical skills",
    "analytical thinking",
    "optimization",
    "simulation",
    "analytical processes",
    "structured data",
    "unstructured data",
    "data science solutions",
    "database manager",
    "Demand Generation",
    "resource optimization",
    "data pipelines",
    "reporting systems",
    "data flows",
    "report outputs",
    "derivatives",
    "interest rates",
    "credit, equity",
    "structured products",
    "systems",
    "operations",
    "models",
    "code",
    "data imputation",
    "production scale",
    "survey",
    "sales data",
    "Ph.D.",
    "PhD",
    "reliability testing",
    "fabrication",
    "testing",
    "security clearance",
    "FFRDC",
    "SETA contractors",
    "validation",
    "transfer",
    "physical testing",
    "mobile",
    "visualizations",
    "visualization",
    "finance",
    "metadata",
    "reports",
    "Computer Engineering",
    "programming courses",
    "queries",
    "Web Applications",
    "individuality",
    "creativity",
    "bioluminescence",
    "fluorescence",
    "applications",
    "commercial accounts",
    "academic accounts",
    "DVM",
    "MD",
    "on prem",
    "pipelining",
    "locallity",
}

_BLOCKLIST_LOWER: set[str] = {t.lower() for t in _SKILL_BLOCKLIST}


def _remove_blocked(tokens: list[str] | None) -> list[str]:
    if not tokens:
        return tokens or []
    return [t for t in tokens if t.lower() not in _BLOCKLIST_LOWER]


def apply_responsibility_exclusion(
    skills_preferred: list[str] | None,
    responsibility_skills_found: list[str] | None,
    skills_required: list[str] | None,
) -> tuple[list[str] | None, list[str]]:
    """
    Single source of truth for the responsibility-exclusion rule.

    Any skill that the model found in a responsibility statement must not appear
    in skills_preferred — it belongs in skills_required because it is something
    the person will actively do in the role.

    Returns (new_skills_preferred, new_skills_required).
    Called by both postprocess() (per-record, eval path) and
    postprocess_df() (DataFrame, pipeline push path).
    """
    if not responsibility_skills_found or not skills_preferred:
        return skills_preferred, skills_required or []
    overlap = set(skills_preferred) & set(responsibility_skills_found)
    if not overlap:
        return skills_preferred, skills_required or []
    new_preferred = [s for s in skills_preferred if s not in overlap]
    new_required = (skills_required or []) + sorted(overlap)
    return new_preferred, new_required


def postprocess(job: Job) -> Job:
    """
    Deterministic cleanup of known model-level inconsistencies.

    Applied immediately after parse_posting_async() returns, before serialisation.
    Returns the same Job object with corrections applied in-place.
    """
    # Responsibility exclusion — rule defined once in apply_responsibility_exclusion().
    job.skills_preferred, job.skills_required = apply_responsibility_exclusion(
        job.skills_preferred, job.responsibility_skills_found, job.skills_required
    )

    # Blocklist: remove role names, broad field labels, and generic activity nouns
    # from all three skill fields. These carry no ecological signal.
    job.skills_required = _remove_blocked(job.skills_required)
    job.skills_preferred = _remove_blocked(job.skills_preferred)
    # job.skills_soft = _remove_blocked(job.skills_soft)

    return job


def postprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the same postprocessing rules as postprocess() but over a full DataFrame.

    Used by pipeline.py at push time to produce the clean postprocessed dataset.
    Both this function and postprocess() share the same rule implementations
    (apply_responsibility_exclusion, _remove_blocked) — no logic is duplicated.

    Returns a copy of df with corrections applied.
    """
    if (
        "responsibility_skills_found" not in df.columns
        or "skills_preferred" not in df.columns
    ):
        return df

    df = df.copy()
    n_moved = 0

    for idx, row in df.iterrows():
        preferred_before = row["skills_preferred"]
        new_preferred, new_required = apply_responsibility_exclusion(
            preferred_before,
            row["responsibility_skills_found"],
            row["skills_required"],
        )
        if new_preferred != preferred_before:
            df.at[idx, "skills_preferred"] = new_preferred
            df.at[idx, "skills_required"] = new_required
            n_moved += len(set(preferred_before or []) - set(new_preferred or []))

    print(
        f"  Responsibility exclusion: moved {n_moved} skill token(s) across {len(df)} records."
    )

    for col in ("skills_required", "skills_preferred"):
        if col in df.columns:
            df[col] = df[col].apply(
                lambda tokens: (
                    _remove_blocked(tokens) if isinstance(tokens, list) else tokens
                )
            )

    return df
