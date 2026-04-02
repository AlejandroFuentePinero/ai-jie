"""
Human evaluation module — review extractions side by side with the original text
and produce human scores using the same EvaluationScore schema as the judge.

This enables two comparisons:
  1. Extraction quality: human scores as an independent quality signal
  2. Judge calibration: where human and judge scores diverge, that is signal
     about judge bias or miscalibration (dimension-level and row-level)

Output: human_scores.jsonl saved in the same run directory as scores.jsonl,
keyed on _row_id so the two files can be joined directly.

Usage (notebook):
    from src.evals.human_eval import load_run

    session = load_run("v9g")
    session.status()

    ROW_ID = session.next_unscored()
    session.show_description(ROW_ID)
    session.show_extraction(ROW_ID)

    session.score(
        ROW_ID,
        company_name_accuracy=3,
        ...
        overall=2,
        flags=["seniority_wrong"],
    )

    session.compare()
"""

import json
import re
from pathlib import Path

import pandas as pd

from src.config import EVALS_RESULTS_DIR
from src.data_ingestion.models import EvaluationScore
from src.evals.report import ALL_SCORE_COLS


class HumanEvalSession:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self._sample: dict[int, dict] = self._load_jsonl("sample.jsonl")
        self._extractions: dict[int, dict] = self._load_jsonl("extractions.jsonl")
        self._judge_scores: dict[int, dict] = self._load_jsonl("scores.jsonl")
        self._human_scores: dict[int, dict] = self._load_jsonl("human_scores.jsonl")

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _load_jsonl(self, filename: str) -> dict[int, dict]:
        path = self.run_dir / filename
        if not path.exists():
            return {}
        result: dict[int, dict] = {}
        with open(path) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    result[int(rec["_row_id"])] = rec
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
        return result

    def _append_human_score(self, record: dict) -> None:
        path = self.run_dir / "human_scores.jsonl"
        with open(path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def _rewrite_human_scores(self) -> None:
        path = self.run_dir / "human_scores.jsonl"
        with open(path, "w") as f:
            for rec in self._human_scores.values():
                f.write(json.dumps(rec) + "\n")

    # ── Navigation ────────────────────────────────────────────────────────────

    @property
    def row_ids(self) -> list[int]:
        return sorted(self._extractions.keys())

    @property
    def scored_ids(self) -> list[int]:
        return sorted(self._human_scores.keys())

    def next_unscored(self) -> int | None:
        """Return the lowest row_id not yet human-scored, or None if all done."""
        for row_id in self.row_ids:
            if row_id not in self._human_scores:
                return row_id
        return None

    # ── Display ───────────────────────────────────────────────────────────────

    def show_description(self, row_id: int) -> None:
        """Display the original job title, location, and description."""
        row = self._sample.get(row_id)
        if row is None:
            print(f"row_id {row_id} not found in sample.jsonl")
            return

        title = row.get("title", "(no title)")
        location = row.get("location", "—")
        description = row.get("description", "(no description)")

        try:
            from IPython.display import Markdown, display
            display(Markdown(
                f"## [{row_id}] {title}\n\n"
                f"**Location:** {location}\n\n"
                f"---\n\n"
                f"{description}"
            ))
        except ImportError:
            print(f"[{row_id}] {title} | {location}")
            print("-" * 60)
            print(description)

    def show_extraction(self, row_id: int) -> None:
        """Display extracted fields grouped by Company / Role / Skills / Compensation."""
        ext = self._extractions.get(row_id)
        if ext is None:
            print(f"row_id {row_id} not found in extractions.jsonl")
            return

        skip = {"_row_id", "title", "description", "location", "prompt_version",
                "preferred_signals_found", "responsibility_skills_found"}
        fields = {k: v for k, v in ext.items() if k not in skip}

        groups = {
            "Company": ["company_name", "company_description"],
            "Role": ["seniority", "job_family", "years_experience_min", "years_experience_max",
                     "education_required", "key_responsibilities"],
            "Skills": ["skills_required", "skills_preferred", "skills_soft"],
        }

        # Chain-of-thought scaffolding — shown separately for human eval debugging
        responsibility_skills = ext.get("responsibility_skills_found")
        preferred_signals = ext.get("preferred_signals_found")

        try:
            from IPython.display import Markdown, display
            lines = [f"## Extraction — [{row_id}]\n"]
            for group, keys in groups.items():
                lines.append(f"### {group}")
                for k in keys:
                    v = fields.get(k)
                    if isinstance(v, list):
                        formatted = ", ".join(str(x) for x in v) if v else "—"
                    else:
                        formatted = str(v) if v is not None else "—"
                    lines.append(f"- **{k}**: {formatted}")
                lines.append("")
            # Scaffolding fields — show what the model identified before classifying skills;
            # responsibility_skills_found verifies responsibility scanning;
            # preferred_signals_found verifies optionality zone detection
            lines.append("### Scaffolding: responsibility_skills_found")
            if responsibility_skills:
                lines.append(", ".join(str(s) for s in responsibility_skills))
            else:
                lines.append("— (null — no responsibility-embedded skills found)")
            lines.append("")
            lines.append("### Scaffolding: preferred_signals_found")
            if preferred_signals:
                for s in preferred_signals:
                    lines.append(f"- {s}")
            else:
                lines.append("— (null — no optionality language found)")
            display(Markdown("\n".join(lines)))
        except ImportError:
            for group, keys in groups.items():
                print(f"\n{group}")
                for k in keys:
                    print(f"  {k}: {fields.get(k)}")
            print("\nScaffolding: responsibility_skills_found")
            print(f"  {', '.join(str(s) for s in responsibility_skills)}" if responsibility_skills else "  — (null)")
            print("\nScaffolding: preferred_signals_found")
            if preferred_signals:
                for s in preferred_signals:
                    print(f"  - {s}")
            else:
                print("  — (null)")

    # ── Scoring ───────────────────────────────────────────────────────────────

    def score(
        self,
        row_id: int,
        *,
        company_name_accuracy: int,
        company_description_accuracy: int,
        seniority_accuracy: int,
        job_family_accuracy: int,
        years_experience_accuracy: int,
        education_accuracy: int,
        responsibilities_quality: int,
        skills_required_accuracy: int,
        skills_preferred_accuracy: int,
        skills_soft_accuracy: int,
        null_appropriateness: int,
        overall: int,
        flags: list[str] | None = None,
    ) -> None:
        """
        Validate and save a human score for the given row_id.

        All integer scores must be 1, 2, or 3:
          3 = correct and complete per the extraction rules
          2 = mostly correct, minor deviation or small omission
          1 = clearly wrong, hallucinated, or significant rule violation

        flags: short strings describing specific issues, e.g.
          ["seniority_wrong", "skills_required_incomplete"]
        """
        if row_id not in self._extractions:
            print(f"⚠  row_id {row_id} not in extractions — check your row_id.")
            return

        if row_id in self._human_scores:
            print(f"⚠  row_id {row_id} already scored. Overwriting.")
            del self._human_scores[row_id]
            self._rewrite_human_scores()

        score_obj = EvaluationScore(
            company_name_accuracy=company_name_accuracy,
            company_description_accuracy=company_description_accuracy,
            seniority_accuracy=seniority_accuracy,
            job_family_accuracy=job_family_accuracy,
            years_experience_accuracy=years_experience_accuracy,
            education_accuracy=education_accuracy,
            responsibilities_quality=responsibilities_quality,
            skills_required_accuracy=skills_required_accuracy,
            skills_preferred_accuracy=skills_preferred_accuracy,
            skills_soft_accuracy=skills_soft_accuracy,
            null_appropriateness=null_appropriateness,
            overall=overall,
            flags=flags or [],
        )

        record = {"_row_id": row_id, **score_obj.model_dump()}
        self._human_scores[row_id] = record
        self._append_human_score(record)
        print(f"✓  row_id={row_id} saved  (overall={overall}, flags={flags or []})")

    # ── Status ────────────────────────────────────────────────────────────────

    def status(self) -> None:
        """Print scoring progress."""
        n_total = len(self.row_ids)
        n_scored = len(self.scored_ids)
        bar = "█" * n_scored + "░" * (n_total - n_scored)
        print(f"Progress: {n_scored}/{n_total}  [{bar}]")
        nxt = self.next_unscored()
        if nxt is not None:
            print(f"Next unscored: row_id={nxt}")
        else:
            print("All rows scored — run session.compare() to see results.")

    # ── Comparison ────────────────────────────────────────────────────────────

    def compare(self) -> pd.DataFrame:
        """
        Compare human scores against judge scores for all jointly scored rows.

        Returns a DataFrame of per-row deltas (human − judge) per dimension.
        Positive delta = human scored higher than judge.
        Negative delta = judge scored higher than human.
        """
        if not self._human_scores:
            print("No human scores yet — score some rows first.")
            return pd.DataFrame()

        judge_df = (
            pd.DataFrame(list(self._judge_scores.values()))
            .set_index("_row_id")
        )
        human_df = (
            pd.DataFrame(list(self._human_scores.values()))
            .set_index("_row_id")
        )

        common_ids = judge_df.index.intersection(human_df.index)
        if common_ids.empty:
            print("No overlapping row_ids between judge and human scores.")
            return pd.DataFrame()

        score_cols = [c for c in ALL_SCORE_COLS if c in judge_df.columns and c in human_df.columns]
        judge_sub = judge_df.loc[common_ids, score_cols]
        human_sub = human_df.loc[common_ids, score_cols]
        delta = human_sub - judge_sub

        print(f"\nHuman vs Judge — {len(common_ids)} rows\n{'='*60}")
        print("\nMean delta (human − judge) per dimension:  [+ = human higher, − = judge higher]")

        mean_delta = delta.mean()
        for dim, val in mean_delta.items():
            marker = "▲" if val > 0.05 else ("▼" if val < -0.05 else "—")
            print(f"  {dim:<38} {val:+.3f}  {marker}")

        print(f"\nMean absolute disagreement:  {delta.abs().mean().mean():.3f}")

        print(f"\nRows with largest total disagreement (|Δ| summed across all dimensions):")
        total_abs = delta.abs().sum(axis=1).sort_values(ascending=False)
        for row_id, val in total_abs.head(5).items():
            judge_overall = judge_df.loc[row_id, "overall"] if row_id in judge_df.index else "—"
            human_overall = human_df.loc[row_id, "overall"] if row_id in human_df.index else "—"
            title = self._sample.get(row_id, {}).get("title", "")
            print(f"  row_id={row_id}  |Δ|={val:.1f}  judge_overall={judge_overall}  human_overall={human_overall}  ({title[:50]})")

        delta.index.name = "_row_id"
        return delta


# ── Entry point ───────────────────────────────────────────────────────────────

def load_run(
    version: str = "v9g",
    results_root: Path = EVALS_RESULTS_DIR,
) -> HumanEvalSession:
    """
    Find the latest eval run matching the given version and return a HumanEvalSession.

    Args:
        version:      Prompt version label, e.g. "v9g". Matched as exact suffix.
        results_root: Root directory containing timestamped run folders.

    Raises:
        FileNotFoundError: if no run directory matches the version.
    """
    results_root = Path(results_root)
    pattern = re.compile(rf"^\d{{8}}_\d{{6}}_{re.escape(version)}$")
    matches = sorted(
        [d for d in results_root.iterdir() if d.is_dir() and pattern.match(d.name)]
    )
    if not matches:
        raise FileNotFoundError(
            f"No eval run found for version '{version}' in {results_root}"
        )

    run_dir = matches[-1]  # latest timestamp wins if multiple exist
    print(f"Loaded: {run_dir.name}")
    return HumanEvalSession(run_dir)
