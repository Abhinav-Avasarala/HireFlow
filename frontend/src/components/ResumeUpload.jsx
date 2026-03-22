import FieldLabel from "./FieldLabel";

export default function ResumeUpload({ file, onChange }) {
  return (
    <label className="panel input-panel upload-panel">
      <FieldLabel hint="PDF only">Resume</FieldLabel>
      <div className="upload-box">
        <div>
          <strong>{file ? file.name : "Drop in your resume PDF"}</strong>
          <p>
            Start with a single resume. We will parse it, analyze gaps, and regenerate a cleaner
            ATS-friendly version later in the flow.
          </p>
        </div>
        <span className="pill">{file ? "Ready" : "Upload"}</span>
      </div>
      <input
        className="visually-hidden"
        type="file"
        accept="application/pdf"
        onChange={(event) => onChange(event.target.files?.[0] || null)}
      />
    </label>
  );
}
