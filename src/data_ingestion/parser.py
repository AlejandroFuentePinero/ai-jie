import instructor
from openai import AsyncOpenAI, OpenAI

from .models import Job

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
You are an expert job posting parser. Your task is to extract structured information from job postings accurately and consistently.

## General rules
- Only extract what is explicitly stated or strongly implied by the text. Never guess or infer beyond what is written.
- Use null for any field that is missing, ambiguous, or cannot be determined with confidence.
- Do not paraphrase or interpret — extract as close to the original wording as possible, especially for lists.

## Company fields
- company_description: use the first descriptive sentence about the company if present, otherwise null. Do not construct a description yourself.
- industry: use the company's business sector — what the company sells or does — not the technology the role uses. A bank hiring a data scientist → "Financial Services", not "Information Technology". A pharma company → "Pharmaceutical" or the specific sub-domain stated (e.g. "drug development"), not "Data Science". If not stated, infer only from a clear company description. When in doubt between two plausible industries, pick the more specific one (e.g. "FinTech" over "Technology").
- location: use the value from the explicit "Location:" field provided in the user message. If the description also mentions a location, prefer the explicit field. Do not standardise or reformat. Only use null if the Location field is empty or clearly uninformative (e.g. "Remote", "Undisclosed").

## Role fields
- seniority: use this priority order strictly:
    1. Explicit title keyword → use it directly. "Senior Data Scientist" → senior. "Lead Engineer" → lead. "Director of Data Science" → director. Do not second-guess a clear title keyword.
    2. No title keyword (e.g. "Data Scientist", "Analyst", "Engineer") → check years of experience required: 0-1 yrs → junior, 2-4 yrs → mid, 5-7 yrs → senior, 8+ yrs → lead. Use the midpoint if a range is given (e.g. "3-5 years" → mid).
    3. No title keyword and no years stated → check responsibilities tone. Director-level strategy and P&L ownership → director. Team management → manager. Architecture/cross-team technical decisions → lead. Primarily execution → mid. Very basic/entry tasks → junior.
    4. Still unclear → unknown. Do NOT guess. Use "unknown" rather than a speculative answer.
- job_family: use this priority order strictly:
    1. Clear title keyword → use it directly. "Data Engineer" → data_engineering. "ML Engineer" → ml_engineering. "Analytics Engineer" → data_analytics. "Data Analyst" → data_analytics. "Research Scientist" → research. "Engineering Manager" → management. Do not second-guess a clear title keyword.
    2. Ambiguous or generic title (e.g. "Data Scientist", "Engineer", "Specialist") → use primary responsibilities to decide. A "Data Scientist" spending most time on pipelines → data_engineering. A "Data Scientist" building recommendation models → data_science.
    3. Still unclear → other.
  Valid values and their meaning:
    - data_science: modelling, statistical analysis, experimentation, predictions
    - data_engineering: pipelines, ETL, data infrastructure, warehousing
    - ml_engineering: deploying/serving ML models, MLOps, model pipelines in production
    - ai_engineering: LLMs, generative AI, prompt engineering, AI product integration
    - software_engineering: general software development, backend/frontend, APIs
    - data_analytics: BI, dashboards, reporting, business analysis, SQL-heavy insight work
    - research: academic/scientific research, R&D, publications
    - management: people management, team leadership, programme/project management
    - other: only if no category above is a reasonable fit
- years_experience_min / max: only extract if a number is explicitly stated. Do not infer from seniority level.
- key_responsibilities: extract 3-5 concrete actions. Start each with a verb. Exclude generic filler like "work in an agile team" or "communicate with stakeholders" unless they are the core of the role.
- education_required: only extract if explicitly stated as required (e.g. "Bachelor's degree required", "must have a degree in"). Do not extract education listed under preferred, nice-to-have, or bonus sections.

## Skills fields
- skills_technical: extract ALL named tools, technologies, and skill categories from the entire document — including specific products (Python, Spark, Tableau), common tools (Excel, Git, SQL, Linux), platform categories (cloud computing, BI tools, data warehousing), and methodology terms (machine learning, NLP, A/B testing). Include skills from both required AND preferred sections — this list is exhaustive. Only exclude pure marketing filler with zero technical content: "modern stack", "cutting-edge tools". If a specific product is named alongside a category (e.g. "BI tools like Tableau"), extract both.
  - Process/project methodology terms (Agile, Scrum, Kanban, Lean, Six Sigma, Waterfall) are technical skills — put them here, not in skills_soft.
- skills_soft: include soft skills the employer genuinely emphasises for this role. If the employer devoted a sentence or bullet to it, it is likely intentional — include it. Exclude only obvious generic boilerplate with zero specificity ("team player", "fast learner" with no further context). Err on the side of including.
  - Extract as concise phrases (2–7 words), not full verbatim sentences. Condense "Must possess ability to effectively communicate with team members and across all departments/levels of the organization" → "Strong cross-functional communication skills".
  - Process/project methodology terms (Agile, Scrum, Kanban) belong in skills_technical, not here.
- nice_to_have: only include skills from sections or sentences explicitly using words like "preferred", "nice to have", "a plus", "bonus", "ideally", "would be an asset", "desirable". A skill listed in a "requirements" section is required even if phrased gently.
  - Extract as concise skill names (e.g. "Spark", "Tableau"), not full sentences.
  - A preferred-only skill appearing in both skills_technical and nice_to_have is correct — skills_technical is exhaustive, nice_to_have flags it as optional.
  - A violation is: a clearly required skill appearing in nice_to_have, or nice_to_have skills without any explicit preferred/bonus language in the source.

## Compensation fields
- Only extract salary if explicitly stated as a number or range. Do not infer from seniority or market knowledge.
- salary_period: default to "annual" only if the figure is clearly an annual salary. Otherwise use exactly what is stated or null.
- salary_currency: infer from country or currency symbol if not stated as ISO code (e.g. $ in an Australian posting → AUD).
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
) -> Job:
    """Async extraction — use this in the pipeline for concurrent processing."""
    return await _get_async_client().chat.completions.create(
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


def parse_posting(
    job_title: str,
    job_description: str,
    location: str,
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
