import React, { useState } from "react";

type Scenario = "baseline" | "rightsized" | "ri1" | "ri3";

export default function CostTcoPage() {
  const [runId, setRunId] = useState("b2-api-test-001");
  const [scenario, setScenario] = useState<Scenario>("baseline");
  const [cloud, setCloud] = useState("aws");
  const [region, setRegion] = useState("us-east-1");

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="panel p-4">
        <h1 className="text-2xl font-semibold mb-1">Cost &amp; TCO</h1>
        <p className="text-sm text-[var(--text-muted)]">
          This is the landing zone for Phase D. Each card below will eventually
          be driven by your cost engine (baseline, rightsized, and RI/SP
          scenarios) for a single assessment run.
        </p>
      </section>

      {/* Run + scenario + assumptions */}
      <section className="panel p-4 space-y-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Run */}
          <div className="space-y-2">
            <h2 className="text-sm font-semibold">Assessment Run</h2>
            <input
              className="w-full"
              value={runId}
              onChange={(e) => setRunId(e.target.value)}
              placeholder="e.g. b2-api-test-001"
            />
            <p className="text-[11px] text-[var(--text-muted)]">
              In the next pass, this will be a dropdown of runs from{" "}
              <code>/v1/runs</code>. For now it&apos;s just a label driving the
              text on this page.
            </p>
          </div>

          {/* Scenario */}
          <div className="space-y-2">
            <h2 className="text-sm font-semibold">Scenario</h2>
            <select
              className="w-full"
              value={scenario}
              onChange={(e) => setScenario(e.target.value as Scenario)}
            >
              <option value="baseline">Baseline (as-is)</option>
              <option value="rightsized">Rightsized</option>
              <option value="ri1">1-year RI / Savings Plan</option>
              <option value="ri3">3-year RI / Savings Plan</option>
            </select>
            <p className="text-[11px] text-[var(--text-muted)]">
              These map directly to the planned scenarios in your Phase D cost
              model.
            </p>
          </div>

          {/* Cloud & region */}
          <div className="space-y-2">
            <h2 className="text-sm font-semibold">Cloud &amp; Region</h2>
            <div className="flex gap-2">
              <select
                className="flex-1"
                value={cloud}
                onChange={(e) => setCloud(e.target.value)}
              >
                <option value="aws">AWS</option>
                <option value="azure">Azure</option>
                <option value="gcp">GCP</option>
              </select>
              <input
                className="flex-1"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                placeholder="us-east-1"
              />
            </div>
            <p className="text-[11px] text-[var(--text-muted)]">
              Later, these will be passed into your pricing tables /
              calculators. For now, they only drive the labels below.
            </p>
          </div>
        </div>

        <div className="text-[11px] text-[var(--text-muted)]">
          In Phase D, this panel will call an API like{" "}
          <code>
            /v1/cost/estimate?run_id={runId}&amp;scenario={scenario}
          </code>{" "}
          and hydrate the cards and tables below.
        </div>
      </section>

      {/* TCO summary strip */}
      <section className="panel p-4 space-y-4">
        <h2 className="text-lg font-semibold">TCO Summary</h2>
        <p className="text-xs text-[var(--text-muted)]">
          These tiles will show the key story for this assessment: what the
          cloud scenario costs, how it compares to on-prem, and what savings
          look like over 3 years.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-3">
          <TcoTile
            label="Monthly Cloud Cost"
            value="—"
            caption="Will be computed from aggregated compute, storage, and network pricing for this scenario."
          />
          <TcoTile
            label="3-Year Cloud Cost"
            value="—"
            caption="This will reflect your RI/SP choices, growth assumptions, and discount models."
          />
          <TcoTile
            label="Savings vs On-Prem"
            value="—"
            caption="This will eventually compare cloud scenarios to a modeled on-prem TCO baseline."
          />
        </div>
      </section>

      {/* Breakdown tables */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="panel p-4 space-y-2 lg:col-span-2">
          <h2 className="text-lg font-semibold">Compute Breakdown</h2>
          <p className="text-xs text-[var(--text-muted)] mb-2">
            Per-instance or per-group view of EC2/VM sizing, utilization, and
            effective hourly/monthly rates for this scenario.
          </p>
          <PlaceholderTable
            columns={["Group", "Instances", "vCPU", "RAM (GB)", "Monthly Cost"]}
            rows={[
              ["App tier", "—", "—", "—", "—"],
              ["DB tier", "—", "—", "—", "—"],
              ["Mgmt/Tools", "—", "—", "—", "—"],
            ]}
          />
        </div>

        <div className="panel p-4 space-y-2">
          <h2 className="text-lg font-semibold">Storage &amp; Other</h2>
          <p className="text-xs text-[var(--text-muted)] mb-2">
            High-level storage (gp3, io2, S3 tiers) plus licenses and support
            elements that roll into the TCO.
          </p>
          <PlaceholderTable
            columns={["Category", "Monthly Cost"]}
            rows={[
              ["Block storage", "—"],
              ["Object storage", "—"],
              ["Licenses / support", "—"],
            ]}
          />
        </div>
      </section>
    </div>
  );
}

type TcoTileProps = {
  label: string;
  value: string;
  caption: string;
};

function TcoTile({ label, value, caption }: TcoTileProps) {
  return (
    <div className="border rounded-xl bg-white/70 px-4 py-3 flex flex-col">
      <span className="text-[10px] uppercase tracking-wide text-gray-500 mb-1">
        {label}
      </span>
      <span className="text-xl font-semibold text-gray-900 mb-1">
        {value}
      </span>
      <span className="text-[11px] text-[var(--text-muted)]">{caption}</span>
    </div>
  );
}

type PlaceholderTableProps = {
  columns: string[];
  rows: (string[])[];
};

function PlaceholderTable({ columns, rows }: PlaceholderTableProps) {
  return (
    <div className="border rounded-lg bg-white/70 overflow-hidden">
      <table className="w-full text-xs">
        <thead className="bg-gray-100">
          <tr>
            {columns.map((c) => (
              <th
                key={c}
                className="px-2 py-1 text-left font-semibold text-gray-700 border-b"
              >
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, idx) => (
            <tr key={idx} className="odd:bg-white even:bg-gray-50">
              {r.map((cell, j) => (
                <td key={j} className="px-2 py-1 border-b text-gray-800">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
