import React from "react";
import { NavLink } from "react-router-dom";

export default function Sidebar() {
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
          to="/portfolio"
          className={({ isActive }) =>
            `block px-4 py-2 rounded ${
              isActive ? "bg-[var(--brand-accent)]" : "hover:bg-gray-700"
            }`
          }
        >
          Portfolio
        </NavLink>

        <NavLink
          to="/runs"
          className={({ isActive }) =>
            `block px-4 py-2 rounded ${
              isActive ? "bg-[var(--brand-accent)]" : "hover:bg-gray-700"
            }`
          }
        >
          Runs
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

        {/* === NEW MENU ITEMS === */}

        <NavLink
          to="/analysis"
          className={({ isActive }) =>
            `block px-4 py-2 rounded ${
              isActive ? "bg-[var(--brand-accent)]" : "hover:bg-gray-700"
            }`
          }
        >
          Analysis
        </NavLink>

        <NavLink
          to="/cost"
          className={({ isActive }) =>
            `block px-4 py-2 rounded ${
              isActive ? "bg-[var(--brand-accent)]" : "hover:bg-gray-700"
            }`
          }
        >
          Cost & TCO
        </NavLink>

        {/* ⭐ NEW: RECOMMENDATIONS LINK ⭐ */}
        <NavLink
          to="/recommendations"
          className={({ isActive }) =>
            `block px-4 py-2 rounded ${
              isActive ? "bg-[var(--brand-accent)]" : "hover:bg-gray-700"
            }`
          }
        >
          Recommendations
        </NavLink>

        {/* Settings */}
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
        <a
          href="/logout"
          className="block px-4 py-2 text-center rounded bg-[var(--brand-accent)] hover:opacity-90"
        >
          Sign Out
        </a>
      </div>

      <div className="text-xs mt-4 opacity-70">env: dev • instance</div>
    </aside>
  );
}
