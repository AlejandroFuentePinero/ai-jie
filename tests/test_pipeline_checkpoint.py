"""
Checkpoint/resume tests for src/data_ingestion/pipeline.run_pipeline().

Verifies that if the pipeline is interrupted partway through a batch,
restarting it:
  - skips already-extracted records (no duplicate _row_ids in output)
  - processes only the missing records (extractor called exactly for those)
  - does not lose the pre-existing checkpoint data

No LLM calls are made — parse_posting_async is mocked to return a fixed Job.
"""

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pandas as pd

from src.data_ingestion.models import Job
from src.data_ingestion.pipeline import run_pipeline


# ── Fixtures ──────────────────────────────────────────────────────────────────

_DUMMY_JOB = Job(
    title="Data Scientist",
    description="A test job description long enough to pass the length filter.",
    location="Remote",
    responsibility_skills_found=["Python"],
    preferred_signals_found=None,
    all_technical_skills=["Python"],
    skills_required=["Python"],
    skills_preferred=None,
    skills_soft=None,
)


def _make_df(row_ids: list[int]) -> pd.DataFrame:
    """Build a minimal DataFrame whose index matches the given row IDs."""
    df = pd.DataFrame(
        [
            {
                "title": f"Job {i}",
                "description": "A test job description long enough to pass the length filter.",
                "location": "Remote",
                "sector": None,
            }
            for i in row_ids
        ],
        index=row_ids,
    )
    return df


def _write_checkpoint(path: Path, row_ids: list[int]) -> None:
    """Write a partial JSONL checkpoint containing the given row IDs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for rid in row_ids:
            record = {
                "_row_id": rid,
                "prompt_version": "vTEST",
                **_DUMMY_JOB.model_dump(),
            }
            f.write(json.dumps(record, default=str) + "\n")


def _read_checkpoint(path: Path) -> list[int]:
    """Return the list of _row_ids present in the JSONL file."""
    ids = []
    with open(path) as f:
        for line in f:
            record = json.loads(line)
            ids.append(record["_row_id"])
    return ids


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_resume_skips_already_processed(tmp_path):
    """
    Given a checkpoint with rows 0-2, running against rows 0-4 must call
    the extractor only for rows 3 and 4.
    """
    output_path = tmp_path / "jobs.jsonl"
    _write_checkpoint(output_path, row_ids=[0, 1, 2])

    df = _make_df(row_ids=[0, 1, 2, 3, 4])
    mock_extractor = AsyncMock(return_value=_DUMMY_JOB)

    with patch("src.data_ingestion.pipeline.parse_posting_async", mock_extractor):
        asyncio.run(run_pipeline(df, output_path=output_path, concurrency=2))

    # Extractor should have been called exactly twice (rows 3 and 4).
    assert mock_extractor.call_count == 2


def test_resume_produces_no_duplicate_row_ids(tmp_path):
    """
    After a resume run, the output file must contain each _row_id exactly once.
    """
    output_path = tmp_path / "jobs.jsonl"
    _write_checkpoint(output_path, row_ids=[0, 1, 2])

    df = _make_df(row_ids=[0, 1, 2, 3, 4])
    mock_extractor = AsyncMock(return_value=_DUMMY_JOB)

    with patch("src.data_ingestion.pipeline.parse_posting_async", mock_extractor):
        asyncio.run(run_pipeline(df, output_path=output_path, concurrency=2))

    ids = _read_checkpoint(output_path)
    assert len(ids) == len(set(ids)), f"Duplicate _row_ids found: {ids}"


def test_resume_contains_all_row_ids(tmp_path):
    """
    After a resume run, the output must contain every row from the full DataFrame.
    """
    output_path = tmp_path / "jobs.jsonl"
    _write_checkpoint(output_path, row_ids=[0, 1, 2])

    df = _make_df(row_ids=[0, 1, 2, 3, 4])
    mock_extractor = AsyncMock(return_value=_DUMMY_JOB)

    with patch("src.data_ingestion.pipeline.parse_posting_async", mock_extractor):
        result_df = asyncio.run(run_pipeline(df, output_path=output_path, concurrency=2))

    assert set(result_df["_row_id"]) == {0, 1, 2, 3, 4}


def test_checkpoint_already_complete_skips_extractor(tmp_path):
    """
    When the checkpoint already covers all rows, the extractor is never called.
    """
    output_path = tmp_path / "jobs.jsonl"
    _write_checkpoint(output_path, row_ids=[0, 1, 2])

    df = _make_df(row_ids=[0, 1, 2])
    mock_extractor = AsyncMock(return_value=_DUMMY_JOB)

    with patch("src.data_ingestion.pipeline.parse_posting_async", mock_extractor):
        asyncio.run(run_pipeline(df, output_path=output_path, concurrency=2))

    mock_extractor.assert_not_called()


def test_no_checkpoint_processes_all_rows(tmp_path):
    """
    With no pre-existing checkpoint, every row in the DataFrame is extracted.
    """
    output_path = tmp_path / "jobs.jsonl"
    df = _make_df(row_ids=[0, 1, 2])
    mock_extractor = AsyncMock(return_value=_DUMMY_JOB)

    with patch("src.data_ingestion.pipeline.parse_posting_async", mock_extractor):
        asyncio.run(run_pipeline(df, output_path=output_path, concurrency=2))

    assert mock_extractor.call_count == 3


def test_corrupt_checkpoint_line_is_skipped(tmp_path):
    """
    A malformed JSON line in the checkpoint must not crash the pipeline;
    that record is treated as unprocessed and re-extracted.
    """
    output_path = tmp_path / "jobs.jsonl"

    # Write one valid line and one corrupt line.
    with open(output_path, "w") as f:
        f.write(json.dumps({"_row_id": 0, **_DUMMY_JOB.model_dump()}, default=str) + "\n")
        f.write("{{not valid json}}\n")

    df = _make_df(row_ids=[0, 1])
    mock_extractor = AsyncMock(return_value=_DUMMY_JOB)

    with patch("src.data_ingestion.pipeline.parse_posting_async", mock_extractor):
        asyncio.run(run_pipeline(df, output_path=output_path, concurrency=2))

    # Row 0 was valid in checkpoint → skipped. Row 1 was not → extracted.
    assert mock_extractor.call_count == 1
