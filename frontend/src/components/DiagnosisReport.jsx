const API_BASE = "http://localhost:8000/api";

export default function DiagnosisReport({ diagnosis, problemDescription, onReviewSubmit }) {
  if (!diagnosis) return null;

  const confidenceColor =
    diagnosis.confidence >= 85
      ? "#166534"
      : diagnosis.confidence >= 60
      ? "#92400e"
      : "#b91c1c";

  async function submitReview(verdict) {
    const payload = {
      diagnosis_id: `diag-${Date.now()}`,
      problem_description: problemDescription || diagnosis.problem_description || diagnosis.issue,
      ai_prediction_summary: diagnosis.root_cause,
      confidence: diagnosis.confidence,
      verdict,
    };

    await fetch(`${API_BASE}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (onReviewSubmit) {
      await onReviewSubmit();
    }

    alert(`Human review recorded: ${verdict}. The fix is not accepted until a reviewer signs off.`);
  }

  return (
    <div className="panel" style={{ padding: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <h2 style={{ margin: 0, fontSize: "1.35rem" }}>{diagnosis.issue}</h2>
        <span style={{ color: confidenceColor, fontWeight: 700 }}>
          {diagnosis.confidence}% confidence
        </span>
      </div>

      <div style={{ marginTop: 16, display: "grid", gap: 14 }}>
        <div>
          <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#475569", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Affected Layer
          </div>
          <div>{diagnosis.affected_layer}</div>
        </div>

        <div>
          <h3 style={{ margin: "0 0 8px" }}>Root Cause</h3>
          <p style={{ margin: 0, color: "#334155" }}>{diagnosis.root_cause}</p>
        </div>

        <div>
          <h3 style={{ margin: "0 0 8px" }}>Recommended Fix</h3>
          <p style={{ margin: 0, color: "#334155" }}>{diagnosis.recommended_fix}</p>
        </div>

        <div>
          <h3 style={{ margin: "0 0 8px" }}>Verification Steps</h3>
          <ol style={{ margin: 0, paddingLeft: 20, color: "#334155" }}>
            {diagnosis.verification_steps.map((step, i) => (
              <li key={i} style={{ marginBottom: 6 }}>{step}</li>
            ))}
          </ol>
        </div>

        {diagnosis.source_snippets?.length > 0 && (
          <div>
            <h3 style={{ margin: "0 0 8px" }}>Source Snippets</h3>
            <ul style={{ margin: 0, paddingLeft: 20, color: "#334155" }}>
              {diagnosis.source_snippets.map((snippet, i) => (
                <li key={i} style={{ marginBottom: 6 }}>{snippet}</li>
              ))}
            </ul>
          </div>
        )}

        <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: 14 }}>
          <h3 style={{ margin: "0 0 8px" }}>Human review</h3>
          <p style={{ margin: "0 0 12px", color: "#334155" }}>
            A human must review every diagnosis before a fix is accepted.
          </p>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button type="button" className="feedback-button" onClick={() => submitReview("Correct")}>Accept</button>
            <button type="button" className="secondary-button" onClick={() => submitReview("Partially Correct")}>Edit</button>
            <button type="button" className="secondary-button" onClick={() => submitReview("Wrong")}>Reject</button>
          </div>
        </div>
      </div>
    </div>
  );
}
