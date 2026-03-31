from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Seniority(str, Enum):
    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    MANAGER = "manager"
    DIRECTOR = "director"
    UNKNOWN = "unknown"


class JobFamily(str, Enum):
    DATA_SCIENCE = "data_science"
    DATA_ENGINEERING = "data_engineering"
    ML_ENGINEERING = "ml_engineering"
    AI_ENGINEERING = "ai_engineering"
    SOFTWARE_ENGINEERING = "software_engineering"
    DATA_ANALYTICS = "data_analytics"
    RESEARCH = "research"
    MANAGEMENT = "management"
    OTHER = "other"


class Job(BaseModel):
    """A structured representation of a job posting."""

    @field_validator("*", mode="before")
    @classmethod
    def _coerce_null_string(cls, v):
        """Normalise the string 'null' to None so stray LLM outputs don't pollute fields."""
        if v == "null":
            return None
        return v

    # --- Raw input (passthrough) ---
    title: str
    description: str
    location: str
    sector: Optional[str] = None  # Glassdoor broad sector — passed through, not extracted

    # --- Company ---
    company_name: Optional[str] = Field(
        None,
        description="The name of the hiring company. May appear anywhere in the posting — header, 'About us' section, body, or footer. Extract the canonical company name, not a department or team (e.g. 'IBM' not 'IBM's AI Research Group'). Null only if genuinely not mentioned anywhere.",
    )
    company_description: Optional[str] = Field(
        None,
        description="Always null — populated by a downstream enrichment agent, not extracted from the posting.",
    )

    remote_policy: Optional[str] = Field(
        None, description="Remote, hybrid, or on-site — as stated in the posting."
    )
    employment_type: Optional[str] = Field(
        None, description="Full-time, part-time, contract, casual, or temporary — as stated in the posting. 'Temporary' may appear in the title or body."
    )

    # --- Role ---
    seniority: Optional[Seniority] = Field(
        None,
        description="Explicit seniority anywhere in title or description takes absolute priority. When not explicit: start from years (0-1→junior, 2-4→mid, 5-7→senior, 8+→lead), then adjust up if the described scope clearly exceeds what years suggest (e.g. mentoring juniors, owning architecture, managing direct reports). Unknown if still unclear.",
    )
    job_family: Optional[JobFamily] = Field(
        None, description="Title keyword takes priority. Use responsibilities as tiebreaker when the title is ambiguous."
    )
    years_experience_min: Optional[int] = Field(
        None, description="Minimum years of experience explicitly stated."
    )
    years_experience_max: Optional[int] = Field(
        None, description="Maximum years of experience if a range is stated. Null for open-ended ranges ('3+ years', 'at least 5 years').",
    )
    key_responsibilities: list[str] = Field(
        default_factory=list,
        description="Up to 7 concrete responsibilities explicitly stated in the posting. Verb-led. No inferred or constructed items. If more than 7 are stated, select the first 7 stated.",
    )
    education_required: Optional[str] = Field(
        None,
        description="Minimum education level stated e.g. Bachelor's in Computer Science.",
    )

    # --- Skills ---
    skills_required: Optional[list[str]] = Field(
        None,
        description="Technical skills, tools, technologies, methodology terms, and domain knowledge areas the posting presents as required or expected. Includes precise tokens (Python, SQL) and broader knowledge domains (e.g. 'investment finance', 'security analytics'). Scan the entire posting including responsibilities — tools named in responsibility bullets are implicitly required skills. Exhaustive. Soft/interpersonal skills never go here — they belong in skills_soft regardless of where they appear in the posting.",
    )
    skills_preferred: Optional[list[str]] = Field(
        None,
        description="Technical skills, tools, technologies, and domain expertise areas the posting presents as optional or desirable. Use semantic judgment to identify optional framing. Null if no optional framing exists.",
    )
    skills_soft: Optional[list[str]] = Field(
        None,
        description="Interpersonal or organisational skills the employer genuinely emphasises. Concise phrases (2–7 words) — condense, do not copy verbatim sentences. Covers all soft skills regardless of whether they are framed as required or preferred. Null only if the posting contains no meaningful soft skill signal.",
    )

    # --- Compensation ---
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = Field(
        None, description="ISO currency code e.g. AUD, USD."
    )
    salary_period: Optional[str] = Field(
        None, description="annual, monthly, or hourly."
    )


class EvaluationScore(BaseModel):
    # Company
    company_name_accuracy: int  # 1-3: correctly extracted or null if not stated
    company_description_accuracy: int  # 1-3: always null (enrichment agent handles)
    remote_policy_accuracy: int  # 1-3: remote/hybrid/on-site correctly identified
    employment_type_accuracy: int  # 1-3: full-time/contract etc correctly identified
    # Role
    seniority_accuracy: int  # 1-3: title first, then years, then responsibilities
    job_family_accuracy: int  # 1-3: closest category based on responsibilities
    years_experience_accuracy: (
        int  # 1-3: only extracted if explicitly stated as a number
    )
    education_accuracy: int  # 1-3: only required education, not preferred
    responsibilities_quality: int  # 1-3: concrete verb-led actions, no filler
    # Skills
    skills_required_accuracy: int  # 1-3: required technical skills correctly and completely extracted
    skills_preferred_accuracy: int  # 1-3: preferred/optional technical skills correctly extracted; null ok if none
    skills_soft_accuracy: int  # 1-3: soft skills the employer emphasises, concise phrases
    # Compensation
    salary_accuracy: int  # 1-3: only extracted if explicitly stated
    # Overall
    null_appropriateness: int  # 1-3: nulls used correctly across all fields
    overall: int  # 1-3: holistic trust score
    flags: list[str]  # specific issues found, empty list if none
