from pydantic import BaseModel, ConfigDict, Field

from app.schemas.analysis import MatchScore


class RespondRequest(BaseModel):
    session_id: str
    answer: str


class OptimizedResumeOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = ""
    key_skills: list[str] = Field(default_factory=list)
    bullet_updates: list[str] = Field(default_factory=list)


class CareerStrategy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    missing_skills: list[str] = Field(default_factory=list)
    project_suggestions: list[str] = Field(default_factory=list)
    networking_suggestion: str = ""


class RespondResponse(BaseModel):
    session_id: str
    status: str
    optimized_resume: OptimizedResumeOutput
    updated_score: MatchScore
    changes_explained: list[str]
    career_strategy: CareerStrategy
