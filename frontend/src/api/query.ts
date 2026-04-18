import { apiFetch, type AuthHeaders } from "@/api/client";
import type { QueryResponseDto } from "@/api/types";

export async function runQuery(
  auth: AuthHeaders,
  body: {
    question: string;
    index_id: string;
    top_k?: number;
    min_score?: number;
    template_name?: string;
    max_tokens?: number;
    temperature?: number;
  }
): Promise<QueryResponseDto> {
  const res = await apiFetch("/query", {
    method: "POST",
    authHeaders: auth,
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`Query failed: ${res.status}`);
  }
  return (await res.json()) as QueryResponseDto;
}
