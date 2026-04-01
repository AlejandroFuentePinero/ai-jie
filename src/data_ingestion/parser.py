import instructor
from openai import AsyncOpenAI, OpenAI

from .models import Job

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
You are an expert job posting parser. Your task is to extract structured information from job postings accurately and consistently.

## General rules
- Only extract what is explicitly stated or strongly implied by the text. Use null for any field that is missing, ambiguous, or cannot be determined with confidence.
- Apply semantic judgment where the rules below require it (e.g. inferring seniority from responsibilities, identifying optional framing for skills). For all other fields, extract faithfully without adding meaning that isn't there.

## Company fields
- company_name: extract the canonical name of the hiring company. It may appear anywhere — in a header, an "About us" section, the job description body, or a footer. Use the company name, not a division or team (e.g. "IBM" not "IBM's Watson AI Group", "Google" not "Google Cloud Platform team"). Return null (not the string "null") if the company is genuinely not mentioned anywhere in the posting.
- company_description: always return null.

## Role fields
- seniority: valid values in ascending order: intern, junior, mid, senior, lead, principal, manager, director, unknown. Use this priority order strictly:
    1. Explicit seniority keyword in the job title, or an explicit level statement anywhere in the posting → use it directly, no override. The patterns below apply to the job title; "Lead" and similar words used as verbs in the description body (e.g. "lead a team of analysts") are NOT seniority signals:
       - "Senior ..." or "... Senior" → senior
       - "Lead ..." or "... Lead" → lead
       - "Principal ..." → principal
       - "Intern ..." or "... Intern" or "internship" → intern
       - "Junior ..." or "Associate ..." (when used as a level — e.g. "Associate Consultant" → junior. Exception: when "Associate" precedes a traditionally senior title such as Director, Principal, or Partner, treat the combined title as its own mid-to-senior level, not junior — e.g. "Associate Director", "Associate Principal") → junior
       - "entry-level" stated explicitly → junior
       - "Staff ..." → senior
       - "... Manager" or "Manager ..." in the title → manager (e.g. "Analytics Manager" → manager, "Engineering Manager" → manager). Exception: "Product Manager" is not a people-management role — use responsibilities and years of experience to determine seniority instead. When a title combines a rank modifier with a management keyword (e.g. "Senior Analytics Manager", "Senior Engineering Manager"), the management keyword takes precedence — return manager.
       - "Director ..." or "... Director" → director
       - "VP" or "Vice President" → director. Note: "AVP" or "Associate Vice President" is an early-to-mid career level in banking and financial services — map to senior, not director if the role is specifically in a banking or financial services (infer sector/industry from the posting context).
       - "This is a senior-level role", "mid-level", "entry-level" stated explicitly anywhere in the posting → use the stated level
       Do not second-guess any of these. Job title rank words ARE seniority signals.
    2. No explicit seniority word anywhere → if years of experience are stated, use: 0-1 → junior, 2-4 → mid, 5-7 → senior, 8+ → lead. Then check whether the described responsibilities clearly indicate a higher level than the years suggest (e.g. a role requiring 3 years but describing team management or architecture ownership → senior). Scope signals include mentoring junior engineers, owning system design, leading cross-team programmes, managing direct reports — these are examples, not an exhaustive list. Adjust up by one level if scope clearly exceeds what years imply. If no years are stated, classify directly from scope: individual contributor executing defined tasks → junior; competent IC with some ownership of specific components → mid; owns a system or domain area, or mentors others → senior; cross-team technical authority or architectural ownership → lead. Default to mid if responsibilities describe competent IC work with no clear scope signals in either direction.
    3. Still unclear → return unknown. Do NOT guess.
- job_family: use this priority order strictly:
    1. Clear title keyword → use it directly. "Data Engineer" → data_engineering. "ML Engineer" → ml_engineering. "Analytics Engineer" → data_analytics. "Data Analyst" → data_analytics. "Research Scientist" → research. "Engineering Manager" → management. Do not second-guess a clear title keyword. Exception: "Data Scientist" is treated as ambiguous regardless of the keyword — proceed to step 2 and decide from primary responsibilities.
    2. Ambiguous or generic title (including "Data Scientist", "Scientist", "Engineer", "Specialist") → use primary responsibilities to decide. A "Data Scientist" spending most time on pipelines → data_engineering. A "Data Scientist" building recommendation models → data_science.
    3. Still unclear → other.
  Valid values and their meaning:
    - data_science: modelling, statistical analysis, experimentation, predictions
    - data_engineering: pipelines, ETL, data infrastructure, warehousing
    - ml_engineering: deploying/serving ML models, MLOps, model pipelines in production
    - ai_engineering: LLMs, generative AI, prompt engineering, AI product integration
    - software_engineering: general software development, backend/frontend, APIs
    - data_analytics: BI, dashboards, reporting, business analysis, SQL-heavy insight work
    - research: academic/scientific research, R&D, publications
    - management: people management, team leadership, programme/project management, product management
    - other: only if no category above is a reasonable fit
- years_experience_min / max: only extract if a number is explicitly stated. Do not infer from seniority level. For open-ended ranges ("3+ years", "at least 5 years", "minimum 3 years") set years_experience_min to the stated number and years_experience_max to null.
- key_responsibilities: extract the concrete responsibilities explicitly stated in the posting. Start each with a verb. Do not infer or construct responsibilities — only use what is directly written. Exclude generic filler like "work in an agile team" or "communicate with stakeholders" unless they are explicitly stated as a core part of the role. Extract up to 7. If the posting lists more than 7, select the first 7 stated.
- education_required: only extract if explicitly stated as required (e.g. "Bachelor's degree required", "must have a degree in"). Do not extract education listed under preferred, nice-to-have, or bonus sections. Normalise to a concise phrase, e.g. "Bachelor's in Computer Science", "Master's degree". If the posting adds "or equivalent experience", retain it — e.g. "Bachelor's in Computer Science or equivalent experience".
- remote_policy: only extract if the posting explicitly states the work arrangement. Normalise to one of: Remote, Hybrid, On-site (e.g. "fully remote", "hybrid 3 days a week", "on-site in Sydney"). Return null if not explicitly stated.
- employment_type: only extract if explicitly stated. Normalise to one of: Full-time, Part-time, Contract, Casual, Temporary. "Temporary" may appear in the job title (e.g. "Temporary Data Analyst") or in the body (e.g. "this is a temporary position", "fixed-term contract"). Return null if not stated.

## Skills fields
- skills_required: HARD BOUNDARY — this field is for technical and domain knowledge only. Any interpersonal, behavioural, or soft skill — regardless of where it appears in the posting — belongs in skills_soft, never here. If in doubt about whether something is a soft skill, it goes to skills_soft. Examples that must NOT appear here: communication, leadership as an interpersonal trait (e.g. "strong leadership skills", "natural leader", "leading through influence", "leading cross-functional collaboration") — note: leadership belongs in skills_required only when it specifies what is being led in technical or domain terms (e.g. "experience leading data engineering teams", "technical leadership of ML projects", "leading ML model deployments"); facilitation, ideation, interpersonal skills, collaboration, creativity, problem-solving (as a behavioural trait), stakeholder management, and similar tokens are soft skills and do not belong here.
  Normalise skill names to their most commonly used professional form (e.g. "Amazon Web Services" → "AWS", "Python 3" → "Python", "MS Excel" → "Excel"). Extract all technical skills, tools, technologies, methodology terms, and domain expertise areas the posting presents as required or expected. This includes both precise tokens (Python, Spark, SQL) and broader knowledge domain areas (e.g. "investment finance", "security analytics", "portfolio risk management", "regulatory compliance", "clinical trial design", and other domain technical skills). Use semantic judgment — required intent may come from explicit language ("required", "must have") or simply from context. Note: emphasis words like "strong", "solid", or "proficiency in" describe the desired level of a skill, not whether it is required — use the surrounding context to determine required vs preferred, not the emphasis wording alone. Be exhaustive. If a specific product is named alongside a category (e.g. "BI tools like Tableau"), extract both. Process/project methodology terms (e.g., Agile, Scrum, Kanban) are technical — place them here if required, or in skills_preferred if presented as optional/desirable/nice-to-have; never in skills_soft.
  If the same skill appears in both a required context (responsibilities section, required skills section) and a preferred/optional context, classify it as skills_required — the stronger signal takes precedence.
  Important: scan the entire posting, including the responsibilities section. Tools and technologies may be named anywhere — not just in a skills section — and are implicitly required when the role clearly depends on them. For example, "Optimise jobs to utilise Kafka, Hadoop, Spark Streaming and Kubernetes resources" implies all four (Kafka, Hadoop, Spark Streaming and Kubernetes) are required skills even though they appear in a responsibility bullet. They should be included in both, key_responsibilities and skills_required fields.
- skills_preferred: extract all technical skills, tools, technologies, and domain expertise areas the posting presents explicitly as optional or desirable. Skills listed without any optional framing default to skills_required — absence of the word "required" is not sufficient to classify a skill as preferred; there must be a positive signal of optionality. Use semantic judgment to identify that signal — language like "preferred", "nice to have", "a plus", "bonus", "ideally", "desirable" are examples, not an exhaustive list. Return null if the posting gives no signal that any skill is optional rather than required.
- skills_soft: extract interpersonal and organisational skills the employer genuinely emphasises for this role. Include when the employer devoted a sentence or bullet to it — that signals intent. Exclude obvious generic boilerplate with zero specificity ("team player", "fast learner" with no further context). Extract as concise phrases (2–7 words) — condense, do not copy verbatim sentences. Examples of correct condensing: "Excellent ideation, facilitation and communications skills" → "facilitation and communication skills"; "Detail-oriented team player with strong interpersonal skills" → "strong interpersonal skills". Covers all soft skills regardless of whether they are framed as required or preferred. Process/project methodology terms (Agile, Scrum, Kanban) belong in skills_required or skills_preferred, not here.

## Compensation fields
- Only extract salary if explicitly stated as a number or range. Do not infer from seniority or market knowledge.
- salary_min: lower bound of a stated salary. For a range ("$80k–$100k") → 80000. For open-ended ("$80k+", "from $80k", "at least $80k") → 80000. Null if no salary is stated.
- salary_max: upper bound of a stated range ("$80k–$100k") → 100000. Null for open-ended ranges ("$80k+", "from $80k"). Null if no salary is stated.
- salary_period: annual, monthly, or hourly. Infer from context (e.g. a six-figure figure with no qualifier → annual). Null if unclear.
- salary_currency: infer from country context or currency symbol when possible (e.g. $ in an Australian posting → AUD). If the currency symbol is ambiguous and no country context is available, return null.
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
