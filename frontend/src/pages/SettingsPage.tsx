import React, { useState } from "react";

type Theme = "light" | "dark" | "fiveNine";

export default function SettingsPage() {
  const [theme, setTheme] = useState<Theme>("fiveNine");
  const [healthChecking, setHealthChecking] = useState(false);
  const [healthResult, setHealthResult] = useState<string | null>(null);

  function applyTheme(next: Theme) {
    setTheme(next);
    const root = document.documentElement;

    // Simple theme hook – you can expand this later.
    if (next === "dark") {
      root.style.setProperty("--brand-bg-main", "#111827");
    } else if (next === "light") {
      root.style.setProperty("--brand-bg-main", "#f9fafb");
    } else {
      // 5NINE / default
      root.style.setProperty("--brand-bg-main", "#f6f6f5");
    }
  }

  async function checkHealth() {
    setHealthChecking(true);
    setHealthResult(null);
    try {
      const res = await fetch("/healthz");
      const text = await res.text();
      let parsed: any = null;
      try {
        parsed = JSON.parse(text);
      } catch {
        // not JSON, fine
      }

      if (!res.ok) {
        setHealthResult(
          parsed?.detail || text || `Health check failed: ${res.status}`,
        );
      } else {
        setHealthResult(
          parsed ? JSON.stringify(parsed, null, 2) : text || "OK",
        );
      }
    } catch (err: any) {
      setHealthResult(err?.message || "Unexpected error calling /healthz.");
    } finally {
      setHealthChecking(false);
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-gray-600 mt-1">
          Personalize the UI and check the health of your CloudReadyAI
          instance.
        </p>
      </header>

      {/* Theme */}
      <section className="panel p-6 space-y-3">
        <h2 className="text-lg font-semibold">Theme</h2>
        <p className="text-xs text-gray-600">
          Quick toggle for background tone. Colors are aligned with the 5NINE
          palette; you can refine this later.
        </p>
        <div className="flex flex-wrap gap-3 mt-2 text-sm">
          <button
            className={`px-4 py-2 border rounded-md ${
              theme === "fiveNine" ? "bg-accent text-white" : ""
            }`}
            onClick={() => applyTheme("fiveNine")}
          >
            5NINE Default
          </button>
          <button
            className={`px-4 py-2 border rounded-md ${
              theme === "light" ? "bg-accent text-white" : ""
            }`}
            onClick={() => applyTheme("light")}
          >
            Light
          </button>
          <button
            className={`px-4 py-2 border rounded-md ${
              theme === "dark" ? "bg-accent text-white" : ""
            }`}
            onClick={() => applyTheme("dark")}
          >
            Dark
          </button>
        </div>
      </section>

      {/* Health check */}
      <section className="panel p-6 space-y-3">
        <h2 className="text-lg font-semibold">Backend Health</h2>
        <p className="text-xs text-gray-600">
          Calls the FastAPI <code>/healthz</code> endpoint you already use from
          the CLI to confirm the instance is healthy.
        </p>
        <button
          className="btn-primary px-4 py-2 mt-1"
          onClick={checkHealth}
          disabled={healthChecking}
        >
          {healthChecking ? "Checking…" : "Run Health Check"}
        </button>

        {healthResult && (
          <pre className="mt-3 text-xs bg-white border rounded-md p-3 max-h-64 overflow-auto">
            {healthResult}
          </pre>
        )}
      </section>
    </div>
  );
}
