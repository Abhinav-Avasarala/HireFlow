import FieldLabel from "./FieldLabel";

export default function JobInput({ jobUrl, jobText, onJobUrlChange, onJobTextChange }) {
  return (
    <div className="input-stack">
      <div className="panel input-panel">
        <FieldLabel hint="Preferred">Job URL</FieldLabel>
        <input
          className="text-input"
          type="url"
          placeholder="https://company.com/jobs/role"
          value={jobUrl}
          onChange={(event) => onJobUrlChange(event.target.value)}
        />
      </div>

      <div className="or-divider">
        <span>or</span>
      </div>

      <div className="panel input-panel">
        <FieldLabel hint="Fallback">Pasted Job Description</FieldLabel>
        <textarea
          className="text-area"
          placeholder="Paste the job description here if you do not have a URL."
          rows={8}
          value={jobText}
          onChange={(event) => onJobTextChange(event.target.value)}
        />
      </div>
    </div>
  );
}
