import React from "react";
import { Navigate, useLocation } from "react-router-dom";

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const token = localStorage.getItem("authToken");

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <>{children}</>;
}
