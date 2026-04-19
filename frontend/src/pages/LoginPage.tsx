import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { apiFetch, getApiBaseUrl } from "@/api/client";
import { useAuthSession } from "@/context/AuthSessionContext";

type ApiErrorBody = { error?: { message?: string } };

function messageFromErrorBody(body: unknown): string | null {
  if (!body || typeof body !== "object") return null;
  const msg = (body as ApiErrorBody).error?.message;
  return typeof msg === "string" && msg.trim() ? msg.trim() : null;
}

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from ?? "/";

  const { setJwtSession, setApiKeySession } = useAuthSession();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onJwtLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await apiFetch("/auth/token", {
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
        if (res.status === 401) {
          setError(
            apiMsg ??
              "Invalid email or password. If you have no account yet, from the repository root run: python -m scripts.bootstrap_dev_user (requires PostgreSQL, migrations, and APP_ENV=development)."
          );
        } else if (res.status === 422) {
          setError(apiMsg ?? "Check that the email is valid and fields are filled.");
        } else if (res.status === 502 || res.status === 503 || res.status === 504) {
          setError(
            apiMsg ??
              "Cannot reach the API (bad gateway). Start the backend on port 8000 from the repo root, e.g. uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000. The Vite dev server proxies /api to localhost:8000."
          );
        } else if (res.status >= 500) {
          setError(
            apiMsg ??
              "Server error — check the API terminal logs, DATABASE_URL, and that alembic upgrade head has been applied."
          );
        } else {
          setError(apiMsg ?? `Sign-in failed (HTTP ${res.status}).`);
        }
        return;
      }
      const data = body as { access_token?: string };
      if (!data?.access_token) {
        setError("Unexpected response: missing access_token.");
        return;
      }
      setJwtSession(data.access_token);
      navigate(from, { replace: true });
    } catch {
      setError("Could not reach API. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  function onApiKeyLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const trimmed = apiKey.trim();
    if (!trimmed) {
      setError("Enter an API key.");
      return;
    }
    setApiKeySession(trimmed);
    navigate(from, { replace: true });
  }

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-8 px-4 py-16">
      <header>
        <h1 className="text-2xl font-semibold">VertexOps</h1>
        <p className="mt-1 text-sm text-slate-400">
          Sign in with email and password (JWT) or paste an API key. API base:{" "}
          <code className="rounded bg-slate-800 px-1">{getApiBaseUrl()}</code>
        </p>
      </header>

      {error ? (
        <div className="rounded border border-red-900/60 bg-red-950/40 px-3 py-2 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-4">
        <h2 className="mb-3 text-sm font-medium text-slate-300">JWT (email / password)</h2>
        <form className="flex flex-col gap-3" onSubmit={onJwtLogin}>
          <input
            className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            type="email"
            autoComplete="username"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            type="password"
            autoComplete="current-password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {loading ? "Signing in…" : "Sign in with JWT"}
          </button>
        </form>
      </section>

      <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-4">
        <h2 className="mb-3 text-sm font-medium text-slate-300">API key</h2>
        <form className="flex flex-col gap-3" onSubmit={onApiKeyLogin}>
          <input
            className="rounded border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-sm"
            type="password"
            autoComplete="off"
            placeholder="vops_…"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
          <button
            type="submit"
            className="rounded border border-slate-600 px-3 py-2 text-sm font-medium text-slate-100 hover:bg-slate-800"
          >
            Continue with API key
          </button>
        </form>
      </section>
    </div>
  );
}
