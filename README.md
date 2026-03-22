# HireFlow

HireFlow is a **Voice + Chat AI Career Agent** built for a 3-day hackathon. The product helps a user tailor their resume to a job posting, identify skill gaps, answer clarification questions, and generate a cleaner, more targeted resume.

The project is intentionally optimized for:

- clean UX
- minimal architecture
- strong demo flow
- visible use of **Firecrawl** and **ElevenLabs**

## Goal

Build a demo-ready system that can:

1. accept a resume PDF
2. accept a job posting URL or pasted job text
3. extract and structure the job posting
4. parse the resume
5. run a gap analysis
6. ask 1-2 smart clarification questions
7. accept text or voice responses
8. generate:
   - an ATS-optimized resume PDF
   - a match score
   - an explanation of changes
   - actionable career strategy
9. speak the clarification prompts and final summary using ElevenLabs

## Core Product Definition

This is **not** a generic chatbot.

This is an **agentic career workflow** that:

- analyzes a specific job posting
- compares it against a specific resume
- asks for missing context
- updates the resume strategically
- explains why the changes matter

## Required External Services

### Firecrawl

Must be used for:

- scraping job posting URLs
- extracting structured job content
- supporting real-time job data ingestion

### ElevenLabs

Must be used for:

- speaking clarification questions
- speaking final results
- optional user voice input flow

## Core User Flow

1. User uploads a resume PDF.
2. User enters a job posting:
   - preferred: job URL
   - fallback: pasted text
3. User clicks `Analyze`.
4. Backend:
   - uses Firecrawl for job extraction when URL is provided
   - parses the resume PDF into structured data
   - performs job-vs-resume gap analysis
5. Agent generates 1-2 targeted clarification questions.
6. Questions are shown as text and spoken with ElevenLabs.
7. User replies:
   - by text
   - or by voice
8. System generates:
   - ATS-optimized resume content
   - resume PDF via LaTeX
   - match score
   - explanation of changes
   - career strategy
9. Final results are displayed in text and summarized in voice.

## Demo-Critical Output

The demo must clearly show:

1. resume upload
2. Firecrawl-based job extraction from URL
3. gap analysis
4. agent clarification question in text + voice
5. user response in text or voice
6. optimized resume PDF
7. match score
8. final spoken summary

## Product Principles

- Keep it minimal.
- Prioritize end-to-end functionality over sophistication.
- Avoid features that do not improve the demo.
- Favor deterministic structure around AI outputs.
- Make Firecrawl and ElevenLabs visible in the demo story.

## MVP Scope

### In Scope

- single-user flow
- one resume upload at a time
- one job posting at a time
- URL scraping via Firecrawl
- pasted job description fallback
- PDF text extraction from resume
- structured resume parsing
- structured job parsing
- simple scoring
- 1-2 clarification questions
- text + voice output
- optional voice input if time permits
- LaTeX-based output resume PDF

### Out of Scope

- authentication
- multi-resume management
- database-heavy persistence
- advanced recruiter analytics
- multi-turn conversational memory beyond current session
- elaborate styling or design systems
- complex background job infrastructure

## Suggested Tech Stack

### Frontend

- React
- Vite
- simple CSS or a minimal component library

### Backend

- Python
- FastAPI
- Uvicorn

### AI / Orchestration

- OpenAI API for reasoning, extraction normalization, questions, and rewrite steps

### External APIs

- Firecrawl for job URL extraction
- ElevenLabs for text-to-speech and optional speech workflows

### Resume Processing

- PDF text extraction with `pdfplumber` or `pypdf`
- LaTeX template for final resume generation
- `pdflatex` for compiling PDF

## Clean Folder Structure

```text
HireFlow/
├── README.md
├── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── health.py
│   │   │   │   ├── analyze.py
│   │   │   │   ├── voice.py
│   │   │   │   └── resume.py
│   │   ├── schemas/
│   │   │   ├── job.py
│   │   │   ├── resume.py
│   │   │   ├── analysis.py
│   │   │   └── voice.py
│   │   ├── services/
│   │   │   ├── firecrawl_service.py
│   │   │   ├── elevenlabs_service.py
│   │   │   ├── openai_service.py
│   │   │   ├── resume_parser.py
│   │   │   ├── gap_analysis.py
│   │   │   ├── clarification_agent.py
│   │   │   ├── resume_optimizer.py
│   │   │   └── latex_generator.py
│   │   ├── prompts/
│   │   │   ├── extract_resume.txt
│   │   │   ├── analyze_gap.txt
│   │   │   ├── clarification.txt
│   │   │   ├── optimize_resume.txt
│   │   │   └── strategy.txt
│   │   ├── templates/
│   │   │   ├── resume.tex
│   │   │   └── generated/
│   │   ├── utils/
│   │   │   ├── files.py
│   │   │   ├── scoring.py
│   │   │   └── text.py
│   │   └── storage/
│   │       ├── uploads/
│   │       └── outputs/
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── components/
│   │   │   ├── ResumeUpload.jsx
│   │   │   ├── JobInput.jsx
│   │   │   ├── AnalyzeButton.jsx
│   │   │   ├── ClarificationCard.jsx
│   │   │   ├── MatchScoreCard.jsx
│   │   │   ├── StrategyCard.jsx
│   │   │   ├── ResumePreview.jsx
│   │   │   └── VoicePlayer.jsx
│   │   ├── pages/
│   │   │   └── Home.jsx
│   │   ├── styles/
│   │   │   └── app.css
│   │   └── types/
│   │       └── api.js
│   ├── package.json
│   └── README.md
└── docs/
    ├── api-contract.md
    ├── demo-script.md
    └── decisions.md
```

## Why This Structure

- `backend/app/services/` keeps external API integrations and domain logic separate.
- `schemas/` keeps request and response shapes predictable.
- `prompts/` keeps prompt text versioned and easy to tune during the hackathon.
- `templates/` isolates the LaTeX resume template from logic.
- `frontend/components/` maps directly to the demo flow, which keeps the UI easy to change quickly.
- `docs/` stores lightweight project memory so decisions do not get lost across iterations.

## Main Backend Modules

### 1. Job Extraction Module

Input:

- job URL or pasted text

Output:

- normalized job object:
  - title
  - company
  - summary
  - required skills
  - preferred skills
  - keywords
  - responsibilities
  - seniority

Notes:

- URL path must use Firecrawl.
- Pasted text path can skip Firecrawl and go directly to normalization.

### 2. Resume Parser

Input:

- uploaded resume PDF

Output:

- normalized resume object:
  - contact info
  - summary
  - skills
  - experience bullets
  - projects
  - education

### 3. Gap Analysis Module

Produces:

- missing skills
- missing keywords
- aligned strengths
- questionable or weak areas
- draft match score

### 4. Clarification Agent

Produces:

- 1-2 targeted follow-up questions

Question rules:

- only ask questions that can materially improve the resume
- prefer missing skills, tools, metrics, domain relevance, or project evidence
- keep questions concise

### 5. Resume Optimizer

Produces:

- revised summary
- revised bullets
- keyword-enriched skills section
- improved project phrasing

Rule:

- do not fabricate experience
- only strengthen, reframe, or incorporate clarified user information

### 6. PDF Generator

Produces:

- LaTeX file
- final PDF resume

### 7. Voice Module

Produces:

- spoken clarification question audio
- spoken final summary audio
- optional voice input handling

## Scoring System

Keep scoring simple and explainable:

- `skills_match`: overlap between required job skills and resume skills
- `keyword_match`: overlap between extracted keywords and resume content
- `overall_score`: weighted average

Suggested initial formula:

- skills match: 50%
- keyword match: 30%
- experience/responsibility alignment: 20%

This can be adjusted later, but should remain transparent for demo purposes.

## Minimal API Contract

### `POST /api/analyze`

Purpose:

- accept resume + job input
- return parsed analysis and clarification questions

Input:

- `resume_pdf`
- `job_url` or `job_text`

Response:

- parsed job
- parsed resume
- match score
- gaps
- clarification questions
- question audio URL(s)

### `POST /api/respond`

Purpose:

- accept user clarification response
- generate final outputs

Input:

- analysis/session id
- text response or transcribed voice response

Response:

- optimized resume data
- explanation of changes
- career advice
- final match score
- final audio summary URL
- generated PDF URL

### `POST /api/voice/transcribe`

Purpose:

- optional voice-input path

### `GET /api/resume/{file_id}`

Purpose:

- download generated PDF

### `GET /api/health`

Purpose:

- health check for demo readiness

## Recommended Build Order

Build in this order to reduce risk:

1. backend skeleton
2. Firecrawl job extraction
3. resume PDF text extraction
4. analysis endpoint returning structured JSON
5. clarification question generation
6. ElevenLabs text-to-speech
7. frontend upload/input/results flow
8. response step for optimized resume generation
9. LaTeX PDF generation
10. polish demo flow

## Step-by-Step Implementation Plan

### Phase 1: Foundation

1. Create backend and frontend scaffolding.
2. Add `.env.example` with all required API keys.
3. Add FastAPI app with health endpoint.
4. Add React app with a single-page layout.
5. Define shared JSON response shapes early.

### Phase 2: Core Analysis Path

1. Build Firecrawl integration for job URLs.
2. Add pasted text fallback for job descriptions.
3. Build resume PDF text extraction.
4. Normalize both resume and job data using structured AI prompts.
5. Implement gap analysis and match scoring.
6. Return clarification questions.

### Phase 3: Voice + Final Output

1. Add ElevenLabs text-to-speech for questions.
2. Build UI audio playback.
3. Add user response submission.
4. Generate optimized resume content.
5. Generate career strategy output.
6. Add ElevenLabs summary audio for final result.

### Phase 4: PDF Output + Demo Polish

1. Fill LaTeX resume template from structured optimized data.
2. Compile final PDF.
3. Expose PDF download endpoint.
4. Clean UI states for loading, error, and success.
5. Create demo script and sample assets.

## Practical 3-Day Plan

### Day 1

- scaffold project
- configure FastAPI + React
- implement Firecrawl job extraction
- implement resume PDF parsing
- return first structured analysis JSON

### Day 2

- implement gap analysis
- generate clarification questions
- integrate ElevenLabs for spoken questions
- build frontend flow for upload, analyze, and response

### Day 3

- implement resume optimization
- generate LaTeX PDF
- add final score + strategy + summary voice output
- test the full demo path
- polish copy and UI

## Environment Variables

Planned environment values:

```env
OPENAI_API_KEY=
FIRECRAWL_API_KEY=
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

Additional values can be added later if required.

## Definition of Done

The hackathon MVP is done when the following works end-to-end:

1. upload resume PDF
2. provide job URL
3. Firecrawl extracts the posting
4. resume and job are analyzed
5. clarification question is displayed and spoken
6. user submits response
7. system generates updated resume
8. PDF is downloadable
9. final summary is spoken

## Engineering Guidelines For This Project

- Keep functions small and explicit.
- Prefer typed schemas over loose dictionaries.
- Store prompts in files, not inline strings.
- Avoid premature abstraction.
- Stub fast, then replace with working integrations.
- Every new feature should support the demo path directly.

## Current Plan For Our Iterative Work

We will treat this `README.md` as the living project brief.

Whenever requirements change, we should update:

- scope
- folder structure
- API contract
- implementation order
- demo script assumptions

## Immediate Next Step

Start implementation with:

1. project scaffolding
2. backend FastAPI setup
3. frontend React setup
4. `.env.example`
5. first health and analyze endpoint stubs
