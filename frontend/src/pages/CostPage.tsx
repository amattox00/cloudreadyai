import React, { useState } from "react";

type AwsTcoResponse = {
  run_id: string;
  region: string;
  monthly_ondemand: number;
  annual_ondemand: number;
  monthly_1yr: number;
  annual_1yr: number;
  monthly_3yr: number;
  annual_3yr: number;
  compute_monthly_total: number;
  storage_monthly_total: number;
  nat_gateway_cost?: number;
  rds_cost?: number;
  compute?: Array<{
    server_id: string;
    hostname: string;
    vcpu: number;
    ram_gb: number;
    aws_instance: string;
    monthly_cost: number;
  }>;
  storage?: Array<{
    volume_id: string;
    server_id: string;
    storage_type: string;
    size_gb: number;
    monthly_cost: number;
  }>;
};

const regions = [
  { code: "us-east-1", label: "US East (N. Virginia)" },
  { code: "us-east-2", label: "US East (Ohio)" },
  { code: "us-west-2", label: "US West (Oregon)" },
  { code: "eu-west-1", label: "EU (Ireland)" },
  { code: "eu-central-1", label: "EU (Frankfurt)" },
];

export default function CostPage() {
  const [runId, setRunId] = useState("");
  const [region, setRegion] = useState("us-east-1");
  const [loading, setLoading] = useState(false);
  const [costData, setCostData] = useState<AwsTcoResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  const computeList = Array.isArray(costData?.compute) ? costData!.compute! : [];
  const storageList = Array.isArray(costData?.storage) ? costData!.storage! : [];

  const natMonthly = costData?.nat_gateway_cost ?? 0;
  const rdsMonthly = costData?.rds_cost ?? 0;

  const handleLoadCost = async () => {
    if (!runId) {
      setErrorMsg("Please enter a Run ID first.");
      return;
    }

    setLoading(true);
    setErrorMsg("");
    setCostData(null);

    try {
      const res = await fetch(`/v1/tco/aws/${runId}?region=${region}`);
      if (!res.ok) {
        setErrorMsg("Failed to load cost data from backend.");
        setLoading(false);
        return;
      }
      const json = await res.json();
      if (json.error) {
        setErrorMsg(json.error);
      } else {
        setCostData(json as AwsTcoResponse);
      }
    } catch (err) {
      setErrorMsg("Unexpected error while loading cost data.");
    } finally {
      setLoading(false);
    }
  };

  const handleExportPdf = () => {
    // Stub for now — later this can call a backend /v1/report/pdf endpoint
    window.alert("PDF export coming soon. This is a placeholder button.");
  };

  const handleExportJson = () => {
    if (!costData) return;
    const blob = new Blob([JSON.stringify(costData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${costData.run_id}-${costData.region}-aws-tco.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formatMoney = (value?: number) =>
    typeof value === "number" ? `$${value.toFixed(2)}` : "—";

  const totalMonthlyAll =
    (costData?.monthly_ondemand ?? 0) +
    natMonthly +
    rdsMonthly;

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900">
      <div className="max-w-7xl mx-auto px-6 py-8">

        {/* Breadcrumb */}
        <nav className="text-sm text-gray-500 mb-4">
          <span className="cursor-default">Dashboard</span>
          <span className="mx-2">/</span>
          <span className="font-semibold text-gray-700">Cost &amp; TCO (AWS)</span>
        </nav>

        {/* Page header */}
        <header className="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold">
              Cost &amp; TCO <span className="text-orange-600">(AWS)</span>
            </h1>
            <p className="text-gray-600 mt-2 max-w-2xl">
              Real-time AWS On-Demand pricing (Linux, shared tenancy) with simple 1-year
              and 3-year commitment models, mapped directly to your assessment runs.
            </p>
          </div>

          {/* Action buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleExportJson}
              disabled={!costData}
              className="px-4 py-2 rounded-xl border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Export JSON
            </button>
            <button
              onClick={handleExportPdf}
              disabled={!costData}
              className="px-4 py-2 rounded-xl bg-orange-600 text-white text-sm font-semibold shadow hover:bg-orange-700 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Export to PDF
            </button>
          </div>
        </header>

        {/* Run / Region / AWS branding bar */}
        <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex flex-wrap items-center gap-6">
            <div className="flex flex-col">
              <label className="text-xs font-semibold text-gray-600 mb-1">
                Assessment Run ID
              </label>
              <input
                type="text"
                value={runId}
                onChange={(e) => setRunId(e.target.value)}
                placeholder="run-35073330"
                className="border border-gray-300 rounded-lg px-4 py-2 w-72 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>

            <div className="flex flex-col">
              <label className="text-xs font-semibold text-gray-600 mb-1">
                Region
              </label>
              <select
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="border border-gray-300 rounded-lg px-4 py-2 w-64 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              >
                {regions.map((r) => (
                  <option key={r.code} value={r.code}>
                    {r.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex-1" />

            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wide text-gray-500">
                Powered by
              </span>
              <img
                src="https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png"
                alt="AWS"
                className="h-7 rounded"
              />
            </div>

            <button
              onClick={handleLoadCost}
              disabled={loading}
              className="px-6 py-3 rounded-xl bg-orange-600 text-white font-semibold text-sm shadow hover:bg-orange-700 disabled:opacity-60 disabled:cursor-wait"
            >
              {loading ? "Loading…" : "Load Cost"}
            </button>
          </div>
        </section>

        {/* Error banner */}
        {errorMsg && (
          <div className="mb-6 rounded-xl border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
            {errorMsg}
          </div>
        )}

        {/* Nothing loaded yet */}
        {!costData && !errorMsg && !loading && (
          <div className="mb-10 text-sm text-gray-500">
            Enter a valid assessment Run ID and region, then click{" "}
            <span className="font-semibold">Load Cost</span> to view AWS pricing.
          </div>
        )}

        {/* Main content when data exists */}
        {costData && (
          <>
            {/* Top summary cards */}
            <section className="grid gap-4 md:grid-cols-4 mb-8">
              {/* Run / Region card */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex flex-col justify-between hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-gray-500">RUN</span>
                  <span className="text-[11px] inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
                    🔁 AWS TCO
                  </span>
                </div>
                <div className="text-sm font-mono text-gray-900 truncate">
                  {costData.run_id}
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  Region: <span className="font-semibold">{costData.region}</span>
                </div>
              </div>

              {/* Monthly On-Demand */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-gray-500">
                    MONTHLY (ON-DEMAND)
                  </span>
                  <span className="text-lg">💵</span>
                </div>
                <div className="text-2xl font-bold text-orange-600">
                  {formatMoney(costData.monthly_ondemand)}
                </div>
                <div className="mt-2 h-1.5 rounded-full bg-orange-100 overflow-hidden">
                  <div className="h-full w-2/3 bg-orange-500" />
                </div>
              </div>

              {/* Monthly 1-year */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-gray-500">
                    MONTHLY (1-YEAR, MODELED)
                  </span>
                  <span className="text-lg">📉</span>
                </div>
                <div className="text-2xl font-bold text-green-700">
                  {formatMoney(costData.monthly_1yr)}
                </div>
                <div className="mt-2 h-1.5 rounded-full bg-green-100 overflow-hidden">
                  <div className="h-full w-1/2 bg-green-600" />
                </div>
              </div>

              {/* Monthly 3-year */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-gray-500">
                    MONTHLY (3-YEAR, MODELED)
                  </span>
                  <span className="text-lg">📊</span>
                </div>
                <div className="text-2xl font-bold text-blue-700">
                  {formatMoney(costData.monthly_3yr)}
                </div>
                <div className="mt-2 h-1.5 rounded-full bg-blue-100 overflow-hidden">
                  <div className="h-full w-1/3 bg-blue-600" />
                </div>
              </div>
            </section>

            {/* Annual + per-service summary */}
            <section className="grid gap-4 md:grid-cols-4 mb-10">
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className="text-xs font-semibold text-gray-500 mb-1">
                  ANNUAL (ON-DEMAND)
                </div>
                <div className="text-xl font-bold">{formatMoney(costData.annual_ondemand)}</div>
                <div className="mt-1 text-xs text-gray-500">All services</div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className="text-xs font-semibold text-gray-500 mb-1">
                  ANNUAL (1-YEAR, MODELED)
                </div>
                <div className="text-xl font-bold text-green-700">
                  {formatMoney(costData.annual_1yr)}
                </div>
                <div className="mt-1 text-xs text-gray-500">Estimated with simple discounting</div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className="text-xs font-semibold text-gray-500 mb-1">
                  ANNUAL (3-YEAR, MODELED)
                </div>
                <div className="text-xl font-bold text-blue-700">
                  {formatMoney(costData.annual_3yr)}
                </div>
                <div className="mt-1 text-xs text-gray-500">Planning-only scenario</div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className="text-xs font-semibold text-gray-500 mb-1">
                  TOTAL MONTHLY (ALL SERVICES)
                </div>
                <div className="text-xl font-bold">
                  {formatMoney(totalMonthlyAll)}
                </div>
                <div className="mt-1 text-xs text-gray-500">
                  Includes EC2, EBS, NAT, and RDS components.
                </div>
              </div>
            </section>

            {/* Per-service breakdown strip */}
            <section className="grid gap-4 md:grid-cols-4 mb-12">
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex flex-col gap-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-500">EC2</span>
                  <span>🖥️</span>
                </div>
                <div className="text-lg font-bold">
                  {formatMoney(costData.compute_monthly_total)}
                </div>
                <div className="text-xs text-gray-500">
                  {computeList.length} servers
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex flex-col gap-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-500">EBS</span>
                  <span>💽</span>
                </div>
                <div className="text-lg font-bold">
                  {formatMoney(costData.storage_monthly_total)}
                </div>
                <div className="text-xs text-gray-500">
                  {storageList.length} volumes
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex flex-col gap-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-500">
                    NAT GATEWAY
                  </span>
                  <span>🌐</span>
                </div>
                <div className="text-lg font-bold">
                  {formatMoney(natMonthly)}
                </div>
                <div className="text-xs text-gray-500">Modeled data transfer</div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex flex-col gap-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-500">RDS</span>
                  <span>🗄️</span>
                </div>
                <div className="text-lg font-bold">
                  {formatMoney(rdsMonthly)}
                </div>
                <div className="text-xs text-gray-500">Placeholder modeled DB cost</div>
              </div>
            </section>

            {/* Compute table */}
            <section className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-10">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">Compute (EC2)</h2>
                <span className="text-xs text-gray-500">
                  {computeList.length} servers • Subtotal{" "}
                  <span className="font-semibold">
                    {formatMoney(costData.compute_monthly_total)}
                  </span>
                </span>
              </div>

              {computeList.length === 0 ? (
                <div className="text-sm text-gray-500">
                  No compute records found for this run.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm border-separate border-spacing-y-1">
                    <thead>
                      <tr className="text-xs uppercase tracking-wide text-gray-500">
                        <th className="px-3 py-2">Server</th>
                        <th className="px-3 py-2">vCPU</th>
                        <th className="px-3 py-2">RAM (GB)</th>
                        <th className="px-3 py-2">AWS Instance</th>
                        <th className="px-3 py-2 text-right">Monthly Cost</th>
                      </tr>
                    </thead>
                    <tbody>
                      {computeList.map((s, idx) => (
                        <tr
                          key={idx}
                          className="bg-gray-50 hover:bg-gray-100 transition-colors"
                        >
                          <td className="px-3 py-2">
                            <div className="font-semibold">{s.hostname}</div>
                            <div className="text-[11px] text-gray-500">
                              {s.server_id}
                            </div>
                          </td>
                          <td className="px-3 py-2">{s.vcpu}</td>
                          <td className="px-3 py-2">{s.ram_gb}</td>
                          <td className="px-3 py-2 font-mono text-xs">
                            {s.aws_instance}
                          </td>
                          <td className="px-3 py-2 text-right font-semibold">
                            {formatMoney(s.monthly_cost)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            {/* Storage table */}
            <section className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-10">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">Storage (EBS)</h2>
                <span className="text-xs text-gray-500">
                  {storageList.length} volumes • Subtotal{" "}
                  <span className="font-semibold">
                    {formatMoney(costData.storage_monthly_total)}
                  </span>
                </span>
              </div>

              {storageList.length === 0 ? (
                <div className="text-sm text-gray-500">
                  No storage volumes found for this run.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm border-separate border-spacing-y-1">
                    <thead>
                      <tr className="text-xs uppercase tracking-wide text-gray-500">
                        <th className="px-3 py-2">Volume ID</th>
                        <th className="px-3 py-2">Server ID</th>
                        <th className="px-3 py-2">Type</th>
                        <th className="px-3 py-2">Size (GB)</th>
                        <th className="px-3 py-2 text-right">Monthly Cost</th>
                      </tr>
                    </thead>
                    <tbody>
                      {storageList.map((v, idx) => (
                        <tr
                          key={idx}
                          className="bg-gray-50 hover:bg-gray-100 transition-colors"
                        >
                          <td className="px-3 py-2 font-mono text-xs">
                            {v.volume_id}
                          </td>
                          <td className="px-3 py-2 text-xs">{v.server_id}</td>
                          <td className="px-3 py-2 text-xs">{v.storage_type}</td>
                          <td className="px-3 py-2">{v.size_gb}</td>
                          <td className="px-3 py-2 text-right font-semibold">
                            {formatMoney(v.monthly_cost)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            {/* Disclaimers */}
            <section className="text-[11px] text-gray-500 mb-8">
              <p>
                Pricing estimates are based on AWS public On-Demand rates for Linux instances with
                shared tenancy in the selected region. Actual AWS bills may vary depending on
                Savings Plans / Reserved Instances, data transfer, additional services, discounts,
                and taxes.
              </p>
              <p className="mt-2">
                1-year and 3-year commitment scenarios shown here are simplified models for planning
                purposes only and are not exact AWS Reserved Instance or Savings Plan quotes.
              </p>
            </section>
          </>
        )}
      </div>
    </div>
  );
}
