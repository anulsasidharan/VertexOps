/** Central API base URL — dev uses Vite proxy ``/api`` → backend. */

export function getApiBaseUrl(): string {
  const raw = import.meta.env.VITE_API_BASE_URL?.trim();
  if (raw) {
    return raw.replace(/\/$/, "");
  }
  return "/api/v1";
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
