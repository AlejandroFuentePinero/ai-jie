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
    sector: Optional[str] = None

    # --- Company ---
    company_name: Optional[str] = Field(
        None,
        description="Canonical company name. Null if not mentioned.",
    )
    company_description: Optional[str] = Field(
        None,
        description="Always null.",
    )

    # --- Role ---
    seniority: Optional[Seniority] = Field(
        None,
        description="Title keyword first, then years of experience, then scope of responsibilities. Unknown if unclear.",
    )
    job_family: Optional[JobFamily] = Field(
        None,
        description="Title keyword first. Responsibilities as tiebreaker.",
    )
    years_experience_min: Optional[int] = Field(
        None,
        description="Minimum years explicitly stated. Null if not stated.",
    )
    years_experience_max: Optional[int] = Field(
        None,
        description="Maximum years if a range is stated. Null for open-ended ranges.",
    )
    key_responsibilities: list[str] = Field(
        default_factory=list,
        description="Up to 7 concrete responsibilities. Verb-led. Only what is directly written.",
    )
    education_required: Optional[str] = Field(
        None,
        description="Required education only, not preferred. Null if not stated.",
    )

    # --- Skills scaffolding (chain-of-thought) ---
    responsibility_skills_found: Optional[list[str]] = Field(
        None,
        description=(
            "FILL FIRST. Scan ONLY responsibility/duties statements — "
            "what the person will do in this role. List named tools, "
            "technologies, programming languages, methodologies, or domain skills. "
            "Do NOT scan requirements, qualifications, or preferred sections. "
            "Skill tokens only, not sentences."
        ),
    )
    preferred_signals_found: Optional[list[str]] = Field(
        None,
        description=(
            "FILL SECOND. Find every sentence containing optionality "
            "language (preferred, plus, bonus, nice to have, ideally, "
            "desirable, etc). Copy the FULL sentence, not just the "
            "signal words — the sentence contains the skill names "
            "needed for classification. Null if none exist."
        ),
    )
    all_technical_skills: Optional[list[str]] = Field(
        None,
        description=(
            "FILL THIRD. List EVERY technical skill mentioned anywhere "
            "in the posting — responsibilities, requirements, qualifications, "
            "and preferred sections. Flat list, no classification. "
            "Apply the CV test: only named technologies, tools, methodologies, "
            "and domain expertise areas."
        ),
    )

    # --- Skills classification (partition all_technical_skills) ---
    skills_preferred: Optional[list[str]] = Field(
        None,
        description=(
            "From all_technical_skills, select ONLY skills that appear "
            "in a preferred zone from preferred_signals_found. Exclude "
            "any skill that also appears in responsibility_skills_found. "
            "Null if no optionality language in the posting."
        ),
    )
    skills_required: Optional[list[str]] = Field(
        None,
        description=(
            "All skills from all_technical_skills NOT listed in "
            "skills_preferred above."
        ),
    )
    skills_soft: Optional[list[str]] = Field(
        None,
        description="Interpersonal and behavioural skills. Concise phrases, 2-7 words.",
    )


class EvaluationScore(BaseModel):
    # Company
    company_name_accuracy: int
    company_description_accuracy: int
    # Role
    seniority_accuracy: int
    job_family_accuracy: int
    years_experience_accuracy: int
    education_accuracy: int
    responsibilities_quality: int
    # Skills
    skills_required_accuracy: int
    skills_preferred_accuracy: int
    skills_soft_accuracy: int
    # Overall
    null_appropriateness: int
    overall: int
    flags: list[str]
