from pydantic import BaseModel, ConfigDict, Field


class ResumeExperienceEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str = ""
    organization: str = ""
    date_range: str = ""
    bullets: list[str] = Field(default_factory=list)


class ResumeProjectEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = ""
    technologies: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)


class ResumeEducationEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    school: str = ""
    degree: str = ""
    date_range: str = ""


class NormalizedResume(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = ""
    summary: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[ResumeExperienceEntry] = Field(default_factory=list)
    projects: list[ResumeProjectEntry] = Field(default_factory=list)
    education: list[ResumeEducationEntry] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
