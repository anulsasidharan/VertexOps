import { apiFetch, type AuthHeaders } from "@/api/client";
import type { EvaluationDetailDto } from "@/api/types";

export type EvalCaseInput = {
  question: string;
  predicted?: string;
  ground_truth?: string | null;
  context?: string | null;
  latency_ms?: number;
  token_count?: number;
};

export async function createEvaluation(
  auth: AuthHeaders,
  body: { experiment_id: string; cases: EvalCaseInput[] }
): Promise<{ id: string; status: string }> {
  const res = await apiFetch("/evaluations", {
    method: "POST",
    authHeaders: auth,
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`Create evaluation failed: ${res.status}`);
  }
  return (await res.json()) as { id: string; status: string };
}

export async function fetchEvaluation(
  auth: AuthHeaders,
  evaluationId: string
): Promise<EvaluationDetailDto> {
  const res = await apiFetch(`/evaluations/${evaluationId}`, {
    method: "GET",
    authHeaders: auth,
  });
  if (!res.ok) {
    throw new Error(`Evaluation fetch failed: ${res.status}`);
  }
  return (await res.json()) as EvaluationDetailDto;
}

export async function downloadEvaluationReport(
  auth: AuthHeaders,
  evaluationId: string,
  format: "json" | "html"
): Promise<void> {
  const q = format === "html" ? "?format=html" : "";
  const res = await apiFetch(`/evaluations/${evaluationId}/report${q}`, {
    method: "GET",
    authHeaders: auth,
  });
  if (!res.ok) {
    throw new Error(`Report download failed: ${res.status}`);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = format === "html" ? `eval-${evaluationId}.html` : `eval-${evaluationId}.json`;
  a.click();
  URL.revokeObjectURL(url);
}
