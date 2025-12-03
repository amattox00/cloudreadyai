import React from "react";
import { useParams, Link, useNavigate } from "react-router-dom";

type ServerRow = {
  name: string;
  vcpu: number;
  ramGb: number;
  os: string;
  role: string;
};

type StorageRow = {
  id: string;
  sizeGb: number;
  type: string;
  attachedTo: string;
};

type NetworkRow = {
  segment: string;
  vlan: string;
  bandwidth: string;
  notes: string;
};

type PortfolioDetail = {
  id: string;
  name: string;
  code: string;
  summary: string;
  servers: ServerRow[];
  storage: StorageRow[];
  network: NetworkRow[];
};

const MOCK_PORTFOLIOS: Record<string, PortfolioDetail> = {
  "usda-assess-fy25": {
    id: "usda-assess-fy25",
    name: "USDA Assess FY25",
    code: "USDA-ASSESS-FY25",
    summary:
      "Representative data for USDA assessment. In the real system this will be populated from /v1/portfolio APIs once wired.",
    servers: [
      {
        name: "usda-app-01",
        vcpu: 8,
        ramGb: 32,
        os: "RHEL 8",
        role: "Application",
      },
      {
        name: "usda-db-01",
        vcpu: 16,
        ramGb: 64,
        os: "RHEL 8",
        role: "Database",
      },
    ],
    storage: [
      {
        id: "vol-001",
        sizeGb: 1024,
        type: "SAN (Tier 1)",
        attachedTo: "usda-db-01",
      },
      {
        id: "vol-002",
        sizeGb: 512,
        type: "SAN (Tier 2)",
        attachedTo: "usda-app-01",
      },
    ],
    network: [
      {
        segment: "App VLAN",
        vlan: "120",
        bandwidth: "10 Gbps",
        notes: "Front-end / mid-tier",
      },
      {
        segment: "DB VLAN",
        vlan: "130",
        bandwidth: "10 Gbps",
        notes: "Back-end database segment",
      },
    ],
  },
  "cbp-cspd": {
    id: "cbp-cspd",
    name: "DHS CBP CSPD",
    code: "CBP-CSPD",
    summary:
      "Representative data for DHS CBP CSPD workloads. Will eventually map to live ingestion + analysis results.",
    servers: [
      {
        name: "cbp-cspd-app-01",
        vcpu: 4,
        ramGb: 16,
        os: "Windows Server 2019",
        role: "Application",
      },
      {
        name: "cbp-cspd-web-01",
        vcpu: 4,
        ramGb: 8,
        os: "Windows Server 2019",
        role: "Web",
      },
    ],
    storage: [
      {
        id: "vol-101",
        sizeGb: 256,
        type: "NAS",
        attachedTo: "cbp-cspd-web-01",
      },
      {
        id: "vol-102",
        sizeGb: 512,
        type: "SAN",
        attachedTo: "cbp-cspd-app-01",
      },
    ],
    network: [
      {
        segment: "DMZ VLAN",
        vlan: "210",
        bandwidth: "1 Gbps",
        notes: "External-facing web tier",
      },
      {
        segment: "App VLAN",
        vlan: "220",
        bandwidth: "10 Gbps",
        notes: "Internal application tier",
      },
    ],
  },
};

export default function PortfolioDetailLayout() {
  const { portfolioId } = useParams<{ portfolioId: string }>();
  const navigate = useNavigate();

  if (!portfolioId || !MOCK_PORTFOLIOS[portfolioId]) {
    return (
      <div className="space-y-4">
        <p className="text-red-600 text-sm">
          Portfolio not found. This is using mock data until the portfolio APIs
          are wired.
        </p>
        <button
          className="btn-primary px-4 py-2"
          onClick={() => navigate("/portfolio")}
        >
          Back to Portfolios
        </button>
      </div>
    );
  }

  const detail = MOCK_PORTFOLIOS[portfolioId];

  return (
    <div className="space-y-6">
      {/* Breadcrumbs */}
      <div className="text-xs text-gray-600 space-x-1">
        <Link to="/portfolio" className="text-accent">
          Home
        </Link>
        <span>/</span>
        <span>portfolio</span>
        <span>/</span>
        <span>{detail.code}</span>
      </div>

      <header className="flex items-baseline justify-between">
        <div>
          <h1 className="text-2xl font-semibold">{detail.name}</h1>
          <div className="text-xs text-gray-600">{detail.code}</div>
        </div>
      </header>

      <section className="panel p-6 space-y-2">
        <h2 className="text-lg font-semibold">Summary</h2>
        <p className="text-sm text-gray-700">{detail.summary}</p>
        <p className="text-xs text-gray-600 mt-1">
          In the live system, these values will be driven from the ingestion +
          analysis pipeline for this portfolio&apos;s runs.
        </p>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Servers */}
        <div className="panel p-4 space-y-2">
          <h3 className="font-semibold text-sm">Servers</h3>
          <p className="text-xs text-gray-600">
            Representative compute inventory for this portfolio.
          </p>
          <div className="mt-2 space-y-1 text-xs">
            {detail.servers.map((s) => (
              <div
                key={s.name}
                className="flex justify-between border-b pb-1 mb-1"
              >
                <div>
                  <div className="font-semibold text-sm">{s.name}</div>
                  <div className="text-[11px] text-gray-600">{s.os}</div>
                </div>
                <div className="text-right text-[11px] text-gray-700">
                  <div>
                    {s.vcpu} vCPU / {s.ramGb} GB
                  </div>
                  <div>{s.role}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Storage */}
        <div className="panel p-4 space-y-2">
          <h3 className="font-semibold text-sm">Storage</h3>
          <p className="text-xs text-gray-600">
            Volumes, tiers, and server attachments.
          </p>
          <div className="mt-2 space-y-1 text-xs">
            {detail.storage.map((v) => (
              <div
                key={v.id}
                className="flex justify-between border-b pb-1 mb-1"
              >
                <div>
                  <div className="font-semibold text-sm">{v.id}</div>
                  <div className="text-[11px] text-gray-600">{v.type}</div>
                </div>
                <div className="text-right text-[11px] text-gray-700">
                  <div>{v.sizeGb} GB</div>
                  <div>Server: {v.attachedTo}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Network */}
        <div className="panel p-4 space-y-2">
          <h3 className="font-semibold text-sm">Network</h3>
          <p className="text-xs text-gray-600">
            VLANs and bandwidth relevant to this portfolio.
          </p>
          <div className="mt-2 space-y-1 text-xs">
            {detail.network.map((n) => (
              <div
                key={`${n.segment}-${n.vlan}`}
                className="flex justify-between border-b pb-1 mb-1"
              >
                <div>
                  <div className="font-semibold text-sm">{n.segment}</div>
                  <div className="text-[11px] text-gray-600">
                    VLAN {n.vlan}
                  </div>
                </div>
                <div className="text-right text-[11px] text-gray-700">
                  <div>{n.bandwidth}</div>
                  <div>{n.notes}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
