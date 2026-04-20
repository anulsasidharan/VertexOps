import { apiFetch, type AuthHeaders } from "@/api/client";
import type { DocumentDto, DocumentListDto, PrepareUploadResponse } from "@/api/types";

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
  if (!res.ok) throw new Error(`Documents list failed: ${res.status}`);
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
  if (!res.ok) throw new Error(`Document fetch failed: ${res.status}`);
  return (await res.json()) as DocumentDto;
}

export async function prepareUpload(
  auth: AuthHeaders,
  payload: { filename: string; content_type?: string; title?: string; format?: string; language?: string }
): Promise<PrepareUploadResponse> {
  const res = await apiFetch("/documents/upload-url", {
    method: "POST",
    authHeaders: auth,
    body: JSON.stringify({ content_type: "application/octet-stream", ...payload }),
  });
  if (!res.ok) throw new Error(`Prepare upload failed: ${res.status}`);
  return (await res.json()) as PrepareUploadResponse;
}

export async function completeUpload(
  auth: AuthHeaders,
  documentId: string,
  content_hash?: string
): Promise<DocumentDto> {
  const res = await apiFetch(`/documents/${documentId}/complete`, {
    method: "POST",
    authHeaders: auth,
    body: JSON.stringify({ content_hash: content_hash ?? null }),
  });
  if (!res.ok) throw new Error(`Complete upload failed: ${res.status}`);
  return (await res.json()) as DocumentDto;
}

export async function deleteDocument(
  auth: AuthHeaders,
  documentId: string
): Promise<void> {
  const res = await apiFetch(`/documents/${documentId}`, {
    method: "DELETE",
    authHeaders: auth,
  });
  if (!res.ok && res.status !== 204) throw new Error(`Delete failed: ${res.status}`);
}
