from __future__ import annotations

import json

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.analysis import ClarificationQuestion, MatchScore
from app.schemas.job import NormalizedJob
from app.schemas.resume import NormalizedResume
from app.services.openai_service import OpenAIExtractionError, OpenAIService


class AnalysisLLMOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_summary: str = ""
    top_matches: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    match_score: MatchScore = Field(
        default_factory=lambda: MatchScore(skills=0, keywords=0, overall=0)
    )
    clarification_questions: list[ClarificationQuestion] = Field(default_factory=list)


class AnalysisService:
    def __init__(self, openai_service: OpenAIService) -> None:
        self._openai_service = openai_service

    async def analyze_fit(
        self,
        *,
        normalized_job: NormalizedJob,
        normalized_resume: NormalizedResume,
    ) -> AnalysisLLMOutput:
        payload = {
            "job": normalized_job.model_dump(),
            "resume": normalized_resume.model_dump(),
        }
        return await self._openai_service.extract_structured_output(
            prompt_name="analyze_fit.txt",
            schema_name="analyze_fit",
            schema_model=AnalysisLLMOutput,
            content=json.dumps(payload),
        )
