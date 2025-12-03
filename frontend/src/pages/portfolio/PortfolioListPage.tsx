import React from "react";
import { Link } from "react-router-dom";

type Portfolio = {
  id: string; // slug used in the URL
  name: string;
  code: string;
};

const PORTFOLIOS: Portfolio[] = [
  {
    id: "usda-assess-fy25",
    name: "USDA Assess FY25",
    code: "USDA-ASSESS-FY25",
  },
  {
    id: "cbp-cspd",
    name: "DHS CBP CSPD",
    code: "CBP-CSPD",
  },
];

export default function PortfolioListPage() {
  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold">Portfolios</h1>
        <p className="text-sm text-gray-600">
          Apps, servers, storage, and networks; summarized per run. Select a
          portfolio to open its assessment overview.
        </p>
      </header>

      <section className="panel p-0 divide-y">
        {PORTFOLIOS.map((p) => (
          <div
            key={p.id}
            className="flex items-center justify-between px-6 py-4"
          >
            <div className="space-y-0.5">
              <div className="text-base font-semibold">{p.name}</div>
              <div className="text-xs text-gray-600">{p.code}</div>
            </div>
            <div>
              <Link
                to={`/portfolio/${p.id}/overview`}
                className="text-sm font-semibold text-accent hover:underline"
              >
                Open
              </Link>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}
