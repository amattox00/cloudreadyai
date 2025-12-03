import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function LoginPage() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      // TODO: swap this stub for your real backend call:
      // const res = await fetch("/auth/login", { ... });
      // if (!res.ok) throw new Error("Bad credentials");
      // const { token } = await res.json();
      const token = "dev-token"; // stub for now
      localStorage.setItem("authToken", token);
      nav("/dashboard", { replace: true });
    } catch (e: any) {
      setErr(e?.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      minHeight: "100vh",
      display: "grid",
      placeItems: "center",
      background: "var(--brand-bg-main)"
    }}>
      <div className="rounded-2xl" style={{
        width: "100%",
        maxWidth: 420,
        background: "var(--brand-bg-card)",
        border: "1px solid var(--brand-border)",
        padding: "1.5rem"
      }}>
        <div style={{ fontSize: 26, fontWeight: 800, color: "var(--brand-accent)", marginBottom: 10 }}>
          CloudReadyAI
        </div>
        <div style={{ color: "var(--brand-text-muted)", marginBottom: 20 }}>
          Sign in to continue
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-sm" style={{ color: "var(--brand-text-muted)" }}>Email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@company.com"
              required
              style={{ width: "100%" }}
            />
          </div>
          <div>
            <label className="block text-sm" style={{ color: "var(--brand-text-muted)" }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              style={{ width: "100%" }}
            />
          </div>

          {err && <div style={{ color: "#b91c1c", fontSize: 12 }}>{err}</div>}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
            style={{ width: "100%" }}
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div style={{ marginTop: 16, fontSize: 12, color: "var(--brand-text-muted)" }}>
          <span>Need an account? </span>
          <Link to="#" style={{ color: "var(--brand-accent)" }}>Contact admin</Link>
        </div>
      </div>
    </div>
  );
}
