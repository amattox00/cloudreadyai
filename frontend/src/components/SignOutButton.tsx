import React from "react";

export default function SignOutButton() {
  const handleSignOut = () => {
    // Clear any saved auth/session tokens
    localStorage.removeItem("authToken");
    sessionStorage.clear();

    // Redirect to login page (hard reload to reset app state)
    window.location.assign("/login");
  };

  return (
    <button
      onClick={handleSignOut}
      className="w-full mt-4 font-semibold py-2 rounded-lg transition"
      style={{
        backgroundColor: "var(--brand-accent)",
        color: "white",
        border: "none",
        fontSize: "1rem",
      }}
    >
      Sign Out
    </button>
  );
}
