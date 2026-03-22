from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import settings
from app.schemas.job import NormalizedJob
from app.schemas.resume import NormalizedResume


SchemaModel = TypeVar("SchemaModel", bound=BaseModel)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


class OpenAIExtractionError(RuntimeError):
    """Raised when structured extraction fails."""


class OpenAIService:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self._model = settings.openai_model

    @property
    def enabled(self) -> bool:
        return self._client is not None

    async def normalize_job(self, job_text: str) -> NormalizedJob:
        return await self.extract_structured_output(
            prompt_name="normalize_job.txt",
            schema_name="normalized_job",
            schema_model=NormalizedJob,
            content=job_text,
        )

    async def normalize_resume(self, resume_text: str) -> NormalizedResume:
        return await self.extract_structured_output(
            prompt_name="normalize_resume.txt",
            schema_name="normalized_resume",
            schema_model=NormalizedResume,
            content=resume_text,
        )

    async def extract_structured_output(
        self,
        *,
        prompt_name: str,
        schema_name: str,
        schema_model: type[SchemaModel],
        content: str,
    ) -> SchemaModel:
        if not self._client:
            raise OpenAIExtractionError("OPENAI_API_KEY is not configured.")

        prompt = load_prompt(prompt_name)
        schema = schema_model.model_json_schema()

        try:
            response = await self._client.responses.create(
                model=self._model,
                instructions=prompt,
                input=content,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "strict": True,
                        "schema": schema,
                    }
                },
            )
        except Exception as exc:  # pragma: no cover - network/API behavior
            raise OpenAIExtractionError(f"OpenAI extraction request failed: {exc}") from exc

        output_text = (response.output_text or "").strip()
        if not output_text:
            raise OpenAIExtractionError("OpenAI extraction returned empty structured output.")

        try:
            payload = json.loads(output_text)
            return schema_model.model_validate(payload)
        except Exception as exc:
            raise OpenAIExtractionError("OpenAI extraction returned invalid structured JSON.") from exc


def load_prompt(prompt_name: str) -> str:
    return (PROMPTS_DIR / prompt_name).read_text(encoding="utf-8")
