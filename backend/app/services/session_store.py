from __future__ import annotations

from dataclasses import dataclass

from app.schemas.analysis import AnalysisResponse
from app.schemas.job import NormalizedJob
from app.schemas.resume import NormalizedResume


@dataclass
class AnalysisSession:
    session_id: str
    analysis: AnalysisResponse
    normalized_job: NormalizedJob | None
    normalized_resume: NormalizedResume | None
    raw_job_text: str
    raw_resume_text: str


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, AnalysisSession] = {}

    def save(self, session: AnalysisSession) -> None:
        self._sessions[session.session_id] = session

    def get(self, session_id: str) -> AnalysisSession | None:
        return self._sessions.get(session_id)


session_store = SessionStore()
