"""
Eval trend tracker: reads all eval_results/*/report.json files, writes
eval_results/evals/trend.csv, and generates trajectory plots saved to
eval_results/evals/.

Refresh after any new eval run:
    python -m src.evals.eval_trend

In a notebook (returns Figure objects for inline display):
    from src.evals.eval_trend import build_trend, plot_trends
    from src.config import EVALS_RESULTS_DIR

    df = build_trend(EVALS_RESULTS_DIR)
    figs = plot_trends(df, notebook_mode=True)
    figs["overview"]      # renders inline
    figs["by_group"]
    figs["all_fields"]
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

# Output subfolder inside eval_results/
EVALS_SUBDIR = "evals"

# All dimensions in a stable display order (superset across all versions)
DIMENSIONS = [
    # Company
    "company_name_accuracy",
    "company_description_accuracy",
    "industry_accuracy",
    "location_accuracy",           # v1/v2 only — null in later runs
    "remote_policy_accuracy",
    "employment_type_accuracy",
    # Role
    "seniority_accuracy",
    "job_family_accuracy",
    "years_experience_accuracy",
    "education_accuracy",
    "responsibilities_quality",
    # Skills
    "skills_technical_precision",
    "skills_technical_recall",
    "skills_soft_accuracy",
    "nice_to_have_accuracy",
    # Compensation
    "salary_accuracy",
    # Overall
    "null_appropriateness",
    "overall",
]

# Group membership for the per-group subplot
GROUPS = {
    "Company":      ["company_name_accuracy", "company_description_accuracy",
                     "industry_accuracy", "remote_policy_accuracy", "employment_type_accuracy"],
    "Role":         ["seniority_accuracy", "job_family_accuracy", "years_experience_accuracy",
                     "education_accuracy", "responsibilities_quality"],
    "Skills":       ["skills_technical_precision", "skills_technical_recall",
                     "skills_soft_accuracy", "nice_to_have_accuracy"],
    "Compensation": ["salary_accuracy"],
    "Overall":      ["null_appropriateness", "overall"],
}

# Short axis labels
_LABELS = {
    "company_name_accuracy":        "name",
    "company_description_accuracy": "description",
    "industry_accuracy":            "industry",
    "location_accuracy":            "location",
    "remote_policy_accuracy":       "remote_policy",
    "employment_type_accuracy":     "employment_type",
    "seniority_accuracy":           "seniority",
    "job_family_accuracy":          "job_family",
    "years_experience_accuracy":    "years_exp",
    "education_accuracy":           "education",
    "responsibilities_quality":     "responsibilities",
    "skills_technical_precision":   "tech_precision",
    "skills_technical_recall":      "tech_recall",
    "skills_soft_accuracy":         "soft",
    "nice_to_have_accuracy":        "nice_to_have",
    "salary_accuracy":              "salary",
    "null_appropriateness":         "null_handling",
    "overall":                      "overall",
}


# ── Data ──────────────────────────────────────────────────────────────────────

def build_trend(eval_root: Path) -> pd.DataFrame:
    """
    Scan eval_root for timestamped run directories, parse each report.json,
    and return a DataFrame with one row per run, columns for every dimension.
    Skips the evals/ subfolder itself.
    """
    records = []

    for run_dir in sorted(eval_root.iterdir()):
        if not run_dir.is_dir() or run_dir.name == EVALS_SUBDIR:
            continue
        report_path = run_dir / "report.json"
        if not report_path.exists():
            continue

        report = json.loads(report_path.read_text())

        # Directory format: YYYYMMDD_HHMMSS_<version>
        parts = run_dir.name.split("_", 2)
        timestamp = f"{parts[0]}_{parts[1]}" if len(parts) >= 2 else run_dir.name
        prompt_version = parts[2] if len(parts) >= 3 else "unknown"

        flat_scores: dict = {}
        for group_scores in report.get("groups", {}).values():
            flat_scores.update(group_scores)

        row = {
            "run_dir": run_dir.name,
            "timestamp": timestamp,
            "prompt_version": prompt_version,
            "n": report.get("n"),
            "pct_rows_with_score_1": report.get("pct_rows_with_score_1"),
            "n_flags": len(report.get("all_flags", [])),
        }
        for dim in DIMENSIONS:
            row[dim] = flat_scores.get(dim)

        records.append(row)

    return pd.DataFrame(records)


def save_trend(eval_root: Path) -> pd.DataFrame:
    """Build trend DataFrame, write trend.csv to eval_results/evals/, print summary table."""
    df = build_trend(eval_root)
    out_dir = eval_root / EVALS_SUBDIR
    out_dir.mkdir(exist_ok=True)
    out = out_dir / "trend.csv"
    df.to_csv(out, index=False, float_format="%.3f")
    print(f"trend.csv updated → {out}  ({len(df)} runs)")
    _print_table(df)
    return df


# ── Plots ─────────────────────────────────────────────────────────────────────

def plot_trends(
    df: pd.DataFrame,
    notebook_mode: bool = False,
    output_dir: Path | None = None,
) -> dict[str, plt.Figure]:
    """
    Generate trajectory plots from a trend DataFrame.

    Args:
        df:            Trend DataFrame from build_trend().
        notebook_mode: False (default) — save PNGs to output_dir and close figures.
                       True — skip saving, return open Figure objects for
                       inline rendering in a notebook.
        output_dir:    Where to save PNGs when notebook_mode=False.
                       Defaults to eval_results/evals/.

    Returns:
        Dict of named Figure objects:
            "overview"   — overall score + % score=1 + n_flags
            "by_group"   — one subplot per dimension group
            "all_fields" — heatmap of all dimensions × versions
    """
    versions = df["prompt_version"].tolist()
    x = range(len(versions))
    figs = {}

    # ── 1. Overview: overall score + % rows with score 1 + n_flags ───────────
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    fig.suptitle("Eval Trend — Overview", fontsize=13, fontweight="bold")

    _line(axes[0], x, df["overall"], versions, "Overall score", color="#2563eb")
    axes[0].set_ylim(1, 3)
    axes[0].axhline(3, color="gray", lw=0.6, ls="--")

    _line(axes[1], x, df["pct_rows_with_score_1"] * 100, versions,
          "% rows with score = 1", color="#dc2626")
    axes[1].yaxis.set_major_formatter(mticker.PercentFormatter())

    _line(axes[2], x, df["n_flags"], versions, "Total flags", color="#f59e0b")

    fig.tight_layout()
    figs["overview"] = fig

    # ── 2. By group: one subplot per group ───────────────────────────────────
    n_groups = len(GROUPS)
    fig, axes = plt.subplots(1, n_groups, figsize=(4 * n_groups, 4), sharey=True)
    fig.suptitle("Eval Trend — Score by Group", fontsize=13, fontweight="bold")

    colors = ["#2563eb", "#16a34a", "#dc2626", "#9333ea", "#f59e0b",
              "#0891b2", "#be185d"]

    for ax, (group_name, dims) in zip(axes, GROUPS.items()):
        for i, dim in enumerate(dims):
            if dim not in df.columns:
                continue
            vals = df[dim]
            if vals.isna().all():
                continue
            label = _LABELS.get(dim, dim)
            color = colors[i % len(colors)]
            ax.plot(list(x), vals.tolist(), marker="o", lw=1.8,
                    label=label, color=color)
            last_valid = vals.last_valid_index()
            if last_valid is not None:
                xi = df.index.get_loc(last_valid)
                ax.annotate(f"{vals[last_valid]:.2f}",
                            xy=(xi, vals[last_valid]),
                            xytext=(4, 0), textcoords="offset points",
                            fontsize=7, color=color)
        ax.set_title(group_name, fontsize=10, fontweight="bold")
        ax.set_xticks(list(x))
        ax.set_xticklabels(versions, rotation=45, ha="right", fontsize=8)
        ax.set_ylim(1, 3.1)
        ax.axhline(3, color="gray", lw=0.5, ls="--")
        ax.legend(fontsize=7, loc="lower right")
        ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    figs["by_group"] = fig

    # ── 3. Heatmap: all dimensions × versions ────────────────────────────────
    active_dims = [d for d in DIMENSIONS if d in df.columns and not df[d].isna().all()]
    heat_data = df.set_index("prompt_version")[active_dims].T
    heat_data.index = [_LABELS.get(d, d) for d in heat_data.index]

    fig, ax = plt.subplots(figsize=(max(6, len(versions) * 1.4), len(active_dims) * 0.45 + 1.5))
    fig.suptitle("Eval Trend — All Fields Heatmap", fontsize=13, fontweight="bold")

    im = ax.imshow(heat_data.values.astype(float), aspect="auto",
                   cmap="RdYlGn", vmin=1, vmax=3)

    ax.set_xticks(range(len(versions)))
    ax.set_xticklabels(versions, fontsize=9)
    ax.set_yticks(range(len(heat_data.index)))
    ax.set_yticklabels(heat_data.index, fontsize=8)

    for row_i, row_vals in enumerate(heat_data.values):
        for col_i, val in enumerate(row_vals):
            if pd.notna(val):
                ax.text(col_i, row_i, f"{val:.2f}", ha="center", va="center",
                        fontsize=7.5, color="black")

    plt.colorbar(im, ax=ax, label="Score (1–3)", shrink=0.6)
    fig.tight_layout()
    figs["all_fields"] = fig

    if not notebook_mode:
        if output_dir is None:
            try:
                from src.config import EVALS_RESULTS_DIR
                output_dir = EVALS_RESULTS_DIR / EVALS_SUBDIR
            except ImportError:
                output_dir = Path("eval_results") / EVALS_SUBDIR
        output_dir.mkdir(parents=True, exist_ok=True)

        for name, figure in figs.items():
            out = output_dir / f"trend_{name}.png"
            figure.savefig(out, dpi=150, bbox_inches="tight")
            print(f"  saved → {out}")
            plt.close(figure)

    return figs


# ── Helpers ───────────────────────────────────────────────────────────────────

def _line(ax, x, y, labels, title, color):
    ax.plot(list(x), y.tolist(), marker="o", lw=2, color=color)
    for xi, yi in zip(x, y):
        if pd.notna(yi):
            ax.annotate(f"{yi:.2f}", xy=(xi, yi), xytext=(0, 6),
                        textcoords="offset points", ha="center", fontsize=8)
    ax.set_title(title, fontsize=10)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.grid(axis="y", alpha=0.3)


def _print_table(df: pd.DataFrame) -> None:
    display_cols = ["prompt_version", "n", "pct_rows_with_score_1", "n_flags"] + DIMENSIONS
    display_cols = [c for c in display_cols if c in df.columns]
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    pd.set_option("display.float_format", "{:.2f}".format)
    print("\n" + df[display_cols].to_string(index=False))


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    from src.config import EVALS_RESULTS_DIR

    df = save_trend(EVALS_RESULTS_DIR)
    plot_trends(df, notebook_mode=False, output_dir=EVALS_RESULTS_DIR / EVALS_SUBDIR)
