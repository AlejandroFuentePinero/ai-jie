"""
LLM-as-a-Judge for structured job extraction quality.

Uses instructor (same as the parser) so Pydantic validation + automatic retries
are handled by the library — not fragile manual json.loads() + EvaluationScore(**raw).

Root cause of original failures: raw OpenAI() client + manual JSON parsing had
zero tolerance for type mismatches (e.g. "2" vs 2) or missing fields.
"""

import instructor
from openai import AsyncOpenAI, OpenAI

from src.data_ingestion.models import EvaluationScore, Job

JUDGE_MODEL = "gpt-5.4-mini"

JUDGE_PROMPT = """\
You are evaluating the output of an automated job posting extractor
against the original posting text.
 
## How to evaluate
 
Before scoring anything, you must first establish your own ground truth
by reading the posting and filling the scaffolding fields. Then compare
the extractor's output against your ground truth to assign scores.
 
## Scoring guide
 
  3 = correct and complete; no meaningful issues
  2 = mostly correct but a minor deviation or small omission
  1 = clearly wrong, hallucinated, or significant violation
 
When in doubt, score 2 not 1. Reserve 1 for clear, unambiguous errors.
 
## Evaluation rules
 
COMPANY
- company_name: canonical company name, not a division or team. Null
  only if genuinely not mentioned anywhere in the posting.
- company_description: always null. Score 3 if null, 1 if any value.
 
ROLE
- seniority: explicit title keyword first (Senior → senior, Lead → lead,
  Principal → principal, Manager → manager, Director → director,
  VP → director, AVP → senior in finance, Staff → senior, Associate →
  junior unless before Director/Principal/Partner). Then years of
  experience (0-1 → junior, 2-4 → mid, 5-7 → senior, 8+ → lead) with
  upward adjustment if responsibilities clearly exceed scope. Then
  unknown if still unclear. Score 1 only if the extracted value clearly
  contradicts explicit signals in the posting.
- job_family: title keyword first, responsibilities as tiebreaker.
  Score 2 if the assignment is defensible but another value is equally
  valid.
- years_experience: only if a number is explicitly stated. Open-ended
  ranges → min set, max null. Both null correct when no number appears.
- education_required: only required education, not preferred.
- key_responsibilities: up to 7 concrete verb-led actions explicitly
  stated. Penalise truncation if the posting lists more and the
  extractor captured fewer than 7.
 
SKILLS — use your scaffolding ground truth to score these:
- skills_required_accuracy: compare extractor's skills_required against
  your skills_i_consider_required. Penalise clear omissions of important
  skills and hallucinated items. Soft skills in required is always an
  error. Agile/Scrum are technical, not soft.
- skills_preferred_accuracy: compare extractor's skills_preferred against
  your skills_i_consider_preferred. Penalise required skills incorrectly
  placed here and significant omissions. Null is correct when no
  optionality language exists.
- skills_soft_accuracy: compare extractor's skills_soft against your
  skills_i_consider_soft. Score 1 only for clear content errors
  (Agile/Scrum placed here, or clearly emphasised soft skills returning
  null). Concise paraphrasing is correct behaviour.
 
Use misclassified_skills to inform your scoring — each misclassification
should reduce the score of the affected field.
 
OVERALL
- null_appropriateness: nulls used correctly across all fields.
- overall: holistic rule compliance across all field groups equally.
  Weight Company, Role, and Skills groups equally. Do not anchor on
  null_appropriateness.
- flags: specific rule violations as short strings. Empty list if none.
 
Return ONLY a valid JSON object matching the schema. No preamble, no
markdown fences.
"""

# Fields stripped from the extracted Job before sending to the judge.
# - Passthrough fields (title, location): no ground truth to evaluate against.
# - description: the original text — sending it back would be circular.
# - Scaffolding fields: judge must not anchor on the extractor's intermediate reasoning.
# Keep in sync with _SCAFFOLDING_COLS in hub.py and any new Job scaffolding fields.
_JUDGE_EXCLUDE = frozenset({
    "title",
    "description",
    "location",
    "sector",
    "responsibility_skills_found",
    "preferred_signals_found",
    "all_technical_skills",
})

# Lazy clients — API key read from environment at first call, not at import.
_async_judge: instructor.AsyncInstructor | None = None
_sync_judge: instructor.Instructor | None = None


def _get_async_judge() -> instructor.AsyncInstructor:
    global _async_judge
    if _async_judge is None:
        _async_judge = instructor.from_openai(AsyncOpenAI(max_retries=6))
    return _async_judge


def _get_sync_judge() -> instructor.Instructor:
    global _sync_judge
    if _sync_judge is None:
        _sync_judge = instructor.from_openai(OpenAI())
    return _sync_judge


def _build_user_message(job_title: str, description: str, extracted: Job) -> str:
    import json

    extracted_dict = {
        k: v for k, v in extracted.model_dump().items() if k not in _JUDGE_EXCLUDE
    }

    return (
        f"Original job title: {job_title}\n\n"
        f"Original description:\n{description}\n\n"
        f"Extracted data:\n{json.dumps(extracted_dict, indent=2, default=str)}"
    )


async def judge_extraction_async(
    job_title: str,
    description: str,
    extracted: Job,
) -> EvaluationScore:
    """
    Async judge — use inside run_eval() for concurrent scoring.

    instructor handles:
      - Pydantic validation of the response
      - Automatic retries with corrective feedback if the model returns
        wrong types or missing fields (max_retries=3)
    """
    return await _get_async_judge().chat.completions.create(
        model=JUDGE_MODEL,
        response_model=EvaluationScore,
        messages=[
            {"role": "system", "content": JUDGE_PROMPT},
            {
                "role": "user",
                "content": _build_user_message(job_title, description, extracted),
            },
        ],
        max_retries=3,
        temperature=0,
    )


def judge_extraction(
    job_title: str,
    description: str,
    extracted: Job,
) -> EvaluationScore:
    """Sync wrapper — for notebook exploration only."""
    return _get_sync_judge().chat.completions.create(
        model=JUDGE_MODEL,
        response_model=EvaluationScore,
        messages=[
            {"role": "system", "content": JUDGE_PROMPT},
            {
                "role": "user",
                "content": _build_user_message(job_title, description, extracted),
            },
        ],
        max_retries=3,
        temperature=0,
    )
