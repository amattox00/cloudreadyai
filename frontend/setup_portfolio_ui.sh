#!/bin/bash
cd ~/cloudreadyai/frontend

echo "📁 Creating folders..."
mkdir -p src/components
mkdir -p src/pages/portfolio/tabs

#######################################################
# 1. App.tsx
#######################################################
cat > src/App.tsx <<'TSX'
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import DashboardPage from "./pages/DashboardPage";
import PortfolioListPage from "./pages/portfolio/PortfolioListPage";
import PortfolioDetailLayout from "./pages/portfolio/PortfolioDetailLayout";
import PortfolioOverviewTab from "./pages/portfolio/tabs/PortfolioOverviewTab";
import PortfolioDiagramsTab from "./pages/portfolio/tabs/PortfolioDiagramsTab";
import PortfolioCostsTab from "./pages/portfolio/tabs/PortfolioCostsTab";
import PortfolioReportsTab from "./pages/portfolio/tabs/PortfolioReportsTab";
import RunsPage from "./pages/RunsPage";
import DiagramsPage from "./pages/DiagramsPage";
import SettingsPage from "./pages/SettingsPage";
import NotFoundPage from "./pages/NotFoundPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />

          <Route path="/portfolio" element={<PortfolioListPage />} />
          <Route path="/portfolio/:portfolioId" element={<PortfolioDetailLayout />}>
            <Route index element={<Navigate to="overview" replace />} />
            <Route path="overview" element={<PortfolioOverviewTab />} />
            <Route path="diagrams" element={<PortfolioDiagramsTab />} />
            <Route path="costs" element={<PortfolioCostsTab />} />
            <Route path="reports" element={<PortfolioReportsTab />} />
          </Route>

          <Route path="/runs" element={<RunsPage />} />
          <Route path="/diagrams" element={<DiagramsPage />} />
          <Route path="/settings" element={<SettingsPage />} />

          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
TSX

#######################################################
# 2. Layout + Components
#######################################################
cat > src/components/Layout.tsx <<'TSX'
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import Breadcrumbs from "./Breadcrumbs";

export default function Layout() {
  return (
    <div className="flex h-screen w-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Topbar />
        <div className="px-6 pt-4">
          <Breadcrumbs />
        </div>
        <main className="p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
TSX

cat > src/components/Sidebar.tsx <<'TSX'
import { NavLink } from "react-router-dom";

const linkCls = "block px-4 py-2 rounded-xl hover:bg-gray-100 transition";
const active = "bg-gray-200 font-semibold";

export default function Sidebar() {
  return (
    <aside className="w-64 border-r p-4 space-y-2">
      <div className="text-xl font-bold mb-4">CloudReadyAI</div>
      <NavLink to="/dashboard" className={({isActive}) => \`\${linkCls} \${isActive?active:""}\`}>Dashboard</NavLink>
      <NavLink to="/portfolio" className={({isActive}) => \`\${linkCls} \${isActive?active:""}\`}>Portfolio</NavLink>
      <NavLink to="/runs" className={({isActive}) => \`\${linkCls} \${isActive?active:""}\`}>Runs</NavLink>
      <NavLink to="/diagrams" className={({isActive}) => \`\${linkCls} \${isActive?active:""}\`}>Diagrams</NavLink>
      <NavLink to="/settings" className={({isActive}) => \`\${linkCls} \${isActive?active:""}\`}>Settings</NavLink>
    </aside>
  );
}
TSX

cat > src/components/Topbar.tsx <<'TSX'
export default function Topbar() {
  return (
    <header className="h-14 border-b px-6 flex items-center justify-between">
      <div className="font-medium">Portfolio</div>
      <div className="text-sm text-gray-500">env: dev • instance</div>
    </header>
  );
}
TSX

cat > src/components/Breadcrumbs.tsx <<'TSX'
import { Link, useLocation, useParams } from "react-router-dom";

export default function Breadcrumbs() {
  const loc = useLocation();
  const parts = loc.pathname.split("/").filter(Boolean);
  const { portfolioId } = useParams();

  const pathFor = (i: number) => "/" + parts.slice(0, i + 1).join("/");

  return (
    <nav className="text-sm text-gray-600">
      <Link to="/" className="hover:underline">Home</Link>
      {parts.map((p, i) => (
        <span key={i}>
          <span className="mx-2">/</span>
          <Link to={pathFor(i)} className="hover:underline">
            {p === portfolioId ? \`Portfolio \${portfolioId}\` : p}
          </Link>
        </span>
      ))}
    </nav>
  );
}
TSX

#######################################################
# 3. Portfolio pages
#######################################################
cat > src/pages/portfolio/PortfolioListPage.tsx <<'TSX'
import { Link } from "react-router-dom";

const mockPortfolios = [
  { id: "USDA-ASSESS-FY25", name: "USDA Assess FY25" },
  { id: "CBP-CSPD", name: "DHS CBP CSPD" },
];

export default function PortfolioListPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Portfolios</h1>
      <ul className="divide-y border rounded-xl">
        {mockPortfolios.map(p => (
          <li key={p.id} className="p-4 flex items-center justify-between">
            <div>
              <div className="font-medium">{p.name}</div>
              <div className="text-xs text-gray-500">{p.id}</div>
            </div>
            <Link to={\`/portfolio/\${p.id}\`} className="text-sm underline">Open</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
TSX

cat > src/pages/portfolio/PortfolioDetailLayout.tsx <<'TSX'
import { NavLink, Outlet, useParams } from "react-router-dom";

export default function PortfolioDetailLayout() {
  const { portfolioId } = useParams();

  const tabCls = "px-4 py-2 rounded-xl text-sm hover:bg-gray-100";
  const active = "bg-gray-200 font-semibold";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Portfolio: {portfolioId}</h1>
          <p className="text-sm text-gray-500">Tie all workstreams here.</p>
        </div>
      </div>

      <div className="flex gap-2 border-b pb-3">
        <NavLink end to="overview" className={({isActive}) => \`\${tabCls} \${isActive?active:""}\`}>Overview</NavLink>
        <NavLink to="diagrams" className={({isActive}) => \`\${tabCls} \${isActive?active:""}\`}>Diagrams</NavLink>
        <NavLink to="costs" className={({isActive}) => \`\${tabCls} \${isActive?active:""}\`}>Costs</NavLink>
        <NavLink to="reports" className={({isActive}) => \`\${tabCls} \${isActive?active:""}\`}>Reports</NavLink>
      </div>

      <Outlet />
    </div>
  );
}
TSX

#######################################################
# 4. Portfolio tab files
#######################################################
cat > src/pages/portfolio/tabs/PortfolioOverviewTab.tsx <<'TSX'
export default function PortfolioOverviewTab() {
  return (
    <section className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="border rounded-xl p-4">Summary KPIs</div>
        <div className="border rounded-xl p-4">Recent Runs</div>
        <div className="border rounded-xl p-4">Open Actions</div>
      </div>
    </section>
  );
}
TSX

cat > src/pages/portfolio/tabs/PortfolioDiagramsTab.tsx <<'TSX'
import { Link, useParams } from "react-router-dom";

export default function PortfolioDiagramsTab() {
  const { portfolioId } = useParams();
  return (
    <section className="space-y-4">
      <div className="border rounded-xl p-4">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">Diagrams</h2>
          <Link to="/diagrams" className="text-sm underline">Open Global Diagrams Tool</Link>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Generate or package diagrams scoped to <strong>{portfolioId}</strong>.
        </p>
      </div>
    </section>
  );
}
TSX

cat > src/pages/portfolio/tabs/PortfolioCostsTab.tsx <<'TSX'
export default function PortfolioCostsTab() {
  return (
    <section className="space-y-4">
      <div className="border rounded-xl p-4">
        <h2 className="font-semibold">Cost Estimates</h2>
        <p className="text-sm text-gray-600 mt-2">
          Hook this panel to /v1/cost endpoints for this portfolio’s runs.
        </p>
      </div>
    </section>
  );
}
TSX

cat > src/pages/portfolio/tabs/PortfolioReportsTab.tsx <<'TSX'
export default function PortfolioReportsTab() {
  return (
    <section className="space-y-4">
      <div className="border rounded-xl p-4">
        <h2 className="font-semibold">Reports & Packaging</h2>
        <p className="text-sm text-gray-600 mt-2">
          Connect to your Phase 9 deliverables packaging engine here.
        </p>
      </div>
    </section>
  );
}
TSX

#######################################################
# 5. Supporting pages
#######################################################
cat > src/pages/DashboardPage.tsx <<'TSX'
export default function DashboardPage(){ return <div>Dashboard</div>; }
TSX

cat > src/pages/RunsPage.tsx <<'TSX'
export default function RunsPage(){ return <div>Runs</div>; }
TSX

cat > src/pages/SettingsPage.tsx <<'TSX'
export default function SettingsPage(){ return <div>Settings</div>; }
TSX

cat > src/pages/NotFoundPage.tsx <<'TSX'
export default function NotFoundPage(){ return <div>Not Found</div>; }
TSX

#######################################################
# 6. main.tsx
#######################################################
cat > src/main.tsx <<'TSX'
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
TSX

#######################################################
# 7. Install dependencies and restart
#######################################################
echo "📦 Installing react-router-dom..."
npm install react-router-dom

echo "🚀 Restarting frontend service..."
sudo systemctl restart cloudready-frontend
sudo systemctl status cloudready-frontend --no-pager

echo "✅ Portfolio UI setup complete!"
