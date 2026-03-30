"""
Reporting utilities: score group definitions, summary printing, and report persistence.
Moved from the notebook so they can be reused across runs and scripts.
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    pass

SCORE_GROUPS: dict[str, list[str]] = {
    "Company": [
        "company_name_accuracy",
        "company_description_accuracy",
        "industry_accuracy",
        "remote_policy_accuracy",
        "employment_type_accuracy",
    ],
    "Role": [
        "seniority_accuracy",
        "job_family_accuracy",
        "years_experience_accuracy",
        "education_accuracy",
        "responsibilities_quality",
    ],
    "Skills": [
        "skills_technical_precision",
        "skills_technical_recall",
        "skills_soft_accuracy",
        "nice_to_have_accuracy",
    ],
    "Compensation": [
        "salary_accuracy",
    ],
    "Overall": [
        "null_appropriateness",
        "overall",
    ],
}

ALL_SCORE_COLS: list[str] = [col for cols in SCORE_GROUPS.values() for col in cols]


def print_summary(scores_df: pd.DataFrame, n_failures: int = 0) -> None:
    """Print a formatted evaluation summary to stdout."""
    if scores_df.empty:
        print(f"\n⚠  No scores to summarise (failures={n_failures})")
        return

    print(f"\n{'='*60}")
    print(f"  EVALUATION SUMMARY  (n={len(scores_df)}, failures={n_failures})")
    print(f"{'='*60}")

    for group, cols in SCORE_GROUPS.items():
        present = [c for c in cols if c in scores_df.columns]
        if not present:
            continue
        print(f"\n  {group}")
        print(f"  {'-'*40}")
        for col in present:
            mean = scores_df[col].mean()
            bar = "█" * int(mean * 10)
            pct_ones = (scores_df[col] == 1).mean()
            warning = " ⚠" if pct_ones > 0.2 else ""
            print(f"  {col:<35} {mean:.2f}  {bar}{warning}")

    print(f"\n{'='*60}")
    print("  SCORE DISTRIBUTIONS")
    print(f"{'='*60}")
    try:
        from IPython.display import display
        display(scores_df[ALL_SCORE_COLS].describe().round(2))
    except ImportError:
        print(scores_df[ALL_SCORE_COLS].describe().round(2).to_string())

    # Rows that scored 1 on anything — surface for review
    weak_mask = (scores_df[[c for c in ALL_SCORE_COLS if c in scores_df.columns]] == 1).any(axis=1)
    weak_rows = scores_df[weak_mask]
    if not weak_rows.empty:
        print(f"\n⚠  {len(weak_rows)} rows scored 1 on at least one dimension")

    # All flags
    all_flags = [
        flag
        for flags in scores_df.get("flags", [])
        for flag in (flags if isinstance(flags, list) else [])
    ]
    if all_flags:
        print(f"\n  ALL FLAGS ({len(all_flags)} total):")
        for flag in all_flags:
            print(f"    • {flag}")



def build_report(scores_df: pd.DataFrame) -> dict:
    """Return a JSON-serialisable summary dict, suitable for saving to report.json."""
    if scores_df.empty:
        return {"n": 0, "groups": {}, "all_flags": []}

    present = [c for c in ALL_SCORE_COLS if c in scores_df.columns]
    group_means = {}
    for group, cols in SCORE_GROUPS.items():
        group_cols = [c for c in cols if c in present]
        if group_cols:
            group_means[group] = {
                col: round(float(scores_df[col].mean()), 3) for col in group_cols
            }

    all_flags = [
        flag
        for flags in scores_df.get("flags", [])
        for flag in (flags if isinstance(flags, list) else [])
    ]

    pct_weak = float(
        (scores_df[present] == 1).any(axis=1).mean()
    ) if present else 0.0

    return {
        "n": len(scores_df),
        "pct_rows_with_score_1": round(pct_weak, 3),
        "groups": group_means,
        "all_flags": all_flags,
    }


def save_report(report: dict, output_dir: Path) -> None:
    """Write report.json to the run output directory."""
    path = output_dir / "report.json"
    path.write_text(json.dumps(report, indent=2))
    print(f"  report.json → {path}")
