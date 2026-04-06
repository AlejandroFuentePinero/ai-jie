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
            "FILL FIRST. Scan ONLY responsibility/duties statements. "
            "Extract named tools, technologies, platforms, frameworks, "
            "libraries, programming languages, named methodologies, and "
            "specific techniques or methods. Do NOT extract discipline "
            "names, field labels, or broad category terms — if a term "
            "names an entire field or degree programme rather than a "
            "specific learnable technique, it is context, not a skill. "
            "If sections are not clearly separated, only treat sentences "
            "describing day-to-day activities as responsibilities, not "
            "sentences stating what the candidate should have or know."
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


# ── Judge Schema ──────────────────────────────────────────────


class EvaluationScore(BaseModel):
    # --- Judge scaffolding (chain-of-thought) ---
    skills_i_consider_required: Optional[list[str]] = Field(
        None,
        description=(
            "FILL FIRST. Read the posting and list every technical skill "
            "YOU judge to be required. This is your ground truth for "
            "scoring skills_required_accuracy."
        ),
    )
    skills_i_consider_preferred: Optional[list[str]] = Field(
        None,
        description=(
            "FILL SECOND. Read the posting and list every technical skill "
            "YOU judge to be preferred/optional. This is your ground truth "
            "for scoring skills_preferred_accuracy. Null if none."
        ),
    )
    skills_i_consider_soft: Optional[list[str]] = Field(
        None,
        description=(
            "FILL THIRD. Read the posting and list every soft/interpersonal "
            "skill YOU judge to be genuinely emphasised. This is your ground "
            "truth for scoring skills_soft_accuracy. Null if none."
        ),
    )
    misclassified_skills: Optional[list[str]] = Field(
        None,
        description=(
            "FILL FOURTH. List any skill that the extractor placed in the "
            "wrong bucket — state the skill, where the extractor put it, "
            "and where it should be. Null if no misclassifications."
        ),
    )

    # --- Scores ---
    # Company
    company_name_accuracy: int  # 1-3
    company_description_accuracy: int  # 1-3
    # Role
    seniority_accuracy: int  # 1-3
    job_family_accuracy: int  # 1-3
    years_experience_accuracy: int  # 1-3
    education_accuracy: int  # 1-3
    responsibilities_quality: int  # 1-3
    # Skills
    skills_required_accuracy: int  # 1-3
    skills_preferred_accuracy: int  # 1-3
    skills_soft_accuracy: int  # 1-3
    # Overall
    null_appropriateness: int  # 1-3
    overall: int  # 1-3
    flags: list[str]
