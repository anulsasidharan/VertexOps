import { apiFetch, type AuthHeaders } from "@/api/client";
import type { DocumentDto, DocumentListDto } from "@/api/types";

export async function fetchDocuments(
  auth: AuthHeaders,
  params: { status?: string; limit?: number; offset?: number } = {}
): Promise<DocumentListDto> {
  const q = new URLSearchParams();
  if (params.status) q.set("status", params.status);
  if (params.limit != null) q.set("limit", String(params.limit));
  if (params.offset != null) q.set("offset", String(params.offset));
  const suffix = q.toString() ? `?${q}` : "";
  const res = await apiFetch(`/documents${suffix}`, {
    method: "GET",
    authHeaders: auth,
  });
  if (!res.ok) {
    throw new Error(`Documents list failed: ${res.status}`);
  }
  return (await res.json()) as DocumentListDto;
}

export async function fetchDocument(
  auth: AuthHeaders,
  documentId: string
): Promise<DocumentDto> {
  const res = await apiFetch(`/documents/${documentId}`, {
    method: "GET",
    authHeaders: auth,
  });
  if (!res.ok) {
    throw new Error(`Document fetch failed: ${res.status}`);
  }
  return (await res.json()) as DocumentDto;
}
