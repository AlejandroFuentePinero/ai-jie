from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


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
    ANALYTICS = "analytics"
    RESEARCH = "research"
    MANAGEMENT = "management"
    OTHER = "other"


class Job(BaseModel):
    """A structured representation of a job posting."""

    # --- Raw input (passthrough) ---
    title: str
    description: str
    location: str

    # --- Company ---
    company_name: Optional[str] = None
    company_description: Optional[str] = Field(
        None,
        description="One sentence about the company, usually at the start of the posting.",
    )
    industry: Optional[str] = Field(
        None,
        description="Industry or domain e.g. fintech, healthcare, SaaS, government.",
    )

    remote_policy: Optional[str] = Field(
        None, description="Remote, hybrid, or on-site — as stated in the posting."
    )
    employment_type: Optional[str] = Field(
        None, description="Full-time, part-time, contract, or casual."
    )

    # --- Role ---
    seniority: Optional[Seniority] = Field(
        None,
        description="Title keyword takes priority. Fall back to years of experience, then responsibilities tone, then unknown.",
    )
    job_family: Optional[JobFamily] = Field(
        None, description="Title keyword takes priority. Use responsibilities as tiebreaker when the title is ambiguous."
    )
    years_experience_min: Optional[int] = Field(
        None, description="Minimum years of experience explicitly stated."
    )
    years_experience_max: Optional[int] = Field(
        None, description="Maximum years of experience if a range is stated."
    )
    key_responsibilities: list[str] = Field(
        default_factory=list,
        description="Top 3-5 core responsibilities as concrete actions.",
    )
    education_required: Optional[str] = Field(
        None,
        description="Minimum education level stated e.g. Bachelor's in Computer Science.",
    )

    # --- Skills ---
    skills_technical: Optional[list[str]] = Field(
        None,
        description="All named tools, technologies, platform categories, and methodology terms from the full document. Exhaustive. Exclude only pure marketing filler.",
    )
    skills_soft: Optional[list[str]] = Field(
        None,
        description="Interpersonal or organisational skills the employer genuinely emphasises. Concise phrases (2–7 words). Null only if the posting contains no meaningful soft skill signal.",
    )
    nice_to_have: Optional[list[str]] = Field(
        None,
        description="Skills from sections or sentences with explicit preferred/bonus language only. Concise skill names.",
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
    company_description_accuracy: int  # 1-3: one sentence, from the text, not invented
    industry_accuracy: int  # 1-3: matches company industry not role domain
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
    skills_technical_precision: int  # 1-3: no vague phrases, only named tools
    skills_technical_recall: int  # 1-3: obvious tools not missed
    skills_soft_accuracy: int  # 1-3: only explicitly named soft skills
    nice_to_have_accuracy: int  # 1-3: only skills explicitly marked as optional
    # Compensation
    salary_accuracy: int  # 1-3: only extracted if explicitly stated
    # Overall
    null_appropriateness: int  # 1-3: nulls used correctly across all fields
    overall: int  # 1-3: holistic trust score
    flags: list[str]  # specific issues found, empty list if none
