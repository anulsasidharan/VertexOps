import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { apiFetch, getApiBaseUrl } from "@/api/client";
import { useAuthSession } from "@/context/AuthSessionContext";

type ApiErrorBody = { error?: { message?: string } };

function messageFromErrorBody(body: unknown): string | null {
  if (!body || typeof body !== "object") return null;
  const msg = (body as ApiErrorBody).error?.message;
  return typeof msg === "string" && msg.trim() ? msg.trim() : null;
}

export function RegisterPage() {
  const navigate = useNavigate();
  const { setJwtSession } = useAuthSession();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onRegister(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setLoading(true);
    try {
      const res = await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      let body: unknown = null;
      try {
        body = await res.json();
      } catch {
        /* non-JSON body */
      }
      if (!res.ok) {
        const apiMsg = messageFromErrorBody(body);
        if (res.status === 403) {
          setError(
            apiMsg ??
              "Public sign-up is disabled on this server (ALLOW_PUBLIC_SIGNUP=false). Ask an administrator for access."
          );
        } else if (res.status === 409) {
          setError(apiMsg ?? "An account with this email already exists. Try signing in instead.");
        } else if (res.status === 422) {
          setError(apiMsg ?? "Check that the email is valid and the password meets requirements (8+ characters).");
        } else if (res.status === 404) {
          setError(
            apiMsg ??
              "Registration URL not found (404). Common causes: (1) VITE_API_BASE_URL points at port 3000 (Next landing) instead of the API on 8000 — remove it or use http://127.0.0.1:8000; (2) API not restarted after upgrading; (3) open the dashboard on port 5173 (npm run dev in frontend/), not the landing site, for sign-up. Confirm POST /api/v1/auth/register exists at http://127.0.0.1:8000/docs."
          );
        } else if (res.status === 502 || res.status === 503 || res.status === 504) {
          setError(
            apiMsg ??
              "Cannot reach the API. Start the FastAPI server on port 8000 (see repo README or npm run start:api from frontend/)."
          );
        } else if (res.status >= 500) {
          setError(apiMsg ?? "Server error — check the API logs and database configuration.");
        } else {
          setError(apiMsg ?? `Registration failed (HTTP ${res.status}).`);
        }
        return;
      }
      const data = body as { access_token?: string };
      if (!data?.access_token) {
        setError("Unexpected response: missing access_token.");
        return;
      }
      setJwtSession(data.access_token);
      navigate("/", { replace: true });
    } catch {
      setError(
        "Could not reach the API. Start it on port 8000 (uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 from the repo root, or npm run start:api from frontend/)."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md space-y-6">
        <header className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-indigo-600/20 border border-indigo-600/40 mb-4">
            <span className="text-2xl">⚡</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">Create your VertexOps account</h1>
          <p className="mt-1 text-sm text-slate-400">Use your work email and a strong password</p>
        </header>

        {error ? (
          <div className="rounded-lg border border-red-900/60 bg-red-950/40 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        ) : null}

        <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-4">
          <form className="flex flex-col gap-3" onSubmit={onRegister}>
            <input
              className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              type="email"
              autoComplete="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              type="password"
              autoComplete="new-password"
              placeholder="Password (8+ characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
            />
            <input
              className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              type="password"
              autoComplete="new-password"
              placeholder="Confirm password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              minLength={8}
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
            >
              {loading ? "Creating account…" : "Create account"}
            </button>
          </form>
        </section>

        <p className="text-center text-sm text-slate-400">
          Already have an account?{" "}
          <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-medium">
            Sign in
          </Link>
        </p>

        <p className="text-center text-xs text-slate-600">
          API: <code className="rounded bg-slate-800 px-1 text-slate-500">{getApiBaseUrl()}</code>
        </p>
      </div>
    </div>
  );
}
