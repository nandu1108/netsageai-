/**
 * Renders the structured Diagnosis object returned by POST /api/troubleshoot.
 * Shape (see backend/app/models/schemas.py -> Diagnosis):
 * {
 *   issue, affected_layer, root_cause, confidence,
 *   recommended_fix, verification_steps: [], source_snippets: []
 * }
 */
export default function DiagnosisReport({ diagnosis }) {
  if (!diagnosis) return null;

  const confidenceColor =
    diagnosis.confidence >= 85
      ? "text-green-600"
      : diagnosis.confidence >= 60
      ? "text-yellow-600"
      : "text-red-600";

  return (
    <div className="rounded-lg border p-6 max-w-xl space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{diagnosis.issue}</h2>
        <span className={`font-medium ${confidenceColor}`}>
          {diagnosis.confidence}% confidence
        </span>
      </div>

      <p className="text-sm text-gray-500">
        Affected Layer: {diagnosis.affected_layer}
      </p>

      <div>
        <h3 className="font-medium">Root Cause</h3>
        <p className="text-sm">{diagnosis.root_cause}</p>
      </div>

      <div>
        <h3 className="font-medium">Recommended Fix</h3>
        <p className="text-sm">{diagnosis.recommended_fix}</p>
      </div>

      <div>
        <h3 className="font-medium">Verification Steps</h3>
        <ol className="list-decimal list-inside text-sm space-y-1">
          {diagnosis.verification_steps.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      </div>

      {/* TODO: wire up Correct / Partially Correct / Wrong buttons here,
          POSTing to /api/feedback per the Feedback Learning System feature. */}
    </div>
  );
}
