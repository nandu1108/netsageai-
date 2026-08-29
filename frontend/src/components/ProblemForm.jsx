import { useState } from "react";

const API_BASE = "http://localhost:8000/api";

/**
 * Basic problem-submission form. Extend this to conditionally show
 * VLAN / IP / routing / ACL input sections depending on what data
 * the user has available, per the project brief's input types.
 */
export default function ProblemForm({ onDiagnosis }) {
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/troubleshoot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          problem_description: description,
          // TODO: attach vlan_config / ip_config / routes / acl_rules
          // from additional form fields as the UI grows.
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed (${res.status})`);
      }

      const diagnosis = await res.json();
      onDiagnosis(diagnosis);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-xl">
      <label className="block">
        <span className="text-sm font-medium text-gray-700">
          Describe the problem
        </span>
        <textarea
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder='e.g. "Faculty cannot access server"'
          required
        />
      </label>

      {/* TODO: add structured inputs for VLAN config, IP config,
          routing table, and ACL rules so users without raw configs
          can still describe the topology manually. */}

      <button
        type="submit"
        disabled={loading}
        className="rounded-md bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
      >
        {loading ? "Analyzing..." : "Run Diagnosis"}
      </button>

      {error && <p className="text-red-600 text-sm">{error}</p>}
    </form>
  );
}
