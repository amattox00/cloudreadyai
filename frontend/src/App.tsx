import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";

// Pages
import DashboardPage from "./pages/DashboardPage";
import PortfolioPage from "./pages/PortfolioPage";
import PortfolioDetailPage from "./pages/PortfolioDetailPage";
import RunsPage from "./pages/RunsPage";
import DiagramsPage from "./pages/DiagramsPage";
import AnalysisPage from "./pages/AnalysisPage";
import CostPage from "./pages/CostPage";
import RecommendationsPage from "./pages/RecommendationsPage";
import RunDetailPage from "./pages/runs/RunDetailPage";

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: "flex", height: "100vh" }}>
        <Sidebar />

        <div style={{ flex: 1, overflow: "auto" }}>
          <Routes>
            <Route path="/" element={<DashboardPage />} />

            <Route path="/dashboard" element={<DashboardPage />} />

            <Route path="/portfolio" element={<PortfolioPage />} />
            <Route path="/portfolio/:id" element={<PortfolioDetailPage />} />

            <Route path="/runs" element={<RunsPage />} />
            <Route path="/runs/:runId" element={<RunDetailPage />} />

            <Route path="/diagrams" element={<DiagramsPage />} />

            <Route path="/analysis" element={<AnalysisPage />} />

            <Route path="/cost" element={<CostPage />} />

            {/* ⭐ NEW ROUTE – RECOMMENDATIONS ⭐ */}
            <Route
              path="/recommendations"
              element={<RecommendationsPage />}
            />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
