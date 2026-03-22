from fastapi import APIRouter, HTTPException

from app.schemas.respond import RespondRequest, RespondResponse
from app.services.gap_analysis import (
    parse_job_text,
    parse_resume_text,
    to_normalized_job,
    to_normalized_resume,
)
from app.services.openai_service import OpenAIService
from app.services.respond_service import RespondService
from app.services.session_store import session_store


router = APIRouter(prefix="/api", tags=["respond"])
openai_service = OpenAIService()
respond_service = RespondService(openai_service)


@router.post("/respond", response_model=RespondResponse)
async def respond_to_clarification(payload: RespondRequest) -> RespondResponse:
    session = session_store.get(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Run analysis again.")

    if not payload.answer.strip():
        raise HTTPException(status_code=400, detail="Clarification answer cannot be empty.")

    normalized_job = session.normalized_job
    normalized_resume = session.normalized_resume

    if not normalized_job or not normalized_resume:
        if openai_service.enabled:
            try:
                normalized_job = await openai_service.normalize_job(session.raw_job_text)
                normalized_resume = await openai_service.normalize_resume(session.raw_resume_text)
            except Exception:
                normalized_job = None
                normalized_resume = None

        if not normalized_job or not normalized_resume:
            normalized_job = to_normalized_job(parse_job_text(session.raw_job_text))
            normalized_resume = to_normalized_resume(parse_resume_text(session.raw_resume_text))

    optimized_resume, updated_score, changes, strategy = await respond_service.build_response(
        normalized_job=normalized_job,
        normalized_resume=normalized_resume,
        answer=payload.answer,
    )

    return RespondResponse(
        session_id=payload.session_id,
        status="responded",
        optimized_resume=optimized_resume,
        updated_score=updated_score,
        changes_explained=changes,
        career_strategy=strategy,
    )
