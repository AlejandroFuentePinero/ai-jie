"""
Deterministic post-processing applied to each extracted Job record immediately
after LLM extraction, before serialisation.

Why this layer exists:
  The LLM prompt and schema architecture (chain-of-thought scaffolding, preferred-first
  field ordering) solve the classification problem at scale. However, a small model has
  a ceiling on rule application consistency: the responsibility exclusion rule in
  skills_preferred — "exclude any skill that also appears in responsibility_skills_found"
  — is correctly understood but not reliably applied on every posting.

  This function is the deterministic safety net. It guarantees that any skill the model
  found in a responsibility statement never remains in skills_preferred, regardless of
  whether the model applied the rule or not. The scaffolding fields make this possible:
  responsibility_skills_found gives us exact ground truth about what the model identified
  as responsibility-embedded — we use its own output to enforce the rule it missed.

  Additional fixes applied here as they are identified from full-batch analysis.
  See docs/technical_report.md §9.14 for the full post-processing layer design.
"""

from src.data_ingestion.models import Job


def postprocess(job: Job) -> Job:
    """
    Deterministic cleanup of known model-level inconsistencies.

    Applied immediately after parse_posting_async() returns, before serialisation.
    Returns the same Job object with corrections applied in-place.
    """
    # Responsibility exclusion: any skill the model found in a responsibility statement
    # must not appear in skills_preferred — move it back to skills_required.
    if job.responsibility_skills_found and job.skills_preferred:
        overlap = set(job.skills_preferred) & set(job.responsibility_skills_found)
        if overlap:
            job.skills_preferred = [s for s in job.skills_preferred if s not in overlap]
            job.skills_required = (job.skills_required or []) + sorted(overlap)

    return job
