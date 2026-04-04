"""
Unit tests for src/data_ingestion/postprocess.py.

Covers the two deterministic rules applied to every extracted Job:
  1. apply_responsibility_exclusion — skills found in responsibility statements
     must not remain in skills_preferred; they are moved to skills_required.
  2. _remove_blocked — blocklisted tokens (role names, broad field labels,
     generic nouns) are removed from skills_required and skills_preferred.

Also verifies that postprocess() (per-record, eval path) and postprocess_df()
(DataFrame, pipeline path) apply identical rules to the same input.

Note: token normalisation tests will be added here once that step is designed.
"""

import pandas as pd
import pytest

from src.data_ingestion.models import Job
from src.data_ingestion.postprocess import (
    _remove_blocked,
    apply_responsibility_exclusion,
    postprocess,
    postprocess_df,
)


# ── apply_responsibility_exclusion ────────────────────────────────────────────

def test_exclusion_no_overlap():
    new_pref, new_req = apply_responsibility_exclusion(
        skills_preferred=["Spark", "Kafka"],
        responsibility_skills_found=["Python", "SQL"],
        skills_required=["Python", "SQL"],
    )
    assert new_pref == ["Spark", "Kafka"]
    assert new_req == ["Python", "SQL"]


def test_exclusion_full_overlap():
    new_pref, new_req = apply_responsibility_exclusion(
        skills_preferred=["Python", "SQL"],
        responsibility_skills_found=["Python", "SQL"],
        skills_required=[],
    )
    assert new_pref == []
    assert set(new_req) == {"Python", "SQL"}


def test_exclusion_partial_overlap():
    new_pref, new_req = apply_responsibility_exclusion(
        skills_preferred=["Python", "Spark", "Kafka"],
        responsibility_skills_found=["Python"],
        skills_required=["SQL"],
    )
    assert new_pref == ["Spark", "Kafka"]
    assert "Python" in new_req
    assert "SQL" in new_req


def test_exclusion_none_preferred():
    new_pref, new_req = apply_responsibility_exclusion(
        skills_preferred=None,
        responsibility_skills_found=["Python"],
        skills_required=["SQL"],
    )
    assert new_pref is None
    assert new_req == ["SQL"]


def test_exclusion_none_responsibility():
    new_pref, new_req = apply_responsibility_exclusion(
        skills_preferred=["Spark"],
        responsibility_skills_found=None,
        skills_required=["SQL"],
    )
    assert new_pref == ["Spark"]
    assert new_req == ["SQL"]


def test_exclusion_required_starts_none():
    new_pref, new_req = apply_responsibility_exclusion(
        skills_preferred=["Python"],
        responsibility_skills_found=["Python"],
        skills_required=None,
    )
    assert new_pref == []
    assert "Python" in new_req


def test_exclusion_empty_lists():
    new_pref, new_req = apply_responsibility_exclusion(
        skills_preferred=[],
        responsibility_skills_found=[],
        skills_required=[],
    )
    assert new_pref == []
    assert new_req == []


# ── _remove_blocked ───────────────────────────────────────────────────────────

def test_remove_blocked_none_input():
    assert _remove_blocked(None) == []


def test_remove_blocked_empty_list():
    assert _remove_blocked([]) == []


def test_remove_blocked_no_matches():
    tokens = ["PyTorch", "dbt", "Airflow"]
    assert _remove_blocked(tokens) == tokens


def test_remove_blocked_all_match():
    assert _remove_blocked(["analytics", "communication", "leadership"]) == []


def test_remove_blocked_case_insensitive():
    assert _remove_blocked(["Analytics"]) == []
    assert _remove_blocked(["ANALYTICS"]) == []


def test_remove_blocked_mixed():
    result = _remove_blocked(["PyTorch", "analytics", "dbt", "communication"])
    assert result == ["PyTorch", "dbt"]


def test_remove_blocked_preserves_order():
    tokens = ["Airflow", "dbt", "Spark", "Kafka"]
    assert _remove_blocked(tokens) == tokens


# ── postprocess() vs postprocess_df() consistency ────────────────────────────

def _make_job(skills_preferred, responsibility_skills_found, skills_required):
    return Job(
        title="Data Scientist",
        description="Test description for unit test purposes.",
        location="New York, NY",
        responsibility_skills_found=responsibility_skills_found,
        preferred_signals_found=None,
        all_technical_skills=None,
        skills_preferred=skills_preferred,
        skills_required=skills_required,
        skills_soft=[],
    )


def test_consistency_exclusion_rule():
    """Responsibility exclusion applied identically by both entry points."""
    job = _make_job(
        skills_preferred=["Python", "Spark"],
        responsibility_skills_found=["Python"],
        skills_required=["SQL"],
    )
    processed_job = postprocess(job)

    df = pd.DataFrame([{
        "responsibility_skills_found": ["Python"],
        "skills_preferred": ["Python", "Spark"],
        "skills_required": ["SQL"],
    }])
    processed_row = postprocess_df(df).iloc[0]

    assert set(processed_job.skills_preferred) == set(processed_row["skills_preferred"])
    assert set(processed_job.skills_required) == set(processed_row["skills_required"])


def test_consistency_blocklist_rule():
    """Blocklist removal applied identically by both entry points."""
    job = _make_job(
        skills_preferred=["Spark", "analytics"],
        responsibility_skills_found=[],
        skills_required=["Python", "communication"],
    )
    processed_job = postprocess(job)

    df = pd.DataFrame([{
        "responsibility_skills_found": [],
        "skills_preferred": ["Spark", "analytics"],
        "skills_required": ["Python", "communication"],
    }])
    processed_row = postprocess_df(df).iloc[0]

    assert set(processed_job.skills_preferred) == set(processed_row["skills_preferred"])
    assert set(processed_job.skills_required) == set(processed_row["skills_required"])
