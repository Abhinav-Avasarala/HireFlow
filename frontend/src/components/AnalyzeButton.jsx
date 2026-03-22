export default function AnalyzeButton({ disabled, loading, onClick }) {
  return (
    <button className="analyze-button" type="button" disabled={disabled || loading} onClick={onClick}>
      <span>{loading ? "Analyzing" : "Analyze Application"}</span>
      <span className="button-accent">{loading ? "..." : "Now"}</span>
    </button>
  );
}
