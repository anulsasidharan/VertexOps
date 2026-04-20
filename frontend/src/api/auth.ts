import { apiFetch, type AuthHeaders } from "@/api/client";
import type { ApiKeyDto, ApiKeyCreateResponse } from "@/api/types";

export async function createApiKey(
  auth: AuthHeaders,
  label?: string
): Promise<ApiKeyCreateResponse> {
  const res = await apiFetch("/auth/api-keys", {
    method: "POST",
    authHeaders: auth,
    body: JSON.stringify({ label: label ?? null }),
  });
  if (!res.ok) throw new Error(`Create API key failed: ${res.status}`);
  return (await res.json()) as ApiKeyCreateResponse;
}

export async function listApiKeys(auth: AuthHeaders): Promise<ApiKeyDto[]> {
  const res = await apiFetch("/auth/api-keys", { method: "GET", authHeaders: auth });
  if (!res.ok) throw new Error(`List API keys failed: ${res.status}`);
  return (await res.json()) as ApiKeyDto[];
}

export async function revokeApiKey(auth: AuthHeaders, keyId: string): Promise<void> {
  const res = await apiFetch(`/auth/api-keys/${keyId}`, {
    method: "DELETE",
    authHeaders: auth,
  });
  if (!res.ok && res.status !== 204) throw new Error(`Revoke API key failed: ${res.status}`);
}
