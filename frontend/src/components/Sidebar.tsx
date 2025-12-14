import React from "react";
import { NavLink, useNavigate } from "react-router-dom";

export default function Sidebar() {
  const nav = useNavigate();

  const signOut = () => {
    localStorage.removeItem("authToken");
    nav("/", { replace: true }); // back to Marketing
  };

  return (
    <aside
      className="w-64 h-full flex flex-col p-4 text-white"
      style={{ background: "var(--brand-bg-sidebar)" }}
    >
      {/* Logo */}
      <div className="text-2xl font-bold mb-8">CloudReadyAI</div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1">
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            `block px-4 py-2 rounded ${
              isActive ? "bg-[var(--brand-accent)]" : "hover:bg-gray-700"
            }`
          }
        >
          Dashboard
        </NavLink>

        <NavLink
          to="/runs"
          className={({ isActive }) =>
            `block px-4 py-2 rounded ${
              isActive ? "bg-[var(--brand-accent)]" : "hover:bg-gray-700"
            }`
          }
        >
          Assessments
        </NavLink>

        <NavLink
          to="/portfolio"
          className={({ isActive }) =>
            `block px-4 py-2 rounded ${
              isActive ? "bg-[var(--brand-accent)]" : "hover:bg-gray-700"
            }`
          }
        >
          Clients &amp; Portfolios
        </NavLink>

        <NavLink
          to="/diagrams"
          className={({ isActive }) =>
            `block px-4 py-2 rounded ${
              isActive ? "bg-[var(--brand-accent)]" : "hover:bg-gray-700"
            }`
          }
        >
          Diagrams
        </NavLink>

        <NavLink
          to="/analysis"
          className={({ isActive }) =>
            `block px-4 py-2 rounded ${
              isActive ? "bg-[var(--brand-accent)]" : "hover:bg-gray-700"
            }`
          }
        >
          Insights
        </NavLink>

        <NavLink
          to="/cost"
          className={({ isActive }) =>
            `block px-4 py-2 rounded ${
              isActive ? "bg-[var(--brand-accent)]" : "hover:bg-gray-700"
            }`
          }
        >
          Cost Modeling
        </NavLink>

        <NavLink
          to="/recommendations"
          className={({ isActive }) =>
            `block px-4 py-2 rounded ${
              isActive ? "bg-[var(--brand-accent)]" : "hover:bg-gray-700"
            }`
          }
        >
          Migration Strategy
        </NavLink>

        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `block px-4 py-2 rounded ${
              isActive ? "bg-[var(--brand-accent)]" : "hover:bg-gray-700"
            }`
          }
        >
          Settings
        </NavLink>
      </nav>

      {/* Sign Out */}
      <div className="mt-8">
        <button
          type="button"
          onClick={signOut}
          className="w-full block px-4 py-2 text-center rounded bg-[var(--brand-accent)] hover:opacity-90"
        >
          Sign Out
        </button>
      </div>

      <div className="text-xs mt-4 opacity-70">env: dev • instance</div>
    </aside>
  );
}
