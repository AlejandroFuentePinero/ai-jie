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

EVALUATION PRINCIPLES — read these before scoring anything:

1. COMPLETENESS: The primary goal of the extractor is to retrieve everything meaningful. For skills,
   enumerate the ones you can identify in the posting and check whether the extractor captured them.
   Some items sit on the boundary of what counts as a skill — reasonable people may disagree on
   those, so minor gaps on borderline items are expected and should not be heavily penalised. Reserve
   score 1 for cases where clearly important skills are missing.

2. SEMANTIC ACCURACY: Once extracted, evaluate whether the meaning is faithfully captured — not
   whether the wording is verbatim. The extractor normalises and paraphrases by design. Examples of
   correct behaviour that must NOT be penalised:
   - A skill described as "experience designing distributed data systems at scale" extracted as
     "distributed data systems" — faithful normalisation, not an error.
   - A key responsibility rewritten to start with a verb ("Design scalable pipelines" from "You will
     be designing scalable pipelines") — required by the extraction rules, semantically identical.
   - A company name extracted as "IBM" from "IBM's Watson AI Research Group" — correct canonicalisation.
   - A seniority inferred as "senior" from responsibilities describing architecture ownership and team
     leadership — correct semantic reading even without the word "senior" appearing.
   Only penalise when the extraction is semantically wrong, misleading, or missing something
   meaningful — not when it faithfully paraphrases or normalises the original.

The extractor was given these exact rules. Evaluate compliance with them:

── EXTRACTION RULES THE EXTRACTOR FOLLOWED ──────────────────────────────────────

COMPANY
- company_description: always null — always score 3 if null, score 1 if any value is present.

ROLE
- seniority: determined in strict priority order:
    1. Explicit seniority word anywhere in the title or description → use directly, no override.
       Title rank words ARE seniority signals — examples: "Senior ..." → senior, "Lead ..." → lead,
       "Principal ..." → principal, "... Manager" or "Manager ..." → manager (exception: "Product Manager"
       is not a people-management role — use responsibilities and years instead),
       "Director ..." → director, "VP" / "Vice President" → director,
       "Intern ..." / "... Intern" / "internship" → intern,
       "AVP" / "Associate Vice President" → senior (not director — AVP is early-to-mid in many industries),
       "Associate ..." when used as a level → junior (exception: when "Associate" precedes a traditionally
       senior title such as Director, Principal, or Partner, treat the combined title as its own
       mid-to-senior level, not junior), "Staff ..." → senior.
       Phrases like "this is a senior-level role" or "mid-level analyst" also count.
    2. No explicit seniority word anywhere → if years are stated, use: 0-1 → junior, 2-4 → mid,
       5-7 → senior, 8+ → lead. If no years stated, assess responsibilities alone using scope signals.
       In both cases, check whether responsibilities clearly indicate a higher level than years suggest —
       mentoring junior engineers, owning system design, leading cross-team programmes, managing direct
       reports are examples. A reasonable upward adjustment for scope is correct behaviour.
    3. Still unclear → "unknown". This is correct behaviour, not an error.
- job_family: determined by strict priority:
    1. Clear title keyword → use it directly ("Data Engineer" → data_engineering, "ML Engineer" → ml_engineering,
       "Analytics Engineer" → data_analytics, "Data Analyst" → data_analytics, "Research Scientist" → research,
       "Engineering Manager" → management). Exception: "Data Scientist" is always treated as ambiguous —
       primary responsibilities decide, even when the title is explicit.
    2. Ambiguous or generic title (including "Data Scientist", "Engineer", "Specialist") → primary responsibilities decide.
    3. Still unclear → other.
  Valid values: data_science (modelling, stats, experimentation), data_engineering (pipelines, ETL, infrastructure),
    ml_engineering (deploying/serving models, MLOps), ai_engineering (LLMs, generative AI),
    software_engineering (general dev, APIs), data_analytics (BI, dashboards, reporting, SQL-heavy insight),
    research (academic/scientific R&D), management (people management, team leadership, programme/project management, product management),
    other (nothing else fits). Score 2 if the assignment is defensible but another value is equally valid.
- years_experience: only if a number is explicitly stated; never inferred from seniority. Open-ended ranges
  ("3+ years", "at least 5 years") → min set to stated number, max null. Both null is correct when no
  number appears.
- key_responsibilities: up to 7 concrete verb-led actions explicitly stated in the posting; if more than 7 are listed, the extractor should have selected the first 7 stated; generic filler excluded; no inferred items.
- education_required: only if explicitly required, not preferred. Normalised phrase (e.g. "Bachelor's in Computer Science").

SKILLS
- skills_required: all technical skills, tools, technologies, methodology terms, and domain knowledge
  areas the posting presents as required or expected. Includes precise tool tokens (Python, Spark, SQL)
  and broader knowledge domains senior/specialist roles often require (e.g. "investment finance",
  "security analytics", "regulatory compliance"). Required intent may be explicit or contextual.
  Exhaustive — the extractor was expected to scan the entire posting including the responsibilities
  section. Tools and technologies named in responsibilities are implicitly required skills; penalise
  their omission. Pure marketing filler excluded. Agile/Scrum belong here, not in skills_soft.
  HARD BOUNDARY: soft/interpersonal skills never belong here — they go to skills_soft. Penalise any
  item in skills_required that is interpersonal, behavioural, or a soft skill (e.g. communication,
  leadership, facilitation, ideation, collaboration, creativity, interpersonal skills).
- skills_preferred: all technical skills, tools, technologies, and domain expertise areas the posting
  presents as optional or desirable. The extractor used semantic judgment — optional framing may be
  explicit ("preferred", "nice to have", "a plus") or contextual. Null when no optional framing exists.
- skills_soft: interpersonal and organisational skills the employer genuinely emphasises. Concise
  phrases. Covers soft skills regardless of required/preferred framing. Generic boilerplate with zero
  specificity may be null — correct. Agile/Scrum in skills_soft is an error.

─────────────────────────────────────────────────────────────────────────────────

SCORING GUIDE (apply to every dimension):
  3 = correct and complete per the rules above; no meaningful issues
  2 = mostly correct but a minor deviation from the rules, or a small omission
  1 = clearly wrong, hallucinated, or a significant violation of the rules

IMPORTANT — when in doubt, score 2 not 1:
  If you are uncertain whether an extraction is correct — because signals conflict, because the
  item sits on the boundary of what counts as a skill, or because the semantic reading is
  defensible even if not the only valid one — score 2. Reserve 1 for clear, unambiguous errors
  where the extraction is semantically wrong or an obviously important item is missing.

DIMENSIONS:

COMPANY
- company_name_accuracy        canonical company name extracted (not a division/team); null only if
                               genuinely not mentioned anywhere in the posting — penalise null when
                               the company name is clearly present
- company_description_accuracy always null (populated by enrichment agent, not extracted); score 3 if null, score 1 if any value present

ROLE
- seniority_accuracy           TO SCORE: (1) check title and description for explicit seniority
                               words — "Senior", "Lead", "Principal", "Manager", "Director", "VP",
                               "AVP", "Staff", level phrases like "mid-level" — if present, verify
                               the extractor used the correct seniority value; (2) if no explicit
                               seniority word exists, the extractor inferred from years + scope of
                               responsibilities — evaluate whether that inference is semantically
                               defensible given the full posting; if the inference is reasonable,
                               score 3 even if you might have inferred differently; score 1 only
                               if the extracted value is clearly contradicted by explicit signals
                               in the posting (e.g. "junior" when the title says "Senior", or
                               "senior" when 0-1 years are stated and no senior scope exists);
                               (3) "unknown" is correct when signals are genuinely absent or
                               conflicting — never penalise it
- job_family_accuracy          title-first: clear title keyword overrides responsibilities; ambiguous title → responsibilities
- years_experience_accuracy    only extracted if explicitly stated as a number
- education_accuracy           only required education; preferred/nice-to-have education excluded
- responsibilities_quality     up to 7 concrete verb-led actions explicitly stated; if the posting lists more than 7, the first 7 stated should have been selected; no inferred items; no generic filler; penalise truncation (e.g. only 5 when 9 are clearly listed)

SKILLS
- skills_required_accuracy     TO SCORE: (1) read the posting and identify every technical skill,
                               tool, technology, methodology term, and domain expertise area you judge
                               to be required or expected — including broad competency areas for senior
                               roles, not just precise tool tokens; (2) evaluate semantic completeness:
                               did the extractor capture the meaningful skill signal, even if phrased
                               differently? A domain area like "investment finance" is correct even if
                               not a precise token. (3) penalise clear omissions of required skills and
                               hallucinated items. Score 3 if semantically complete, 2 if minor gaps,
                               1 if significant required skills are missing. Agile/Scrum are technical.
- skills_preferred_accuracy    TO SCORE: (1) read the posting and identify every skill presented as
                               optional or desirable using semantic judgment; (2) evaluate semantic
                               completeness — did the extractor capture what the posting signals as
                               preferred? (3) penalise required skills incorrectly placed here, or
                               significant omissions of preferred skills. Score 3 if coverage is
                               correct, 2 if minor gaps, 1 if significant misses or wrong placement.
                               Null is correct when nothing is presented as optional.
- skills_soft_accuracy         TO SCORE: (1) identify soft/interpersonal skills the employer genuinely
                               emphasises (a sentence or bullet devoted to it signals intent); (2) check
                               extractor coverage — did it capture the meaningful soft skill signal?
                               Soft skills are inherently interpretive; the extractor uses semantic
                               judgment, so accept reasonable paraphrases and condensed phrases; (3) format:
                               items should be concise phrases rather than verbatim sentences — a format
                               issue alone caps the score at 2 but never causes a score of 1; (4) score 1
                               only for clear content errors: Agile/Scrum placed here, or a posting with
                               clearly emphasised soft skills returning null. Generic boilerplate with zero
                               specificity being null is correct, not a miss.

OVERALL
- null_appropriateness         nulls used correctly — penalise hallucinated values and clear over-nulling
- overall                      Holistic rule compliance across ALL field groups equally (Company, Role,
                               Skills, Compensation). Do NOT anchor on null_appropriateness — that is
                               scored separately. A high null_appropriateness does not imply a high
                               overall score if other fields have systematic errors, and vice versa.
                               Weight every group equally; penalise any group with clear rule violations.
                               Groups: Company, Role, Skills.
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

    # Strip passthrough fields and scaffolding fields before sending to judge.
    # description creates circular evaluation; title/location have no ground-truth.
    # preferred_signals_found is chain-of-thought scaffolding — not a quality target.
    _JUDGE_EXCLUDE = {"title", "description", "location", "preferred_signals_found", "responsibility_skills_found"}
    extracted_dict = {
        k: v for k, v in extracted.model_dump().items()
        if k not in _JUDGE_EXCLUDE
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
