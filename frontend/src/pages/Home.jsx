import { useState } from "react";

import { analyzeApplication, respondToClarification } from "../api/client";
import AnalyzeButton from "../components/AnalyzeButton";
import JobInput from "../components/JobInput";
import ResultsPanel from "../components/ResultsPanel";
import ResumeUpload from "../components/ResumeUpload";

export default function Home() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobUrl, setJobUrl] = useState("");
  const [jobText, setJobText] = useState("");
  const [result, setResult] = useState(null);
  const [finalResult, setFinalResult] = useState(null);
  const [clarificationAnswer, setClarificationAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [responding, setResponding] = useState(false);
  const [error, setError] = useState("");

  const canAnalyze = Boolean(resumeFile && (jobUrl.trim() || jobText.trim()));

  async function handleAnalyze() {
    if (!canAnalyze) {
      setError("Upload a resume PDF and provide either a job URL or pasted job text.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setFinalResult(null);
      const payload = await analyzeApplication({ resumeFile, jobUrl, jobText });
      setResult(payload);
    } catch (requestError) {
      setError(requestError.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRespond() {
    if (!result?.session_id) {
      setError("Analyze the application before submitting a clarification answer.");
      return;
    }

    if (!clarificationAnswer.trim()) {
      setError("Add a clarification answer before generating the final output.");
      return;
    }

    try {
      setResponding(true);
      setError("");
      const payload = await respondToClarification({
        sessionId: result.session_id,
        answer: clarificationAnswer,
      });
      setFinalResult(payload);
    } catch (requestError) {
      setError(requestError.message || "Something went wrong.");
    } finally {
      setResponding(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">HireFlow</p>
          <h1>Voice-guided resume tailoring for ambitious job applications.</h1>
          <p className="hero-text">
            Upload a resume, point the agent at a job posting, and generate a cleaner, better
            aligned version with structured analysis, follow-up questions, and voice-guided output.
          </p>
        </div>
      </section>

      <section className="workspace">
        <div className="composer-column">
          <ResumeUpload file={resumeFile} onChange={setResumeFile} />
          <JobInput
            jobUrl={jobUrl}
            jobText={jobText}
            onJobUrlChange={setJobUrl}
            onJobTextChange={setJobText}
          />

          <div className="action-row">
            <AnalyzeButton disabled={!canAnalyze} loading={loading} onClick={handleAnalyze} />
            {error ? <p className="error-text">{error}</p> : null}
          </div>
        </div>

        <ResultsPanel
          result={result}
          finalResult={finalResult}
          clarificationAnswer={clarificationAnswer}
          onClarificationAnswerChange={setClarificationAnswer}
          onRespond={handleRespond}
          responding={responding}
        />
      </section>
    </main>
  );
}
