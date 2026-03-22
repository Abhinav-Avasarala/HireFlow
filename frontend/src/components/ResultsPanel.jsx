function ScorePill({ label, value }) {
  return (
    <div className="score-pill">
      <span>{label}</span>
      <strong>{value}%</strong>
    </div>
  );
}

function FinalScorePill({ label, value }) {
  return (
    <div className="score-pill final">
      <span>{label}</span>
      <strong>{value}%</strong>
    </div>
  );
}

export default function ResultsPanel({
  result,
  finalResult,
  clarificationAnswer,
  onClarificationAnswerChange,
  onRespond,
  responding,
}) {
  if (!result) {
    return (
      <section className="panel results-panel empty-state">
        <p className="eyebrow">Analysis Output</p>
        <h2>Results appear here after the first analysis run.</h2>
        <p>
          The first iteration returns structured mock analysis so we can lock the frontend and API
          contract before integrating Firecrawl, resume parsing, and voice.
        </p>
      </section>
    );
  }

  return (
    <section className="panel results-panel">
      <div className="results-header">
        <div>
          <p className="eyebrow">Analysis Output</p>
          <h2>Initial fit snapshot for {result.resume_filename}</h2>
        </div>
        <span className="pill subtle">{result.job_source === "url" ? "URL input" : "Text input"}</span>
      </div>

      <div className="score-grid">
        <ScorePill label="Skills" value={result.match_score.skills} />
        <ScorePill label="Keywords" value={result.match_score.keywords} />
        <ScorePill label="Overall" value={result.match_score.overall} />
      </div>

      <div className="results-block">
        <h3>Job Summary</h3>
        <p>{result.job_summary}</p>
      </div>

      <div className="results-columns">
        <div className="results-block">
          <h3>Top Matches</h3>
          <ul className="clean-list">
            {result.top_matches.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="results-block">
          <h3>Gaps To Close</h3>
          <ul className="clean-list">
            {result.gaps.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="results-block">
        <h3>Clarification Questions</h3>
        <div className="question-list">
          {result.clarification_questions.map((question) => (
            <article className="question-card" key={question.id}>
              <p>{question.text}</p>
              <span>{question.rationale}</span>
            </article>
          ))}
        </div>
      </div>

      <div className="results-block">
        <h3>Clarification Response</h3>
        <div className="respond-panel">
          <textarea
            className="text-area clarification-area"
            placeholder="Answer the clarification questions here. Include concrete tools, scope, and metrics if you have them."
            rows={5}
            value={clarificationAnswer}
            onChange={(event) => onClarificationAnswerChange(event.target.value)}
          />
          <button className="secondary-button" type="button" onClick={onRespond} disabled={responding}>
            {responding ? "Generating..." : "Generate Final Output"}
          </button>
        </div>
      </div>

      {finalResult ? (
        <div className="final-output">
          <div className="results-block">
            <h3>Updated Score</h3>
            <div className="score-grid">
              <FinalScorePill label="Skills" value={finalResult.updated_score.skills} />
              <FinalScorePill label="Keywords" value={finalResult.updated_score.keywords} />
              <FinalScorePill label="Overall" value={finalResult.updated_score.overall} />
            </div>
          </div>

          <div className="results-columns">
            <div className="results-block">
              <h3>Optimized Summary</h3>
              <p>{finalResult.optimized_resume.summary}</p>
            </div>

            <div className="results-block">
              <h3>Priority Skills</h3>
              <ul className="clean-list">
                {finalResult.optimized_resume.key_skills.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="results-columns">
            <div className="results-block">
              <h3>Bullet Updates</h3>
              <ul className="clean-list">
                {finalResult.optimized_resume.bullet_updates.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="results-block">
              <h3>Changes Explained</h3>
              <ul className="clean-list">
                {finalResult.changes_explained.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="results-columns">
            <div className="results-block">
              <h3>Career Strategy</h3>
              <ul className="clean-list">
                {finalResult.career_strategy.missing_skills.map((item) => (
                  <li key={item}>Missing skill to target: {item}</li>
                ))}
                {finalResult.career_strategy.project_suggestions.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="results-block">
              <h3>Networking Suggestion</h3>
              <p>{finalResult.career_strategy.networking_suggestion}</p>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
