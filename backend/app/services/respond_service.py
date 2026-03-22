from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.analysis import MatchScore
from app.schemas.job import NormalizedJob
from app.schemas.respond import CareerStrategy, OptimizedResumeOutput
from app.schemas.resume import NormalizedResume, ResumeExperienceEntry
from app.services.gap_analysis import build_analysis, parse_normalized_job, parse_normalized_resume
from app.services.openai_service import OpenAIExtractionError, OpenAIService


PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


class RespondLLMOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    optimized_summary: str = ""
    key_skills: list[str] = Field(default_factory=list)
    bullet_updates: list[str] = Field(default_factory=list)
    updated_score: MatchScore = Field(
        default_factory=lambda: MatchScore(skills=0, keywords=0, overall=0)
    )
    changes_explained: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    project_suggestions: list[str] = Field(default_factory=list)
    networking_suggestion: str = ""


class RespondService:
    def __init__(self, openai_service: OpenAIService) -> None:
        self._openai_service = openai_service

    async def build_response(
        self,
        *,
        normalized_job: NormalizedJob,
        normalized_resume: NormalizedResume,
        answer: str,
    ) -> tuple[OptimizedResumeOutput, MatchScore, list[str], CareerStrategy]:
        updated_resume = merge_resume_with_answer(normalized_resume, answer)
        updated_analysis = build_analysis(
            parse_normalized_job(normalized_job),
            parse_normalized_resume(updated_resume),
        )

        if self._openai_service.enabled:
            try:
                llm_output = await self._generate_llm_response(
                    normalized_job=normalized_job,
                    normalized_resume=updated_resume,
                    answer=answer,
                    gaps=updated_analysis.gaps,
                )
                optimized_resume = OptimizedResumeOutput(
                    summary=llm_output.optimized_summary or updated_resume.summary,
                    key_skills=llm_output.key_skills or updated_resume.skills[:8],
                    bullet_updates=llm_output.bullet_updates or flatten_resume_bullets(updated_resume)[:6],
                )
                changes = llm_output.changes_explained or updated_analysis.top_matches
                strategy = CareerStrategy(
                    missing_skills=llm_output.missing_skills or extract_missing_skills(updated_analysis.gaps),
                    project_suggestions=llm_output.project_suggestions[:2],
                    networking_suggestion=llm_output.networking_suggestion
                    or "Reach out to one engineer or recruiter at the target company with a short message tied to this role.",
                )
                return optimized_resume, llm_output.updated_score, changes[:4], strategy
            except OpenAIExtractionError:
                pass

        return build_fallback_response(updated_resume, updated_analysis, answer)

    async def _generate_llm_response(
        self,
        *,
        normalized_job: NormalizedJob,
        normalized_resume: NormalizedResume,
        answer: str,
        gaps: list[str],
    ) -> RespondLLMOutput:
        prompt = load_prompt("respond_resume.txt")
        schema = RespondLLMOutput.model_json_schema()
        payload = {
            "job": normalized_job.model_dump(),
            "resume": normalized_resume.model_dump(),
            "gaps": gaps,
            "clarification_answer": answer,
        }

        response = await self._openai_service.extract_structured_output(
            prompt_name="respond_resume.txt",
            schema_name="respond_resume",
            schema_model=RespondLLMOutput,
            content=json.dumps(payload),
        )
        return response


def load_prompt(prompt_name: str) -> str:
    return (PROMPTS_DIR / prompt_name).read_text(encoding="utf-8")


def merge_resume_with_answer(normalized_resume: NormalizedResume, answer: str) -> NormalizedResume:
    answer = answer.strip()
    if not answer:
        return normalized_resume

    dumped = normalized_resume.model_dump()
    achievements = list(dumped.get("achievements", []))
    achievements.append(answer)

    experience = dumped.get("experience", [])
    if experience:
        experience[0]["bullets"] = [answer] + experience[0].get("bullets", [])
    else:
        experience = [
            ResumeExperienceEntry(
                role="Additional Clarification",
                organization="User Supplied Context",
                date_range="",
                bullets=[answer],
            ).model_dump()
        ]

    dumped["experience"] = experience
    dumped["achievements"] = achievements[:6]
    return NormalizedResume.model_validate(dumped)


def flatten_resume_bullets(resume: NormalizedResume) -> list[str]:
    bullets: list[str] = []
    for entry in resume.experience:
        bullets.extend([bullet for bullet in entry.bullets if bullet.strip()])
    for project in resume.projects:
        bullets.extend([bullet for bullet in project.bullets if bullet.strip()])
    bullets.extend([item for item in resume.achievements if item.strip()])
    return bullets


def extract_missing_skills(gaps: list[str]) -> list[str]:
    if not gaps:
        return []
    lead_gap = gaps[0].split(":")[-1]
    return [item.strip(" .") for item in lead_gap.split(",") if item.strip()]


def build_fallback_response(
    normalized_resume: NormalizedResume,
    updated_analysis,
    answer: str,
) -> tuple[OptimizedResumeOutput, MatchScore, list[str], CareerStrategy]:
    bullets = flatten_resume_bullets(normalized_resume)
    optimized_resume = OptimizedResumeOutput(
        summary=normalized_resume.summary or "Candidate aligned for the target role with added clarification evidence.",
        key_skills=normalized_resume.skills[:8],
        bullet_updates=bullets[:6] if bullets else [answer],
    )
    changes = [
        "Clarification answer was incorporated into the resume evidence set.",
        "Resume scoring was recalculated against the same target job.",
        "Priority gaps were converted into concrete next-step guidance.",
    ]
    strategy = CareerStrategy(
        missing_skills=extract_missing_skills(updated_analysis.gaps),
        project_suggestions=[
            "Build a small project that demonstrates the top missing tool or platform.",
            "Add one project bullet with a measurable performance or user impact result.",
        ],
        networking_suggestion="Message one engineer or recruiter at the target company and mention a project directly relevant to this role.",
    )
    return optimized_resume, updated_analysis.match_score, changes, strategy
