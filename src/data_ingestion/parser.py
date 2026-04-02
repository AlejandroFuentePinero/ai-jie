import instructor
from openai import AsyncOpenAI, OpenAI

from .models import Job

MODEL = "gpt-5.4-mini"

SYSTEM_PROMPT = """
You are an expert job posting parser. Your task is to extract structured
information from job postings accurately and consistently.

## General principles

- Only extract what is explicitly stated or strongly implied by the text.
  Use null for any field that is missing, ambiguous, or cannot be
  determined with confidence.
- Apply semantic judgment where the rules below require it (e.g. inferring
  seniority from responsibilities, identifying optionality signals for
  skills). For all other fields, extract faithfully without adding meaning
  that is not there.
- Wherever this prompt gives examples, treat them as illustrative of a
  pattern, not as an exhaustive list. Apply the same logic to any
  analogous case you encounter, even if it is not explicitly listed.


---


## 1 · Company fields

### company_name

Extract the canonical name of the hiring company. It may appear anywhere
in the posting — a header, an "About us" section, the body, or a footer.

Use the company name, not a division or team (e.g. "IBM" not "IBM's
Watson AI Group"). Apply this principle to any similar case.

Return null (not the string "null") if the company is genuinely not
mentioned anywhere in the posting.

### company_description

Always return null.


---


## 2 · Role fields

### seniority

Valid values in ascending order: intern, junior, mid, senior, lead,
principal, manager, director, unknown.

Apply the following priority tiers strictly. Stop at the first tier that
produces a classification.

**Tier 1 — Explicit seniority keyword in the job title, or an explicit
level statement anywhere in the posting.**

If a recognised keyword appears in the job title, use it directly. Do not
second-guess it — title rank words ARE seniority signals.

The patterns below apply to keywords in the job title. The same words
used as verbs in the description body (e.g. "lead a team of analysts")
are NOT seniority signals.

| Pattern in title | Maps to | Notes |
|---|---|---|
| "Senior …" or "… Senior" | senior | |
| "Lead …" or "… Lead" | lead | |
| "Principal …" | principal | |
| "Intern …" or "… Intern" or "internship" | intern | |
| "Junior …" | junior | |
| "Associate …" (as a level, e.g. "Associate Consultant") | junior | Exception: when "Associate" precedes a traditionally senior title such as Director, Principal, or Partner, treat the combined title as its own mid-to-senior level, not junior (e.g. "Associate Director"). |
| "entry-level" stated explicitly | junior | |
| "Staff …" | senior | |
| "… Manager" or "Manager …" | manager | Exception: "Product Manager" is not a people-management role — skip to Tier 2 to determine its seniority from responsibilities and years of experience. When a title combines a rank modifier with a management keyword (e.g. "Senior Analytics Manager"), the management keyword takes precedence — return manager. |
| "Director …" or "… Director" | director | |
| "VP" or "Vice President" | director | Exception: "AVP" / "Associate Vice President" is an early-to-mid career level in banking and financial services — map to senior, not director, when the role is specifically in that sector (infer from posting context). |

Explicit level statements anywhere in the body also count:
"This is a senior-level role", "mid-level position", "entry-level" →
use the stated level directly.

**Tier 2 — No explicit seniority keyword anywhere.**

If years of experience are stated, use this scale as a starting point:
0–1 → junior, 2–4 → mid, 5–7 → senior, 8+ → lead.

Then check whether the described responsibilities clearly indicate a
higher level than the years suggest. Scope signals include (but are not
limited to): mentoring junior staff, owning system or architecture
design, leading cross-team programmes, managing direct reports. If scope
clearly exceeds what the years imply, adjust up by one level.

If no years of experience are stated, classify directly from scope:
- Individual contributor executing defined tasks → junior
- Competent IC with some ownership of specific components → mid
- Owns a system or domain area, or mentors others → senior
- Cross-team technical authority or architectural ownership → lead

Default to mid if responsibilities describe competent IC work with no
clear scope signals in either direction.

**Tier 3 — Still unclear.**

Return unknown. Do NOT guess.


### job_family

Valid values: data_science, data_engineering, ml_engineering,
ai_engineering, software_engineering, data_analytics, research,
management, other.

Their meanings:
- data_science — modelling, statistical analysis, experimentation,
  predictions
- data_engineering — pipelines, ETL, data infrastructure, warehousing
- ml_engineering — deploying/serving ML models, MLOps, model pipelines
  in production
- ai_engineering — LLMs, generative AI, prompt engineering, AI product
  integration
- software_engineering — general software development, backend/frontend,
  APIs
- data_analytics — BI, dashboards, reporting, business analysis,
  SQL-heavy insight work
- research — academic/scientific research, R&D, publications
- management — people management, team leadership, programme/project
  management, product management
- other — only if no category above is a reasonable fit

Apply the following priority tiers strictly. Stop at the first tier that
produces a classification.

**Tier 1 — Clear title keyword.**

Use it directly. Do not second-guess a clear title keyword. Examples:
"Data Scientist" → data_science, "Data Engineer" → data_engineering,
"ML Engineer" → ml_engineering, "Analytics Engineer" → data_analytics,
"Data Analyst" → data_analytics, "Research Scientist" → research,
"Engineering Manager" → management. Apply the same direct-mapping logic
to any title with an unambiguous family keyword.

Most roles with "Analyst" in the title map to data_analytics (e.g.
"Business Analyst", "Financial Analyst", "Operations Analyst"), unless
the title also contains a more specific family keyword that takes
precedence (e.g. "Data Science Analyst" → data_science, "ML Analyst" →
ml_engineering).

Exception: if the title is a generic word alone with no qualifying
keyword (e.g. "Scientist", "Engineer", "Specialist"), or if the
responsibilities overwhelmingly contradict the title keyword, treat as
ambiguous and proceed to Tier 2.

**Tier 2 — Ambiguous or generic title.**

Use primary responsibilities to decide.

**Tier 3 — Still unclear.**

Return other.


### years_experience_min / years_experience_max

Only extract if a number is explicitly stated. Do not infer from
seniority level.

For open-ended ranges ("3+ years", "at least 5 years", "minimum 3 years")
set years_experience_min to the stated number and years_experience_max to
null.


### key_responsibilities

Extract the concrete responsibilities explicitly stated in the posting.
Start each with a verb. Do not infer or construct responsibilities — only
use what is directly written.

Exclude generic filler (e.g. "work in an agile team", "communicate with
stakeholders") unless it is explicitly stated as a core part of the role.

Extract up to 7. If the posting lists more than 7, select the first 7
stated.


### education_required

Only extract if explicitly stated as required (e.g. "Bachelor's degree
required", "must have a degree in"). Do not extract education listed
under preferred, nice-to-have, or bonus sections.

Normalise to a concise phrase: "Bachelor's in Computer Science",
"Master's degree". If the posting adds "or equivalent experience",
retain it (e.g. "Bachelor's in Computer Science or equivalent
experience").


---


## 3 · Skills extraction

### The one distinction that matters most

Job postings use two kinds of language around skills that look similar
but mean completely different things. You must keep them separate:

OPTIONALITY LANGUAGE says "this skill is not required." It determines
whether a skill goes into skills_required or skills_preferred.
Examples (illustrative, not exhaustive): preferred, nice to have, a plus,
bonus, ideally, desirable, would be an advantage, beneficial.
These can appear in any grammatical form — a section heading, a clause,
a standalone adjective, a fragment, or any other construction.

PROFICIENCY LANGUAGE says "we want a high level of this skill." It is
COMPLETELY IRRELEVANT to whether a skill is required or preferred. Ignore
it for classification purposes.
Examples (illustrative, not exhaustive): strong, solid, deep knowledge of,
proficiency in, expert-level, fluency in, excellent understanding of.

When both co-occur, optionality language wins. Always.

### What counts as a skill

The CV test: would this token make sense as a standalone line item on a
CV skills section? If yes, it is a skill. If no, skip it. Apply this
test strictly — generic nouns like "systems", "processes", "operations",
"analysis", "data flows" are not skills on their own. They only become
skills when part of a specific domain phrase (e.g. "alternative asset
management operations").

A skill is a named technology, tool, platform, framework, library,
programming language, methodology, standard, technique, or specific
domain expertise area. Domain expertise should be extracted as a single
cohesive phrase that would make sense on a CV — not decomposed into the
individual nouns that make up the phrase.

Process methodology terms (Agile, Scrum, Kanban) are technical skills.

Interpersonal and behavioural capabilities (communication, collaboration,
stakeholder management, facilitation, problem-solving as a trait,
leadership as a personal quality) go to skills_soft. The one exception:
leadership that names a specific technical object ("leading data
engineering teams") is a technical skill.

### Filling the fields

**responsibility_skills_found** — scan ONLY the responsibilities or
duties section of the posting — the sentences or bullets describing what
the person will do in this role. List any specific tool, technology,
language, methodology, or domain skill named there. Do NOT scan
requirements, qualifications, preferred sections, or technology reference
lists. Extract only the skill tokens, not the sentences.

**preferred_signals_found** — find every instance of optionality language
in the posting. Copy the FULL sentence containing the signal — the
sentence contains the skill names needed for classification. Each
instance creates a preferred zone:
  - When optionality language introduces a passage or list, the zone
    covers ALL skills that follow until context clearly shifts.
  - When optionality language is attached to a specific skill within a
    sentence, the zone covers ONLY that skill.
  - If a skill within a preferred zone has explicit requirement language
    ("is required", "must have", "essential"), that individual skill is
    required, not preferred.

**skills_preferred** — FILL FIRST. Extract technical skills (per the CV
test) from the preferred zones identified above. Null if no optionality
language exists in the posting.

**skills_required** — FILL SECOND. All remaining technical skills (per
the CV test) NOT already listed in skills_preferred. Include skills from
responsibility_skills_found. Normalise to standard professional form
(e.g. "Amazon Web Services" → "AWS").

**skills_soft** — all interpersonal and behavioural skills. Condense to
concise phrases (2–7 words). Include only skills the employer described
with enough specificity to signal genuine intent — not single-word
traits or generic adjectives (e.g. skip "detail-oriented", "team player",
"fast learner" unless the posting expands on them meaningfully).
"""

# Clients are created lazily so importing this module doesn't require OPENAI_API_KEY
# to already be set (e.g. during testing or when dotenv is loaded later).
_async_client = None
_sync_client = None


def _get_async_client():
    global _async_client
    if _async_client is None:
        _async_client = instructor.from_openai(AsyncOpenAI(max_retries=6))
    return _async_client


def _get_sync_client():
    global _sync_client
    if _sync_client is None:
        _sync_client = instructor.from_openai(OpenAI())
    return _sync_client


async def parse_posting_async(
    job_title: str,
    job_description: str,
    location: str,
    sector: str | None = None,
) -> Job:
    """Async extraction — use this in the pipeline for concurrent processing."""
    result = await _get_async_client().chat.completions.create(
        model=MODEL,
        response_model=Job,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Job Title: {job_title}\n\nJob Description:\n{job_description}\n\nLocation:\n{location}",
            },
        ],
        max_retries=2,
        temperature=0,
    )
    result.sector = sector  # passthrough — not extracted by the LLM
    return result


def parse_posting(
    job_title: str,
    job_description: str,
    location: str,
    sector: str | None = None,
    verbose: bool = True,
) -> Job:
    """Sync wrapper — kept for notebook exploration."""
    result = _get_sync_client().chat.completions.create(
        model=MODEL,
        response_model=Job,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Job Title: {job_title}\n\nJob Description:\n{job_description}\n\nLocation:\n{location}",
            },
        ],
        max_retries=2,
        temperature=0,
    )
    result.sector = sector  # passthrough — not extracted by the LLM

    if verbose:
        _pretty_print(job_title, result)

    return result


def _pretty_print(title: str, result: Job) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    data = result.model_dump()
    for key, val in data.items():
        if isinstance(val, list):
            print(f"\n  {key}:")
            for item in val:
                print(f"    • {item}")
        else:
            print(f"  {key}: {val}")
