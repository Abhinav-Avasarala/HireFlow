import logging
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.analysis import AnalysisResponse
from app.schemas.job import NormalizedJob
from app.schemas.resume import NormalizedResume
from app.services.analysis_service import AnalysisService
from app.services.firecrawl_service import FirecrawlError, FirecrawlService
from app.services.gap_analysis import (
    build_analysis,
    parse_job_text,
    parse_normalized_job,
    parse_normalized_resume,
    parse_resume_text,
    to_normalized_job,
    to_normalized_resume,
)
from app.services.openai_service import OpenAIExtractionError, OpenAIService
from app.services.resume_parser import ResumeParseError, ResumeParser
from app.services.session_store import AnalysisSession, session_store


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["analysis"])
firecrawl_service = FirecrawlService()
openai_service = OpenAIService()
analysis_service = AnalysisService(openai_service)
resume_parser = ResumeParser()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    resume_pdf: UploadFile = File(...),
    job_url: str | None = Form(default=None),
    job_text: str | None = Form(default=None),
) -> AnalysisResponse:
    if not job_url and not job_text:
        raise HTTPException(status_code=400, detail="Provide either job_url or job_text.")

    if resume_pdf.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Resume upload must be a PDF.")

    job_source = "url" if job_url else "text"
    resume_bytes = await resume_pdf.read()

    try:
        resume_text = resume_parser.extract_text(resume_bytes)
    except ResumeParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    metadata_keywords: list[str] = []
    source_summary = ""
    if job_url:
        try:
            scrape_result = await firecrawl_service.scrape_job_posting(job_url.strip())
        except FirecrawlError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        job_content = scrape_result.markdown
        metadata_keywords = scrape_result.keywords
        source_summary = scrape_result.description or scrape_result.title or scrape_result.source_url
    else:
        job_content = (job_text or "").strip()
        source_summary = normalize_summary(job_content)

    normalized_job: NormalizedJob | None = None
    normalized_resume: NormalizedResume | None = None
    analysis_status = "analyzed-fallback"
    if openai_service.enabled:
        try:
            normalized_job = await openai_service.normalize_job(job_content)
            normalized_resume = await openai_service.normalize_resume(resume_text)
            job = parse_normalized_job(normalized_job)
            resume = parse_normalized_resume(normalized_resume)
            analysis_status = "normalized-llm"
        except OpenAIExtractionError:
            logger.exception("OpenAI normalization failed; using fallback parsing.")
            job = parse_job_text(job_content, metadata_keywords=metadata_keywords)
            resume = parse_resume_text(resume_text)
            normalized_job = to_normalized_job(job)
            normalized_resume = to_normalized_resume(resume)
    else:
        job = parse_job_text(job_content, metadata_keywords=metadata_keywords)
        resume = parse_resume_text(resume_text)
        normalized_job = to_normalized_job(job)
        normalized_resume = to_normalized_resume(resume)

    if openai_service.enabled and normalized_job and normalized_resume:
        try:
            llm_analysis = await analysis_service.analyze_fit(
                normalized_job=normalized_job,
                normalized_resume=normalized_resume,
            )
            analysis_job_summary = llm_analysis.job_summary or job.summary or source_summary
            analysis_top_matches = llm_analysis.top_matches
            analysis_gaps = llm_analysis.gaps
            analysis_score = llm_analysis.match_score
            analysis_questions = llm_analysis.clarification_questions
            analysis_status = "analyzed-llm"
        except OpenAIExtractionError:
            logger.exception("OpenAI fit analysis failed; using fallback analysis.")
            fallback_analysis = build_analysis(job, resume)
            analysis_job_summary = job.summary or source_summary
            analysis_top_matches = fallback_analysis.top_matches
            analysis_gaps = fallback_analysis.gaps
            analysis_score = fallback_analysis.match_score
            analysis_questions = fallback_analysis.clarification_questions
    else:
        fallback_analysis = build_analysis(job, resume)
        analysis_job_summary = job.summary or source_summary
        analysis_top_matches = fallback_analysis.top_matches
        analysis_gaps = fallback_analysis.gaps
        analysis_score = fallback_analysis.match_score
        analysis_questions = fallback_analysis.clarification_questions

    response = AnalysisResponse(
        session_id=str(uuid4()),
        job_source=job_source,
        resume_filename=resume_pdf.filename or "resume.pdf",
        status=analysis_status,
        job_summary=analysis_job_summary,
        top_matches=analysis_top_matches,
        gaps=analysis_gaps,
        match_score=analysis_score,
        clarification_questions=analysis_questions,
    )
    session_store.save(
        AnalysisSession(
            session_id=response.session_id,
            analysis=response,
            normalized_job=normalized_job,
            normalized_resume=normalized_resume,
            raw_job_text=job_content,
            raw_resume_text=resume_text,
        )
    )
    return response


def normalize_summary(text: str, limit: int = 180) -> str:
    compact = " ".join(text.split())
    return compact[:limit]
