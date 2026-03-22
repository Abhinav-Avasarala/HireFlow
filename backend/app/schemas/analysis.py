from pydantic import BaseModel


class MatchScore(BaseModel):
    skills: int
    keywords: int
    overall: int


class ClarificationQuestion(BaseModel):
    id: str
    text: str
    rationale: str


class AnalysisResponse(BaseModel):
    session_id: str
    job_source: str
    resume_filename: str
    status: str
    job_summary: str
    top_matches: list[str]
    gaps: list[str]
    match_score: MatchScore
    clarification_questions: list[ClarificationQuestion]
