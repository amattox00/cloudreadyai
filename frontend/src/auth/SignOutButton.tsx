import React from "react";
import { useAuth } from "./AuthContext";
import { useNavigate } from "react-router-dom";

export default function SignOutButton() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <button
      onClick={handleLogout}
      className="px-4 py-2 rounded-md bg-red-600 text-white hover:bg-red-700"
    >
      Sign Out
    </button>
  );
}
