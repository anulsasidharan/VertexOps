import { apiFetch, type AuthHeaders } from "@/api/client";
import type { IndexDto, IndexListDto } from "@/api/types";

export async function fetchIndexes(auth: AuthHeaders): Promise<IndexListDto> {
  const res = await apiFetch("/indexes", { method: "GET", authHeaders: auth });
  if (!res.ok) {
    throw new Error(`Indexes list failed: ${res.status}`);
  }
  return (await res.json()) as IndexListDto;
}

export async function createIndex(
  auth: AuthHeaders,
  body: { name: string; vector_backend?: string; namespace?: string | null }
): Promise<IndexDto> {
  const res = await apiFetch("/indexes", {
    method: "POST",
    authHeaders: auth,
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`Index create failed: ${res.status}`);
  }
  return (await res.json()) as IndexDto;
}

export async function rebuildIndex(
  auth: AuthHeaders,
  indexId: string
): Promise<IndexDto> {
  const res = await apiFetch(`/indexes/${indexId}/rebuild`, {
    method: "POST",
    authHeaders: auth,
  });
  if (!res.ok) {
    throw new Error(`Index rebuild failed: ${res.status}`);
  }
  return (await res.json()) as IndexDto;
}
