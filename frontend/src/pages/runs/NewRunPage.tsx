import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function NewRunPage() {
  const [label, setLabel] = useState("");
  const [environment, setEnvironment] = useState("prod");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage(null);
    setError(null);

    const payload = {
      label: label || "New CloudReadyAI assessment",
      environment,
    };

    try {
      const res = await fetch("/v1/runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      // Backend might not be wired yet; handle that gracefully.
      let data: any = {};
      try {
        data = await res.json();
      } catch {
        // ignore JSON parse errors; this is expected if the API returns HTML/empty
      }

      if (!res.ok) {
        throw new Error(
          data?.detail ||
            `Backend responded with HTTP ${res.status}. /v1/runs POST may not be implemented yet.`
        );
      }

      const newId: string = data?.id || "(check backend logs for ID)";
      setMessage(`Run created successfully with id ${newId}.`);

      // For now, route back to /runs; later we can deep-link into portfolio.
      navigate("/runs");
    } catch (err: any) {
      console.error("Error creating run:", err);
      setError(
        err?.message ||
          "Unable to create run. This is expected if POST /v1/runs is not live yet."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="panel p-4">
        <h1 className="text-2xl font-semibold mb-1">New Assessment</h1>
        <p className="text-sm text-[var(--text-muted)]">
          This is the Phase A/B entry point into CloudReadyAI. In later phases
          this will drive ingestion, diagrams, portfolio, and cost views for a
          single run.
        </p>
      </section>

      <section className="panel p-4 max-w-xl">
        <h2 className="text-lg font-semibold mb-3">Assessment Details</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium">
              Assessment name (optional)
            </label>
            <input
              type="text"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder="e.g., USDA-ASSESS-FY25 baseline"
            />
            <p className="text-xs text-[var(--text-muted)]">
              If left blank, CloudReadyAI will use a default label.
            </p>
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium">Environment</label>
            <select
              value={environment}
              onChange={(e) => setEnvironment(e.target.value)}
            >
              <option value="prod">Production</option>
              <option value="nonprod">Non-Production</option>
              <option value="lab">Lab / POC</option>
            </select>
          </div>

          {message && (
            <div className="text-sm text-green-700 bg-green-50 border border-green-200 rounded-md px-3 py-2">
              {message}
            </div>
          )}

          {error && (
            <div className="text-sm text-red-700 bg-red-50 border border-red-200 rounded-md px-3 py-2">
              {error}
            </div>
          )}

          <div className="pt-2">
            <button
              type="submit"
              className="btn-primary px-4 py-2"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Creating Run…" : "Create Run"}
            </button>
          </div>

          <p className="text-xs text-[var(--text-muted)] mt-2">
            Today this is a thin wrapper around <code>POST /v1/runs</code>.
            Once the backend contracts are finalized, it will automatically
            kick off Phase B ingestion and wire into diagrams, portfolio, and
            cost/tCO flows.
          </p>
        </form>
      </section>
    </div>
  );
}
