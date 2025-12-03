// src/components/NavBar.tsx
import React from "react";
import { NavLink, useNavigate } from "react-router-dom";

const baseLink =
  "px-3 py-2 rounded-md text-sm font-medium transition hover:bg-slate-800";
const activeLink = "bg-slate-900 text-white";
const inactiveLink = "text-slate-300";

export const NavBar: React.FC = () => {
  const navigate = useNavigate();

  const links = [
    { to: "/", label: "Dashboard" },
    { to: "/portfolio", label: "Portfolio" },
    { to: "/diagrams", label: "Diagrams" },
    { to: "/uploads", label: "Uploads" },
  ];

  const handleSignOut = () => {
    localStorage.removeItem("authToken");
    navigate("/login", { replace: true });
  };

  return (
    <header className="border-b border-slate-800 bg-slate-950/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        {/* Left: logo / title */}
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-400" />
          <span className="text-sm font-semibold tracking-wide">
            CloudReadyAI
          </span>
          <span className="ml-2 rounded-full border border-emerald-500/40 px-2 py-0.5 text-[10px] uppercase tracking-wide text-emerald-300/80">
            Prototype
          </span>
        </div>

        {/* Right: nav links + sign out */}
        <nav className="flex items-center gap-3">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              className={({ isActive }) =>
                [
                  baseLink,
                  isActive ? activeLink : inactiveLink,
                ].join(" ")
              }
            >
              {link.label}
            </NavLink>
          ))}

          <button
            type="button"
            onClick={handleSignOut}
            className="ml-4 rounded-md border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 hover:text-white"
          >
            Sign Out
          </button>
        </nav>
      </div>
    </header>
  );
};
