import { useState } from "react";

const API_BASE = "http://localhost:8000/api";

const defaultVlanConfig = {
  device: "SW1",
  configured_vlans: { 10: "Students", 30: "Guests" },
  expected_vlans: { 10: "Students", 20: "Faculty", 30: "Guests" },
  trunk_allowed_vlans: [10, 30],
};

const defaultIpConfig = {
  device: "PC1",
  ip_address: "192.168.20.15",
  subnet_mask: "255.255.255.0",
  gateway: "192.168.30.1",
};

const defaultRoutes = [
  { destination_network: "192.168.20.0/24", next_hop: "10.0.0.1", exists: false },
];

const defaultAclRules = [
  { action: "DENY", source: "Faculty", destination: "Server" },
];

export default function ProblemForm({ onDiagnosis }) {
  const [description, setDescription] = useState("Faculty cannot access the server.");
  const [vlanText, setVlanText] = useState(JSON.stringify(defaultVlanConfig, null, 2));
  const [ipText, setIpText] = useState(JSON.stringify(defaultIpConfig, null, 2));
  const [routesText, setRoutesText] = useState(JSON.stringify(defaultRoutes, null, 2));
  const [aclText, setAclText] = useState(JSON.stringify(defaultAclRules, null, 2));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        problem_description: description,
      };

      const vlanConfig = vlanText ? JSON.parse(vlanText) : null;
      const ipConfig = ipText ? JSON.parse(ipText) : null;
      const routes = routesText ? JSON.parse(routesText) : null;
      const aclRules = aclText ? JSON.parse(aclText) : null;

      if (vlanConfig) payload.vlan_config = vlanConfig;
      if (ipConfig) payload.ip_config = ipConfig;
      if (routes) payload.routes = routes;
      if (aclRules) payload.acl_rules = aclRules;

      const res = await fetch(`${API_BASE}/troubleshoot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed (${res.status})`);
      }

      const diagnosis = await res.json();
      onDiagnosis({ ...diagnosis, problem_description: description });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="panel" style={{ padding: 24 }}>
      <div style={{ display: "grid", gap: 18 }}>
        <div>
          <label className="field">
            <span className="field-label">Problem description</span>
            <textarea
              className="field-textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder='e.g. "Faculty cannot access the server"'
              required
            />
          </label>
        </div>

        <div className="form-grid">
          <label className="field">
            <span className="field-label">VLAN config JSON</span>
            <textarea className="field-textarea" value={vlanText} onChange={(e) => setVlanText(e.target.value)} />
          </label>

          <label className="field">
            <span className="field-label">IP config JSON</span>
            <textarea className="field-textarea" value={ipText} onChange={(e) => setIpText(e.target.value)} />
          </label>

          <label className="field">
            <span className="field-label">Routes JSON</span>
            <textarea className="field-textarea" value={routesText} onChange={(e) => setRoutesText(e.target.value)} />
          </label>

          <label className="field">
            <span className="field-label">ACL rules JSON</span>
            <textarea className="field-textarea" value={aclText} onChange={(e) => setAclText(e.target.value)} />
          </label>
        </div>

        <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <button type="submit" disabled={loading} className="primary-button">
            {loading ? "Analyzing..." : "Run Diagnosis"}
          </button>

          <button
            type="button"
            className="secondary-button"
            onClick={() => {
              setDescription("Faculty cannot access the server.");
              setVlanText(JSON.stringify(defaultVlanConfig, null, 2));
              setIpText(JSON.stringify(defaultIpConfig, null, 2));
              setRoutesText(JSON.stringify(defaultRoutes, null, 2));
              setAclText(JSON.stringify(defaultAclRules, null, 2));
            }}
          >
            Reset demo data
          </button>
        </div>

        {error && <p className="status-text">{error}</p>}
      </div>
    </form>
  );
}
