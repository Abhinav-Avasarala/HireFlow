export default function FieldLabel({ children, hint }) {
  return (
    <div className="field-label">
      <span>{children}</span>
      {hint ? <span className="field-hint">{hint}</span> : null}
    </div>
  );
}
