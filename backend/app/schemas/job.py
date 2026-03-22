from pydantic import BaseModel, ConfigDict, Field


class NormalizedJob(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = ""
    company: str = ""
    location: str = ""
    summary: str = ""
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    qualifications: list[str] = Field(default_factory=list)
