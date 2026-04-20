/** Central API base URL — dev uses Vite ``server.proxy`` / ``preview.proxy`` for ``/api`` → backend. */

function _isLocalhostPort3000(urlLike: string): boolean {
  const s = urlLike.replace(/\/+$/, "");
  const withScheme = /^https?:\/\//i.test(s) ? s : `http://${s}`;
  try {
    const u = new URL(withScheme);
    if (u.hostname !== "localhost" && u.hostname !== "127.0.0.1") {
      return false;
    }
    return u.port === "3000";
  } catch {
    return false;
  }
}

/**
 * Normalize ``VITE_API_BASE_URL`` / default so requests hit ``/api/v1/...`` on the API.
 * Exported for tests — pass ``opts.dev`` to assert dev-only behaviour without ``import.meta``.
 */
export function normalizeApiBaseUrl(
  raw: string | undefined,
  opts?: { dev?: boolean },
): string {
  const trimmed = raw?.trim();
  if (!trimmed) {
    return "/api/v1";
  }
  const isDev = opts?.dev ?? import.meta.env.DEV;
  // Port 3000 is the Next.js marketing app in this monorepo, not FastAPI (8000). Requests there 404.
  if (isDev && _isLocalhostPort3000(trimmed)) {
    console.warn(
      "[VertexOps] VITE_API_BASE_URL points at localhost:3000 (Next.js landing). Using same-origin /api/v1 so the Vite dev proxy can reach the API on port 8000."
    );
    return "/api/v1";
  }

  let base = trimmed.replace(/\/+$/, "");
  // Versioned API lives under /api/v1 (see backend.main). Bare origins often mis-set as
  // http://127.0.0.1:8000 which would otherwise produce /auth/register → 404.
  if (/^https?:\/\//i.test(base) && !/\/api\/v\d+$/i.test(base)) {
    base = `${base}/api/v1`;
  }
  if (base === "/api") {
    return "/api/v1";
  }
  return base;
}

export function getApiBaseUrl(): string {
  return normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL);
}

export type AuthHeaders = Record<string, string>;

export function buildAuthHeaders(
  mode: "jwt" | "api_key" | "none",
  jwt: string | null,
  apiKey: string | null
): AuthHeaders {
  if (mode === "jwt" && jwt) {
    return { Authorization: `Bearer ${jwt}` };
  }
  if (mode === "api_key" && apiKey) {
    return { "X-API-Key": apiKey };
  }
  return {};
}

export async function apiFetch(
  path: string,
  init: RequestInit & { authHeaders?: AuthHeaders } = {}
): Promise<Response> {
  const base = getApiBaseUrl();
  const url = path.startsWith("http") ? path : `${base}${path.startsWith("/") ? "" : "/"}${path}`;
  const { authHeaders, headers: initHeaders, ...rest } = init;
  const headers = new Headers(initHeaders);
  if (authHeaders) {
    for (const [k, v] of Object.entries(authHeaders)) {
      headers.set(k, v);
    }
  }
  if (!headers.has("Content-Type") && init.body && typeof init.body === "string") {
    headers.set("Content-Type", "application/json");
  }
  return fetch(url, { ...rest, headers });
}
