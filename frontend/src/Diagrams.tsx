import { useState } from "react";

export default function Diagrams() {
  const [cloud, setCloud] = useState("aws");
  const [diagramType, setDiagramType] = useState("landing_zone");
  const [orgName, setOrgName] = useState("");
  const [environment, setEnvironment] = useState("");
  const [workloadName, setWorkloadName] = useState("");
  const [xml, setXml] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const diagramTypesForCloud: Record<string, string[]> = {
    aws: ["landing_zone", "dr_topology"],
    azure: ["hub_spoke", "dr_topology"],
    gcp: ["shared_vpc", "dr_topology"],
  };

  const handleCloudChange = (value: string) => {
    setCloud(value);
    setDiagramType(diagramTypesForCloud[value][0]);
  };

  const generateDiagram = async () => {
    setLoading(true);
    setError("");
    setXml("");

    const payload: Record<string, string> = {
      cloud,
      diagram_type: diagramType,
    };

    if (orgName) payload.org_name = orgName;
    if (environment) payload.environment = environment;
    if (workloadName) payload.workload_name = workloadName;

    try {
      const res = await fetch("http://localhost:8000/v1/diagram/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`Backend error ${res.status}`);
      }

      const data = await res.json();
      setXml(data.xml);
    } catch (err: any) {
      setError(err.message || "Unknown error");
    }

    setLoading(false);
  };

  const downloadDrawio = () => {
    if (!xml) return;
    const blob = new Blob([xml], { type: "application/xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${cloud}-${diagramType}.drawio`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", maxWidth: 900, margin: "0 auto" }}>
      <h1>CloudReadyAI — Diagram Generator</h1>

      <div style={{ marginBottom: "1.5rem" }}>
        <label>Cloud:</label>
        <select value={cloud} onChange={(e) => handleCloudChange(e.target.value)} style={{ marginLeft: 8 }}>
          <option value="aws">AWS</option>
          <option value="azure">Azure</option>
          <option value="gcp">GCP</option>
        </select>
      </div>

      <div style={{ marginBottom: "1.5rem" }}>
        <label>Diagram Type:</label>
        <select
          value={diagramType}
          onChange={(e) => setDiagramType(e.target.value)}
          style={{ marginLeft: 8 }}
        >
          {diagramTypesForCloud[cloud].map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label>Organization Name (optional):</label>
        <input value={orgName} onChange={(e) => setOrgName(e.target.value)} style={{ marginLeft: 8 }} />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label>Environment (optional):</label>
        <input value={environment} onChange={(e) => setEnvironment(e.target.value)} style={{ marginLeft: 8 }} />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label>Workload Name (optional):</label>
        <input value={workloadName} onChange={(e) => setWorkloadName(e.target.value)} style={{ marginLeft: 8 }} />
      </div>

      <button onClick={generateDiagram} disabled={loading} style={{ marginRight: 16 }}>
        {loading ? "Generating..." : "Generate"}
      </button>

      <button onClick={downloadDrawio} disabled={!xml}>
        Download .drawio
      </button>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {xml && (
        <div style={{ marginTop: "2rem" }}>
          <h3>Generated XML</h3>
          <textarea value={xml} readOnly rows={20} style={{ width: "100%" }} />
        </div>
      )}
    </div>
  );
}
