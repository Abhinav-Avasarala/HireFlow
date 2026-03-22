from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from app.schemas.analysis import ClarificationQuestion, MatchScore
from app.schemas.job import NormalizedJob
from app.schemas.resume import NormalizedResume, ResumeExperienceEntry


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "that",
    "the",
    "their",
    "this",
    "to",
    "with",
    "you",
    "your",
    "will",
    "we",
    "us",
}

COMMON_SKILLS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "node",
    "nodejs",
    "fastapi",
    "django",
    "flask",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "machine learning",
    "deep learning",
    "llm",
    "nlp",
    "pytorch",
    "tensorflow",
    "cuda",
    "distributed systems",
    "microservices",
    "rest",
    "graphql",
    "git",
    "linux",
    "ci/cd",
    "terraform",
    "spark",
    "airflow",
}


@dataclass
class ParsedJob:
    summary: str
    responsibilities: list[str]
    keywords: list[str]
    skills: list[str]


@dataclass
class ParsedResume:
    summary: str
    highlights: list[str]
    skills: list[str]
    raw_text: str


@dataclass
class AnalysisBundle:
    job: ParsedJob
    resume: ParsedResume
    top_matches: list[str]
    gaps: list[str]
    match_score: MatchScore
    clarification_questions: list[ClarificationQuestion]


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_lines(text: str) -> list[str]:
    return [line.strip(" -*\t") for line in text.splitlines() if line.strip()]


def extract_keywords(text: str, limit: int = 12) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9\+\#\-/]{2,}", text.lower())
    filtered = [token for token in tokens if token not in STOP_WORDS]
    counts = Counter(filtered)
    return [token for token, _ in counts.most_common(limit)]


def extract_known_skills(text: str) -> list[str]:
    lowered = text.lower()
    found = [skill for skill in COMMON_SKILLS if skill in lowered]
    return sorted(set(found))


def extract_bullets(text: str, limit: int = 8) -> list[str]:
    bullets = [line for line in split_lines(text) if len(line.split()) >= 5]
    return bullets[:limit]


def parse_job_text(text: str, metadata_keywords: list[str] | None = None) -> ParsedJob:
    bullets = extract_bullets(text, limit=10)
    responsibilities = bullets[:5]
    summary_source = responsibilities[0] if responsibilities else normalize_whitespace(text[:320])
    skills = extract_known_skills(text)
    keywords = list(dict.fromkeys((metadata_keywords or []) + extract_keywords(text)))
    return ParsedJob(
        summary=summary_source,
        responsibilities=responsibilities,
        keywords=keywords[:14],
        skills=skills,
    )


def parse_resume_text(text: str) -> ParsedResume:
    lines = split_lines(text)
    summary = " ".join(lines[:3]) if lines else ""
    return ParsedResume(
        summary=normalize_whitespace(summary)[:320],
        highlights=extract_bullets(text, limit=6),
        skills=extract_known_skills(text),
        raw_text=text,
    )


def parse_normalized_job(job: NormalizedJob) -> ParsedJob:
    skills = list(
        dict.fromkeys(
            [item.strip() for item in job.required_skills + job.preferred_skills if item.strip()]
        )
    )
    keywords = list(dict.fromkeys([item.strip() for item in job.keywords if item.strip()]))
    responsibilities = [item.strip() for item in job.responsibilities if item.strip()]
    summary = job.summary.strip() or " ".join(responsibilities[:2]).strip()
    return ParsedJob(
        summary=summary,
        responsibilities=responsibilities[:6],
        keywords=keywords[:14],
        skills=skills,
    )


def parse_normalized_resume(resume: NormalizedResume) -> ParsedResume:
    highlight_lines: list[str] = []
    for entry in resume.experience:
        highlight_lines.extend([bullet.strip() for bullet in entry.bullets if bullet.strip()])
    for project in resume.projects:
        highlight_lines.extend([bullet.strip() for bullet in project.bullets if bullet.strip()])
    highlight_lines.extend([item.strip() for item in resume.achievements if item.strip()])

    raw_parts = [resume.summary]
    raw_parts.extend(highlight_lines)
    raw_parts.extend(resume.skills)
    raw_text = "\n".join(part for part in raw_parts if part).strip()

    return ParsedResume(
        summary=resume.summary.strip(),
        highlights=highlight_lines[:6],
        skills=list(dict.fromkeys([item.strip() for item in resume.skills if item.strip()])),
        raw_text=raw_text,
    )


def to_normalized_job(job: ParsedJob) -> NormalizedJob:
    return NormalizedJob(
        summary=job.summary,
        required_skills=job.skills,
        preferred_skills=[],
        keywords=job.keywords,
        responsibilities=job.responsibilities,
        qualifications=[],
    )


def to_normalized_resume(resume: ParsedResume) -> NormalizedResume:
    experience = []
    if resume.highlights:
        experience.append(
            ResumeExperienceEntry(
                role="Resume Experience",
                organization="",
                date_range="",
                bullets=resume.highlights[:6],
            )
        )

    return NormalizedResume(
        summary=resume.summary,
        skills=resume.skills,
        experience=experience,
        projects=[],
        education=[],
        achievements=resume.highlights[:6],
    )


def build_analysis(job: ParsedJob, resume: ParsedResume) -> AnalysisBundle:
    job_skill_set = set(job.skills)
    resume_skill_set = set(resume.skills)
    shared_skills = sorted(job_skill_set & resume_skill_set)
    missing_skills = sorted(job_skill_set - resume_skill_set)

    resume_text_lower = resume.raw_text.lower()
    matched_keywords = [keyword for keyword in job.keywords if keyword.lower() in resume_text_lower]
    missing_keywords = [keyword for keyword in job.keywords if keyword.lower() not in resume_text_lower]

    responsibilities_aligned = 0
    for responsibility in job.responsibilities:
        tokens = [token for token in extract_keywords(responsibility, limit=6) if len(token) > 3]
        if any(token in resume_text_lower for token in tokens):
            responsibilities_aligned += 1

    skills_score = round((len(shared_skills) / max(len(job_skill_set), 1)) * 100)
    keyword_score = round((len(matched_keywords) / max(len(job.keywords), 1)) * 100)
    responsibility_score = round((responsibilities_aligned / max(len(job.responsibilities), 1)) * 100)
    overall_score = round((skills_score * 0.5) + (keyword_score * 0.3) + (responsibility_score * 0.2))

    top_matches = []
    if shared_skills:
        top_matches.append(f"Aligned technical coverage across: {', '.join(shared_skills[:4])}.")
    if matched_keywords:
        top_matches.append(f"Resume already reflects high-signal keywords such as {', '.join(matched_keywords[:4])}.")
    if responsibilities_aligned:
        top_matches.append(f"{responsibilities_aligned} job responsibility areas already have related evidence in the resume.")
    if not top_matches:
        top_matches.append("Resume has enough raw content to support a targeted rewrite once key gaps are clarified.")

    gaps = []
    if missing_skills:
        gaps.append(f"Add or verify missing skills: {', '.join(missing_skills[:4])}.")
    if missing_keywords:
        gaps.append(f"Improve keyword coverage for terms like {', '.join(missing_keywords[:4])}.")
    if not re.search(r"\b\d+[%x\+]?|\$\d+|\b\d+\s?(ms|sec|hours|users|clients)\b", resume.raw_text.lower()):
        gaps.append("Experience bullets need stronger measurable outcomes or project metrics.")
    if not gaps:
        gaps.append("Main opportunity is phrasing and structure rather than major content gaps.")

    clarification_questions = [
        ClarificationQuestion(
            id="q1",
            text=(
                f"Do you have hands-on experience with {missing_skills[0]} or a similar tool that is missing from the current resume?"
                if missing_skills
                else "Is there one relevant tool, domain area, or responsibility from the job that you have done but did not list clearly on the resume?"
            ),
            rationale="This helps recover missing evidence for the highest-value requirement gap.",
        ),
        ClarificationQuestion(
            id="q2",
            text="Can you share one project or work bullet with a concrete metric, such as time saved, performance gain, or user impact?",
            rationale="Quantified outcomes improve both recruiter trust and ATS-quality rewriting.",
        ),
    ]

    return AnalysisBundle(
        job=job,
        resume=resume,
        top_matches=top_matches[:3],
        gaps=gaps[:3],
        match_score=MatchScore(skills=skills_score, keywords=keyword_score, overall=overall_score),
        clarification_questions=clarification_questions,
    )
