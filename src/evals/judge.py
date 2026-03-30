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

JUDGE_MODEL = "gpt-4o"

JUDGE_PROMPT = """\
You are evaluating the output of an automated job posting extractor against the original text.
Your job is to assess whether the extractor correctly followed the rules it was given — not whether
the output matches your own opinion of what is correct.

The extractor was given these exact rules. Evaluate compliance with them:

── EXTRACTION RULES THE EXTRACTOR FOLLOWED ──────────────────────────────────────

COMPANY
- company_description: first descriptive sentence about the company; null if absent. Not constructed.
- industry: the company's BUSINESS SECTOR — what it sells or does — not the technology the role uses.
  A bank hiring a data scientist → "Financial Services". A pharma company → "Pharmaceutical" or the
  specific sub-domain stated. When the company's sector is ambiguous, the more specific answer is preferred.
- remote_policy: remote/hybrid/on-site as stated; null if not mentioned.
- employment_type: full-time/part-time/contract/casual as stated; null if not mentioned.

ROLE
- seniority: determined in strict priority order:
    1. Explicit title keyword (senior/junior/lead/principal/director) → use directly, no override.
    2. No title keyword → years of experience: 0-1 → junior, 2-4 → mid, 5-7 → senior, 8+ → lead.
       Use midpoint of a range (e.g. "3-5 years" → mid).
    3. No title keyword and no years → responsibilities tone.
    4. Still unclear → "unknown". This is correct behaviour, not an error.
- job_family: determined by strict priority:
    1. Clear title keyword → use it directly ("Data Engineer" → data_engineering, "ML Engineer" → ml_engineering,
       "Analytics Engineer" → data_analytics, "Data Analyst" → data_analytics, "Research Scientist" → research, "Engineering Manager" → management).
       Do not override a clear title keyword based on responsibilities.
    2. Ambiguous or generic title (e.g. "Data Scientist", "Engineer") → primary responsibilities decide.
    3. Still unclear → other.
  Valid values: data_science (modelling, stats, experimentation), data_engineering (pipelines, ETL, infrastructure),
    ml_engineering (deploying/serving models, MLOps), ai_engineering (LLMs, generative AI),
    software_engineering (general dev, APIs), data_analytics (BI, dashboards, reporting, SQL-heavy insight),
    research (academic/scientific R&D), management (people management, programme management),
    other (nothing else fits). Score 2 if the assignment is defensible but another value is equally valid.
- years_experience: only if a number is explicitly stated; never inferred from seniority.
- key_responsibilities: 3-5 concrete verb-led actions; generic filler excluded.
- education_required: only if explicitly required, not preferred.

SKILLS
- skills_technical: ALL named tools AND skill categories from the entire document are expected —
  specific products (Python, Spark, Tableau), common tools (Excel, Git, SQL), platform categories
  (cloud computing, BI tools, data warehousing), and methodology terms (machine learning, NLP,
  A/B testing). Includes skills from both required AND preferred sections — this list is exhaustive.
  Only pure marketing filler is excluded ("modern stack", "cutting-edge tools").
  Process/project methodology terms (Agile, Scrum, Kanban) belong here, not in skills_soft.
- skills_soft: included when the employer genuinely emphasises a soft skill for this role. Obvious generic
  boilerplate with zero specificity ("team player", "fast learner" with no context) may be null — correct.
  If the employer devoted a sentence or bullet to it, inclusion is expected. Err on the side of including.
  Should be concise phrases (2–7 words), not full verbatim sentences — condensed labels are correct.
  Process/methodology terms (Agile, Scrum) in skills_soft is an error; they belong in skills_technical.
- nice_to_have: only from text using explicit words: "preferred", "nice to have", "a plus", "bonus",
  "ideally", "would be an asset", "desirable". Skills in a requirements section are required, not
  nice-to-have. Should be concise skill names, not full sentences.
  IMPORTANT: a preferred-only skill appearing in BOTH skills_technical and nice_to_have is CORRECT
  — skills_technical is exhaustive, nice_to_have flags the skill as optional. Do NOT penalise this.
  A violation is: a clearly required skill in nice_to_have, OR nice_to_have skills with no explicit
  preferred/bonus language in the source.

COMPENSATION
- salary: only if explicitly stated as a number or range; never inferred.

─────────────────────────────────────────────────────────────────────────────────

SCORING GUIDE (apply to every dimension):
  3 = correct and complete per the rules above; no meaningful issues
  2 = mostly correct but a minor deviation from the rules, or a small omission
  1 = clearly wrong, hallucinated, or a significant violation of the rules

IMPORTANT — when in doubt, score 2 not 1:
  If you cannot determine from the description alone whether the extracted value is correct
  (e.g. industry classification where the sector is genuinely ambiguous, seniority where signals
  conflict, skills where completeness is hard to verify in a long description), score 2.
  Reserve 1 for clear, unambiguous errors.

DIMENSIONS:

COMPANY
- company_name_accuracy        correctly extracted or null if not stated
- company_description_accuracy one sentence from the text, not constructed or invented
- industry_accuracy            correct business sector per the industry rule above
- remote_policy_accuracy       remote/hybrid/on-site correctly identified or null
- employment_type_accuracy     full-time/contract/casual correctly identified or null

ROLE
- seniority_accuracy           follows the priority order above; "unknown" is correct when genuinely unclear
- job_family_accuracy          title-first: clear title keyword overrides responsibilities; ambiguous title → responsibilities
- years_experience_accuracy    only extracted if explicitly stated as a number
- education_accuracy           only required education; preferred/nice-to-have education excluded
- responsibilities_quality     concrete verb-led actions, no generic filler

SKILLS
- skills_technical_precision   includes named tools, categories, and methodology terms from the full
                               document; Agile/Scrum are technical not soft; preferred-section skills
                               ARE expected here — skills_technical is exhaustive
- skills_technical_recall      Score this INDEPENDENTLY of precision. Before scoring: mentally enumerate
                               every technical skill present in the description, then check what the
                               extractor missed. Base your score only on omissions — do not conflate
                               with whether extracted items are correct (that is precision).
- skills_soft_accuracy         soft skills the employer emphasises, as concise phrases; Agile/Scrum in
                               skills_soft is an error; only pure generic boilerplate with no context may be null
- nice_to_have_accuracy        only skills from explicitly preferred/bonus sections; as concise names not
                               sentences; preferred-only skills in both fields is correct — do NOT penalise;
                               penalise only if required skills appear here or if preferred language is absent

COMPENSATION
- salary_accuracy              only extracted if explicitly stated; correct currency and period

OVERALL
- null_appropriateness         nulls used correctly — penalise hallucinated values and clear over-nulling
- overall                      Holistic rule compliance across ALL field groups equally (Company, Role,
                               Skills, Compensation). Do NOT anchor on null_appropriateness — that is
                               scored separately. A high null_appropriateness does not imply a high
                               overall score if other fields have systematic errors, and vice versa.
                               Weight every group equally; penalise any group with clear rule violations.
- flags                        specific rule violations as short strings; empty list if none

Return ONLY a valid JSON object with exactly these keys. No preamble, no markdown fences.
"""

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

    # Strip passthrough fields — raw inputs copied verbatim, not extracted values.
    # Including description creates circular evaluation; title/location have no ground-truth.
    extracted_dict = {
        k: v for k, v in extracted.model_dump().items()
        if k not in ("title", "description", "location")
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
            {"role": "user", "content": _build_user_message(job_title, description, extracted)},
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
            {"role": "user", "content": _build_user_message(job_title, description, extracted)},
        ],
        max_retries=3,
        temperature=0,
    )
