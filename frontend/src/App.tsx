import { BrowserRouter, Routes, Route, useLocation, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import AuthGate from "./components/AuthGate";

// Pages
import MarketingPage from "./pages/MarketingPage";
import LoginPage from "./pages/LoginPage";

import DashboardPage from "./pages/DashboardPage";
import PortfolioPage from "./pages/PortfolioPage";
import PortfolioDetailPage from "./pages/PortfolioDetailPage";
import RunsPage from "./pages/RunsPage";
import DiagramsPage from "./pages/DiagramsPage";
import AnalysisPage from "./pages/AnalysisPage";
import CostPage from "./pages/CostPage";
import RecommendationsPage from "./pages/RecommendationsPage";
import RunDetailPage from "./pages/runs/RunDetailPage";
import NewRunPage from "./pages/runs/NewRunPage";

function Shell({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const isPublic =
    location.pathname === "/" ||
    location.pathname.startsWith("/login");

  if (isPublic) {
    return <>{children}</>;
  }

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <Sidebar />
      <div style={{ flex: 1, overflow: "auto" }}>{children}</div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Shell>
        <Routes>
          {/* Public */}
          <Route path="/" element={<MarketingPage />} />
          <Route path="/login" element={<LoginPage />} />

          {/* App (protected) */}
          <Route
            path="/dashboard"
            element={
              <AuthGate>
                <DashboardPage />
              </AuthGate>
            }
          />

          <Route
            path="/portfolio"
            element={
              <AuthGate>
                <PortfolioPage />
              </AuthGate>
            }
          />
          <Route
            path="/portfolio/:id"
            element={
              <AuthGate>
                <PortfolioDetailPage />
              </AuthGate>
            }
          />

          <Route
            path="/runs"
            element={
              <AuthGate>
                <RunsPage />
              </AuthGate>
            }
          />
          <Route
            path="/runs/new"
            element={
              <AuthGate>
                <NewRunPage />
              </AuthGate>
            }
          />
          <Route
            path="/runs/:runId"
            element={
              <AuthGate>
                <RunDetailPage />
              </AuthGate>
            }
          />

          <Route
            path="/diagrams"
            element={
              <AuthGate>
                <DiagramsPage />
              </AuthGate>
            }
          />

          <Route
            path="/analysis"
            element={
              <AuthGate>
                <AnalysisPage />
              </AuthGate>
            }
          />

          <Route
            path="/cost"
            element={
              <AuthGate>
                <CostPage />
              </AuthGate>
            }
          />

          <Route
            path="/recommendations"
            element={
              <AuthGate>
                <RecommendationsPage />
              </AuthGate>
            }
          />

          {/* Simple fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Shell>
    </BrowserRouter>
  );
}
