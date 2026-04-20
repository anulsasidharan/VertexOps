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
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md space-y-6">
        <header className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-indigo-600/20 border border-indigo-600/40 mb-4">
            <span className="text-2xl">⚡</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">Welcome to VertexOps</h1>
          <p className="mt-1 text-sm text-slate-400">
            Multi-cloud AI infrastructure platform
          </p>
        </header>

        {error ? (
          <div className="rounded-lg border border-red-900/60 bg-red-950/40 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        ) : null}

        {/* SSO buttons */}
        <div className="space-y-2">
          <button
            type="button"
            onClick={() => setError("SSO requires enterprise plan — use email/password below.")}
            className="w-full flex items-center justify-center gap-3 rounded-lg border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-medium text-slate-300 hover:bg-slate-800 transition-colors"
          >
            <span className="text-lg">🔵</span> Continue with Google
          </button>
          <button
            type="button"
            onClick={() => setError("SSO requires enterprise plan — use email/password below.")}
            className="w-full flex items-center justify-center gap-3 rounded-lg border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-medium text-slate-300 hover:bg-slate-800 transition-colors"
          >
            <span className="text-lg">🔷</span> Continue with Okta
          </button>
          <button
            type="button"
            onClick={() => setError("SSO requires enterprise plan — use email/password below.")}
            className="w-full flex items-center justify-center gap-3 rounded-lg border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-medium text-slate-300 hover:bg-slate-800 transition-colors"
          >
            <span className="text-lg">🪟</span> Continue with Azure AD
          </button>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex-1 h-px bg-slate-800" />
          <span className="text-xs text-slate-600 font-medium uppercase tracking-wider">or</span>
          <div className="flex-1 h-px bg-slate-800" />
        </div>

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

        <p className="text-center text-xs text-slate-600">
          API:{" "}
          <code className="rounded bg-slate-800 px-1 text-slate-500">{getApiBaseUrl()}</code>
        </p>
      </div>
    </div>
  );
}
