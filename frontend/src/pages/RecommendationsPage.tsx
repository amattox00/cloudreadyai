import React, { useMemo, useState } from "react";

type Strategy = "Rehost" | "Replatform" | "Refactor" | "Rearchitect" | "Retain" | "Retire";
type Effort = "Low" | "Medium" | "High";
type Risk = "Low" | "Medium" | "High";

interface Recommendation {
  id: string;
  workload: string;
  type: "Server" | "Application" | "Database";
  strategy: Strategy;
  targetCloud: string;
  targetService: string;
  monthlySavings: number;
  savingsPercent: number;
  effort: Effort;
  risk: Risk;
  wave: number;
  category: "Cost" | "Modernization" | "Risk";
  summary: string;
  details: string;
  dependencies: string[];
}

const MOCK_RECOMMENDATIONS: Recommendation[] = [
  {
    id: "REC-001",
    workload: "APP-WEB-01",
    type: "Server",
    strategy: "Rehost",
    targetCloud: "AWS",
    targetService: "EC2 m6i.large + ALB",
    monthlySavings: 180,
    savingsPercent: 32,
    effort: "Low",
    risk: "Low",
    wave: 1,
    category: "Cost",
    summary: "Rightsize and rehost web tier to EC2 with autoscaling.",
    details:
      "Current VM is over-provisioned (CPU ~12%, RAM ~24%). Recommend rehosting to EC2 m6i.large behind an Application Load Balancer with autoscaling based on CPU/requests. No OS-level blocking dependencies identified.",
    dependencies: ["APP-API-01", "SQL-01"],
  },
  {
    id: "REC-002",
    workload: "OrderManagement API",
    type: "Application",
    strategy: "Replatform",
    targetCloud: "AWS",
    targetService: "ECS Fargate",
    monthlySavings: 420,
    savingsPercent: 21,
    effort: "Medium",
    risk: "Medium",
    wave: 3,
    category: "Modernization",
    summary: "Containerize API tier and move to ECS Fargate.",
    details:
      "Stateless .NET API with clean separation from persistence. Ideal candidate for containerization. Recommend ECS Fargate with CI/CD pipeline. Requires modest code changes for configuration and logging.",
    dependencies: ["SQL-01", "Redis-01"],
  },
  {
    id: "REC-003",
    workload: "SQL-01",
    type: "Database",
    strategy: "Replatform",
    targetCloud: "AWS",
    targetService: "RDS SQL Server Standard",
    monthlySavings: 600,
    savingsPercent: 18,
    effort: "High",
    risk: "Medium",
    wave: 3,
    category: "Cost",
    summary: "Migrate SQL Server to managed RDS instance.",
    details:
      "Current SQL cluster is under-utilized and high maintenance. Recommend migration to RDS SQL Server with Multi-AZ for HA. Use DMS for minimal-downtime cutover; coordinate with dependent apps in Wave 3.",
    dependencies: ["OrderManagement API", "ReportingService"],
  },
  {
    id: "REC-004",
    workload: "LEGACY-BATCH-01",
    type: "Server",
    strategy: "Retire",
    targetCloud: "AWS",
    targetService: "N/A",
    monthlySavings: 250,
    savingsPercent: 100,
    effort: "Low",
    risk: "Low",
    wave: 1,
    category: "Risk",
    summary: "Decommission zombie batch server.",
    details:
      "No recent CPU, disk, or network activity detected for 90+ days. No active dependencies found. Recommend full decommission after 30-day observation and business validation.",
    dependencies: [],
  },
  {
    id: "REC-005",
    workload: "Customer Portal",
    type: "Application",
    strategy: "Refactor",
    targetCloud: "AWS",
    targetService: "ECS Fargate + RDS Aurora",
    monthlySavings: 950,
    savingsPercent: 27,
    effort: "High",
    risk: "High",
    wave: 4,
    category: "Modernization",
    summary:
      "Refactor monolithic portal into containerized microservices on ECS + Aurora.",
    details:
      "High-value, internet-facing monolith with performance hotspots. Recommend phased refactor into microservices on ECS Fargate with Aurora backend. Requires coordinated product, security, and development teams.",
    dependencies: ["PaymentGateway", "IdentityService", "Analytics"],
  },
];

type TabKey = "workloads" | "waves" | "architecture" | "overview";

const strategyBadgeClasses: Record<Strategy, string> = {
  Rehost: "bg-blue-50 text-blue-700 border-blue-100",
  Replatform: "bg-emerald-50 text-emerald-700 border-emerald-100",
  Refactor: "bg-purple-50 text-purple-700 border-purple-100",
  Rearchitect: "bg-pink-50 text-pink-700 border-pink-100",
  Retain: "bg-gray-50 text-gray-700 border-gray-100",
  Retire: "bg-amber-50 text-amber-700 border-amber-100",
};

const riskBadgeClasses: Record<Risk, string> = {
  Low: "bg-emerald-50 text-emerald-700 border-emerald-100",
  Medium: "bg-amber-50 text-amber-700 border-amber-100",
  High: "bg-rose-50 text-rose-700 border-rose-100",
};

const effortBadgeClasses: Record<Effort, string> = {
  Low: "bg-emerald-50 text-emerald-700 border-emerald-100",
  Medium: "bg-sky-50 text-sky-700 border-sky-100",
  High: "bg-slate-50 text-slate-700 border-slate-100",
};

const RecommendationsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>("workloads");
  const [selectedRun, setSelectedRun] = useState<string>("RUN-2025-001");
  const [strategyFilter, setStrategyFilter] = useState<Strategy | "All">("All");
  const [riskFilter, setRiskFilter] = useState<Risk | "All">("All");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const totalSavings = useMemo(
    () => MOCK_RECOMMENDATIONS.reduce((sum, r) => sum + r.monthlySavings, 0),
    []
  );

  const avgSavingsPercent = useMemo(
    () =>
      MOCK_RECOMMENDATIONS.length
        ? Math.round(
            MOCK_RECOMMENDATIONS.reduce(
              (sum, r) => sum + r.savingsPercent,
              0
            ) / MOCK_RECOMMENDATIONS.length
          )
        : 0,
    []
  );

  const filteredRecommendations = useMemo(
    () =>
      MOCK_RECOMMENDATIONS.filter((r) => {
        if (strategyFilter !== "All" && r.strategy !== strategyFilter) return false;
        if (riskFilter !== "All" && r.risk !== riskFilter) return false;
        return true;
      }),
    [strategyFilter, riskFilter]
  );

  const waves = useMemo(() => {
    const grouped: Record<number, Recommendation[]> = {};
    for (const rec of MOCK_RECOMMENDATIONS) {
      if (!grouped[rec.wave]) grouped[rec.wave] = [];
      grouped[rec.wave].push(rec);
    }
    return grouped;
  }, []);

  const handleExport = (format: "pdf" | "word" | "json") => {
    alert(`Export as ${format.toUpperCase()} is not wired up yet, but the UI is ready.`);
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="mb-1 flex items-center gap-2 text-xs text-slate-500">
              <span className="uppercase tracking-wide">Assessment</span>
              <span>›</span>
              <span className="font-medium text-slate-700">Recommendations</span>
            </div>
            <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
              Recommendations &amp; Migration Plan
            </h1>
            <p className="mt-1 text-sm text-slate-600">
              Curated actions for this assessment run: rightsizing, migration strategy,
              modernization opportunities, and target-state architecture.
            </p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Assessment Run
              </span>
              <select
                value={selectedRun}
                onChange={(e) => setSelectedRun(e.target.value)}
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 shadow-sm focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
              >
                <option value="RUN-2025-001">RUN-2025-001 (Current)</option>
                <option value="RUN-2025-002">RUN-2025-002</option>
                <option value="RUN-2024-031">RUN-2024-031</option>
              </select>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => handleExport("pdf")}
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-800 shadow-sm hover:bg-slate-50"
              >
                Export PDF
              </button>
              <button
                type="button"
                onClick={() => handleExport("word")}
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-800 shadow-sm hover:bg-slate-50"
              >
                Export Word
              </button>
              <button
                type="button"
                onClick={() => handleExport("json")}
                className="rounded-lg bg-sky-500 px-3 py-2 text-xs font-semibold text-white shadow-sm hover:bg-sky-600"
              >
                Export JSON
              </button>
            </div>
          </div>
        </div>

        {/* KPI row */}
        <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Total Recommendations
            </p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">
              {MOCK_RECOMMENDATIONS.length}
            </p>
          </div>

          <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-wide text-emerald-700">
              Monthly Savings Identified
            </p>
            <p className="mt-2 text-2xl font-semibold text-emerald-900">
              ${totalSavings.toLocaleString()}
            </p>
          </div>

          <div className="rounded-2xl border border-sky-200 bg-sky-50 p-4 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-wide text-sky-700">
              Avg. Optimization
            </p>
            <p className="mt-2 text-2xl font-semibold text-sky-900">
              {avgSavingsPercent}%
            </p>
          </div>

          <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-wide text-amber-700">
              Retire / Low-Risk Assets
            </p>
            <p className="mt-2 text-2xl font-semibold text-amber-900">
              {MOCK_RECOMMENDATIONS.filter((r) => r.strategy === "Retire").length}
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-4 flex flex-wrap gap-2 border-b border-slate-200">
          {[
            { key: "workloads", label: "Workload Recommendations" },
            { key: "waves", label: "Migration Waves" },
            { key: "architecture", label: "Target Architecture" },
            { key: "overview", label: "Executive Overview" },
          ].map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => setActiveTab(tab.key as TabKey)}
              className={`relative -mb-px rounded-t-lg px-4 py-2 text-sm font-medium ${
                activeTab === tab.key
                  ? "bg-white text-sky-700 shadow-inner"
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              {tab.label}
              {activeTab === tab.key && (
                <span className="absolute inset-x-0 -bottom-[1px] h-[2px] rounded-full bg-sky-500" />
              )}
            </button>
          ))}
        </div>

        {/* === WORKLOADS TAB (HYBRID LAYOUT) === */}
        {activeTab === "workloads" && (
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            {/* Filter bar */}
            <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-wrap items-center gap-3 text-xs">
                <span className="font-semibold uppercase tracking-wide text-slate-500">
                  Filters
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-slate-500">Strategy</span>
                  <select
                    value={strategyFilter}
                    onChange={(e) =>
                      setStrategyFilter(e.target.value as Strategy | "All")
                    }
                    className="rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs text-slate-800 shadow-sm focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                  >
                    <option value="All">All</option>
                    <option value="Rehost">Rehost</option>
                    <option value="Replatform">Replatform</option>
                    <option value="Refactor">Refactor</option>
                    <option value="Rearchitect">Rearchitect</option>
                    <option value="Retain">Retain</option>
                    <option value="Retire">Retire</option>
                  </select>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-slate-500">Risk</span>
                  <select
                    value={riskFilter}
                    onChange={(e) =>
                      setRiskFilter(e.target.value as Risk | "All")
                    }
                    className="rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs text-slate-800 shadow-sm focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                  >
                    <option value="All">All levels</option>
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                  </select>
                </div>
              </div>

              <p className="text-xs text-slate-500">
                Showing{" "}
                <span className="font-semibold text-slate-800">
                  {filteredRecommendations.length}
                </span>{" "}
                of {MOCK_RECOMMENDATIONS.length} recommendations.
              </p>
            </div>

            {/* Hybrid card list */}
            <div className="space-y-3">
              {filteredRecommendations.map((rec) => {
                const isExpanded = expandedId === rec.id;

                return (
                  <div
                    key={rec.id}
                    className="rounded-xl border border-slate-200 bg-slate-50/70"
                  >
                    <button
                      type="button"
                      onClick={() =>
                        setExpandedId(isExpanded ? null : rec.id)
                      }
                      className="flex w-full flex-col gap-3 px-4 py-3 text-left hover:bg-slate-50 sm:grid sm:grid-cols-[2fr,1.1fr] sm:items-start"
                    >
                      {/* Left side: workload summary */}
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-slate-900">
                            {rec.workload}
                          </span>
                          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-slate-600">
                            {rec.type}
                          </span>
                        </div>
                        <p className="mt-1 text-xs text-slate-600">
                          {rec.summary}
                        </p>
                        <p className="mt-1 text-[11px] text-slate-400">
                          Wave {rec.wave} • {rec.targetCloud} • {rec.category}
                        </p>
                      </div>

                      {/* Right side: key metrics */}
                      <div className="flex flex-col items-start gap-2 text-xs sm:items-end">
                        <div className="flex flex-wrap gap-2">
                          <span
                            className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium ${strategyBadgeClasses[rec.strategy]}`}
                          >
                            {rec.strategy}
                          </span>
                          <span
                            className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium ${riskBadgeClasses[rec.risk]}`}
                          >
                            {rec.risk} risk
                          </span>
                        </div>

                        <div className="text-right sm:text-right">
                          <div className="text-[11px] uppercase tracking-wide text-slate-400">
                            Target
                          </div>
                          <div className="text-xs font-medium text-slate-800">
                            {rec.targetService}
                          </div>
                          <div className="text-[11px] text-slate-400">
                            {rec.targetCloud}
                          </div>
                        </div>

                        <div className="flex flex-wrap items-center gap-3 sm:justify-end">
                          <div className="text-right text-emerald-700">
                            <div className="text-[11px] uppercase tracking-wide text-emerald-500">
                              Savings
                            </div>
                            <div className="text-xs font-semibold">
                              ${rec.monthlySavings.toLocaleString()}/mo
                            </div>
                            <div className="text-[11px] text-emerald-500">
                              {rec.savingsPercent}% reduction
                            </div>
                          </div>
                          <span
                            className={`inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium ${effortBadgeClasses[rec.effort]}`}
                          >
                            {rec.effort} effort
                          </span>
                        </div>

                        <span className="text-[11px] text-slate-400">
                          {isExpanded ? "Hide details" : "View details"}
                        </span>
                      </div>
                    </button>

                    {/* Expanded details */}
                    {isExpanded && (
                      <div className="border-t border-slate-100 bg-slate-100 px-4 py-3 text-sm text-slate-700">
                        <div className="grid gap-4 md:grid-cols-[2fr,1fr]">
                          <div>
                            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                              Recommendation Details
                            </p>
                            <p className="mt-1 text-sm text-slate-700">
                              {rec.details}
                            </p>
                          </div>
                          <div className="space-y-3 text-xs">
                            <div>
                              <p className="font-semibold uppercase tracking-wide text-slate-500">
                                Dependencies
                              </p>
                              {rec.dependencies.length === 0 ? (
                                <p className="mt-1 text-slate-500">
                                  No active dependencies detected.
                                </p>
                              ) : (
                                <ul className="mt-1 list-disc pl-4 text-slate-700">
                                  {rec.dependencies.map((d) => (
                                    <li key={d}>{d}</li>
                                  ))}
                                </ul>
                              )}
                            </div>
                            <div>
                              <p className="font-semibold uppercase tracking-wide text-slate-500">
                                Planning Notes
                              </p>
                              <p className="mt-1 text-slate-600">
                                Align this change with the migration wave plan, including
                                testing, cutover, and rollback procedures.
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* === WAVES TAB === */}
        {activeTab === "waves" && (
          <div className="space-y-4">
            {Object.keys(waves)
              .sort((a, b) => Number(a) - Number(b))
              .map((waveKey) => {
                const waveNumber = Number(waveKey);
                const recs = waves[waveNumber];
                const totalWaveSavings = recs.reduce(
                  (sum, r) => sum + r.monthlySavings,
                  0
                );

                return (
                  <div
                    key={waveNumber}
                    className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
                  >
                    <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <h2 className="text-sm font-semibold text-slate-900">
                          Wave {waveNumber}
                        </h2>
                        <p className="text-xs text-slate-500">
                          {recs.length} workloads • $
                          {totalWaveSavings.toLocaleString()}/mo savings
                        </p>
                      </div>

                      <div className="flex flex-wrap gap-2 text-[11px] text-slate-500">
                        <span className="rounded-full bg-slate-100 px-2 py-0.5">
                          Servers, apps, and DBs grouped by dependency
                        </span>
                        <span className="rounded-full bg-slate-100 px-2 py-0.5">
                          Prioritized to minimize risk and blast radius
                        </span>
                      </div>
                    </div>

                    <div className="grid gap-3 md:grid-cols-2">
                      {recs.map((rec) => (
                        <div
                          key={rec.id}
                          className="flex flex-col justify-between rounded-xl border border-slate-100 bg-slate-50 p-3"
                        >
                          <div>
                            <div className="flex items-center justify-between gap-2">
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-semibold text-slate-900">
                                  {rec.workload}
                                </span>
                                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-slate-600">
                                  {rec.type}
                                </span>
                              </div>
                              <span
                                className={`inline-flex rounded-full border px-2 py-0.5 text-[10px] font-medium ${strategyBadgeClasses[rec.strategy]}`}
                              >
                                {rec.strategy}
                              </span>
                            </div>
                            <p className="mt-1 line-clamp-2 text-xs text-slate-600">
                              {rec.summary}
                            </p>
                          </div>

                          <div className="mt-3 flex items-center justify-between text-[11px]">
                            <div className="space-y-1">
                              <p className="text-slate-500">
                                Target:{" "}
                                <span className="font-medium text-slate-800">
                                  {rec.targetService}
                                </span>
                              </p>
                              <p className="text-emerald-600">
                                Savings:{" "}
                                <span className="font-semibold">
                                  ${rec.monthlySavings.toLocaleString()}/mo
                                </span>{" "}
                                ({rec.savingsPercent}%)
                              </p>
                            </div>
                            <div className="text-right">
                              <p
                                className={`inline-flex rounded-full border px-2 py-0.5 ${effortBadgeClasses[rec.effort]}`}
                              >
                                {rec.effort} effort
                              </p>
                              <p className="mt-1 text-slate-500">
                                Risk:{" "}
                                <span
                                  className={`inline-flex rounded-full border px-2 py-0.5 ${riskBadgeClasses[rec.risk]}`}
                                >
                                  {rec.risk}
                                </span>
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
          </div>
        )}

        {/* === ARCHITECTURE TAB === */}
        {activeTab === "architecture" && (
          <div className="grid gap-4 lg:grid-cols-[1.7fr,1.3fr]">
            <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
              <h2 className="text-sm font-semibold text-slate-900">
                Target Cloud Architecture (Conceptual View)
              </h2>
              <p className="mt-1 text-xs text-slate-600">
                Logical target-state design derived from the recommendations engine.
                In a later phase this will be fully diagram-driven.
              </p>
              <div className="mt-4 rounded-xl border border-dashed border-slate-200 bg-slate-50 p-4 text-xs text-slate-700">
                <pre className="text-[11px] leading-relaxed">
{`VPC: crai-core-vpc
  - Subnet: app-private-a  (APP-WEB-01, OrderManagement API, Customer Portal)
  - Subnet: db-private-a   (SQL-01, Aurora cluster)
  - Subnet: public-edge-a  (ALB, NAT Gateway)

Networking:
  - ALB routes to EC2 ASG + ECS Fargate services
  - Security groups enforce tier isolation

Compute:
  - EC2 m6i.large autoscaling group
  - ECS Fargate services for APIs and microservices

Data:
  - RDS SQL Server (SQL-01)
  - Aurora PostgreSQL cluster (Portal refactor target)

Identity & Ops:
  - IAM roles for EC2, ECS, RDS
  - Centralized logging & metrics`}
                </pre>
              </div>
            </div>

            <div className="space-y-4">
              <div className="rounded-2xl border border-sky-200 bg-sky-50 p-4 shadow-sm">
                <h2 className="text-sm font-semibold text-sky-900">
                  Service Mapping Summary
                </h2>
                <ul className="mt-2 space-y-2 text-xs text-sky-900">
                  <li>• 2 workloads → EC2 (rightsized rehost)</li>
                  <li>• 2 workloads → ECS Fargate (containerized APIs / services)</li>
                  <li>• 1 workload → RDS SQL Server (managed DB)</li>
                  <li>• 1 workload → Retirement (zombie / unused asset)</li>
                </ul>
              </div>

              <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 shadow-sm text-xs">
                <h2 className="text-sm font-semibold text-emerald-900">
                  Architecture Guardrails
                </h2>
                <ul className="mt-2 space-y-1 text-emerald-900">
                  <li>• Aligns with AWS Well-Architected (cost, reliability, security).</li>
                  <li>• Uses private subnets for application and database tiers.</li>
                  <li>• Leans on managed services to reduce operational overhead.</li>
                  <li>• Provides a clear runway for incremental modernization.</li>
                </ul>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm text-xs">
                <h2 className="text-sm font-semibold text-slate-900">
                  Next Step (Technical)
                </h2>
                <p className="mt-1 text-slate-600">
                  Future iterations will populate this view directly from an architecture
                  engine and render diagrams using draw.io-compatible XML for export.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* === EXECUTIVE OVERVIEW === */}
        {activeTab === "overview" && (
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-sm font-semibold text-slate-900">
              Executive Overview
            </h2>
            <p className="mt-1 text-xs text-slate-600">
              Narrative summary suitable for inclusion in client presentations, reports,
              and proposals.
            </p>
            <div className="mt-4 space-y-3 text-sm text-slate-700">
              <p>
                CloudReadyAI has identified{" "}
                <span className="font-semibold">
                  {MOCK_RECOMMENDATIONS.length} high-impact recommendations
                </span>{" "}
                for assessment run{" "}
                <span className="font-mono text-xs bg-slate-100 px-1.5 py-0.5 rounded">
                  {selectedRun}
                </span>
                .
              </p>
              <p>
                Combined, these actions represent an estimated{" "}
                <span className="font-semibold">
                  ${totalSavings.toLocaleString()} in monthly cost reduction
                </span>{" "}
                (averaging {avgSavingsPercent}% optimization per workload), while also
                improving resilience, security, and operational efficiency.
              </p>
              <p>
                Migration is sequenced into clearly defined waves that balance technical
                dependencies, business risk, and modernization ambition. Early waves focus
                on low-risk cost reduction and cleanup, while later waves address database
                modernization and application refactoring to cloud-native services.
              </p>
              <p>
                This recommendations view becomes the baseline for finalizing the
                migration roadmap, detailed cutover plans, and implementation backlog in
                partnership with the client&apos;s architecture and operations teams.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecommendationsPage;
