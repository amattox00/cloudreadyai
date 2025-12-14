import React from "react";
import { Link } from "react-router-dom";

export default function MarketingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Top nav */}
      <header className="px-6 py-5 border-b border-slate-800/60">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-sky-500/15 border border-sky-500/30 flex items-center justify-center">
              <span className="text-sky-300 font-bold">CR</span>
            </div>
            <div>
              <div className="text-lg font-semibold leading-tight">CloudReadyAI</div>
              <div className="text-xs text-slate-300">Migration assessment • diagrams • TCO</div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="text-sm px-3 py-2 rounded-lg border border-slate-700 hover:bg-slate-900"
            >
              Sign in
            </Link>
            <Link
              to="/login"
              className="text-sm px-3 py-2 rounded-lg bg-sky-600 hover:bg-sky-700"
            >
              Start an assessment
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <main className="px-6 py-12">
        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
          <div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
              Turn CSV inventories into a migration-ready assessment in minutes.
            </h1>
            <p className="mt-4 text-slate-300 max-w-xl">
              Upload infrastructure slices with guardrails, get clean coverage signals, then generate insights,
              diagrams, and cost modeling for a polished demo-ready story.
            </p>

            <div className="mt-6 flex flex-col sm:flex-row gap-3">
              <Link
                to="/login"
                className="inline-flex items-center justify-center px-4 py-2.5 rounded-lg bg-sky-600 hover:bg-sky-700 font-medium"
              >
                Sign in to start
              </Link>
              <Link
                to="/login"
                className="inline-flex items-center justify-center px-4 py-2.5 rounded-lg border border-slate-700 hover:bg-slate-900 font-medium"
              >
                Request a guided demo
              </Link>
            </div>

            <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-3">
              <FeatureCard title="Guardrails" desc="Template downloads + header validation + warnings." />
              <FeatureCard title="Results Explorer" desc="Browse ingested records (v2 inventory tables)." />
              <FeatureCard title="MVP Flow" desc="Ingestion → Insights → Diagrams → Cost → Report." />
            </div>
          </div>

          <div className="border border-slate-800/60 bg-slate-900/40 rounded-2xl p-5">
            <div className="text-xs text-slate-300 uppercase tracking-wide font-semibold">
              What you’ll do first
            </div>
            <ol className="mt-3 space-y-3 text-sm text-slate-200">
              <li className="flex gap-3">
                <span className="h-6 w-6 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold">
                  1
                </span>
                <div>
                  Create an assessment (client + environment).
                  <div className="text-xs text-slate-400">
                    This becomes the “Run” container for your data slices.
                  </div>
                </div>
              </li>
              <li className="flex gap-3">
                <span className="h-6 w-6 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold">
                  2
                </span>
                <div>
                  Download CSV templates and upload clean data.
                  <div className="text-xs text-slate-400">
                    Guardrails prevent broken headers and missing required columns.
                  </div>
                </div>
              </li>
              <li className="flex gap-3">
                <span className="h-6 w-6 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold">
                  3
                </span>
                <div>
                  Use readiness gates to unlock demo outputs.
                  <div className="text-xs text-slate-400">
                    Insights/Diagrams/Cost/Report get unlocked as coverage improves.
                  </div>
                </div>
              </li>
            </ol>

            <div className="mt-5 pt-5 border-t border-slate-800/60">
              <div className="text-xs text-slate-400">
                Note: signup can be added later (Phase: multi-tenant + RBAC). For now, login is dev-mode.
              </div>
            </div>
          </div>
        </div>

        <footer className="max-w-6xl mx-auto mt-14 pt-8 border-t border-slate-800/60 text-xs text-slate-500">
          © {new Date().getFullYear()} CloudReadyAI • Demo build
        </footer>
      </main>
    </div>
  );
}

function FeatureCard({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="border border-slate-800/60 bg-slate-900/40 rounded-xl p-4">
      <div className="text-sm font-semibold">{title}</div>
      <div className="text-xs text-slate-300 mt-1">{desc}</div>
    </div>
  );
}
