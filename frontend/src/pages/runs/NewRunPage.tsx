import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function NewRunPage() {
  const nav = useNavigate();

  const [clientName, setClientName] = useState("");
  const [environment, setEnvironment] = useState("prod");
  const [assessmentName, setAssessmentName] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const buildName = () => {
    const base = assessmentName.trim()
      ? assessmentName.trim()
      : `${clientName.trim() || "New client"} • ${environment.toUpperCase()}`;
    return base;
  };

  async function createRun() {
    setErr(null);
    setLoading(true);

    const payload = {
      name: buildName(),
      source: clientName.trim() || "Client",
      environment: environment,
    };

    try {
      // Attempt 1: send metadata (if backend ignores unknown keys, great)
      let res = await fetch("/v1/run_registry", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      // Attempt 2: fallback if backend expects empty POST
      if (!res.ok) {
        res = await fetch("/v1/run_registry", { method: "POST" });
      }

      if (!res.ok) {
        const t = await res.text().catch(() => "");
        throw new Error(`Create assessment failed (${res.status}): ${t}`);
      }

      const run = await res.json();

      // Store “nice” metadata client-side for MVP demo (until backend fields exist)
      const runId = run?.id;
      if (runId) {
        const key = `run_meta_${runId}`;
        localStorage.setItem(
          key,
          JSON.stringify({
            clientName: clientName.trim(),
            environment,
            assessmentName: buildName(),
            createdAt: new Date().toISOString(),
          })
        );
        nav(`/runs/${encodeURIComponent(runId)}`, { replace: true });
        return;
      }

      // if no run.id, go to Assessments list
      nav("/runs", { replace: true });
    } catch (e: any) {
      setErr(e?.message || "Failed to create assessment.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="px-6 py-6 max-w-3xl">
      <div className="mb-4">
        <h1 className="text-xl font-semibold text-gray-900">Start a new assessment</h1>
        <p className="text-sm text-gray-600">
          Capture basic client context so the demo flow starts clean.
        </p>
      </div>

      <div className="border border-gray-200 bg-white rounded-xl shadow-sm p-5 space-y-4">
        <div>
          <label className="block text-xs font-medium text-gray-700">Client name</label>
          <input
            value={clientName}
            onChange={(e) => setClientName(e.target.value)}
            placeholder="Acme Health"
            className="mt-1 w-full"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-700">Environment</label>
          <select
            value={environment}
            onChange={(e) => setEnvironment(e.target.value)}
            className="mt-1 w-full"
          >
            <option value="prod">Production</option>
            <option value="nonprod">Non-Production</option>
            <option value="dev">Dev</option>
            <option value="test">Test</option>
            <option value="stage">Stage</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-700">
            Assessment name (optional)
          </label>
          <input
            value={assessmentName}
            onChange={(e) => setAssessmentName(e.target.value)}
            placeholder="Acme • Q1 Migration Assessment"
            className="mt-1 w-full"
          />
          <p className="text-[11px] text-gray-500 mt-1">
            If blank, we’ll use: <span className="font-medium">{buildName()}</span>
          </p>
        </div>

        {err && (
          <div className="border border-red-200 bg-red-50 text-red-700 text-sm px-3 py-2 rounded">
            {err}
          </div>
        )}

        <div className="flex items-center gap-3">
          <button
            onClick={() => nav("/runs")}
            className="px-3 py-2 rounded-md border border-gray-200 text-sm hover:bg-gray-50"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            onClick={createRun}
            className="px-3 py-2 rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60"
            disabled={loading || !clientName.trim()}
          >
            {loading ? "Creating..." : "Create assessment"}
          </button>
        </div>
      </div>
    </div>
  );
}
