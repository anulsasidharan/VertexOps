import { apiFetch, type AuthHeaders } from "@/api/client";
import type { ExperimentDto, ExperimentListDto } from "@/api/types";

export async function fetchExperiments(auth: AuthHeaders): Promise<ExperimentListDto> {
  const res = await apiFetch("/experiments", { method: "GET", authHeaders: auth });
  if (!res.ok) throw new Error(`Experiments list failed: ${res.status}`);
  return (await res.json()) as ExperimentListDto;
}

export async function fetchExperiment(auth: AuthHeaders, id: string): Promise<ExperimentDto> {
  const res = await apiFetch(`/experiments/${id}`, { method: "GET", authHeaders: auth });
  if (!res.ok) throw new Error(`Experiment fetch failed: ${res.status}`);
  return (await res.json()) as ExperimentDto;
}

export async function createExperiment(
  auth: AuthHeaders,
  payload: { name: string; description?: string; index_id?: string; config?: Record<string, unknown> }
): Promise<ExperimentDto> {
  const res = await apiFetch("/experiments", {
    method: "POST",
    authHeaders: auth,
    body: JSON.stringify({ config: {}, ...payload }),
  });
  if (!res.ok) throw new Error(`Create experiment failed: ${res.status}`);
  return (await res.json()) as ExperimentDto;
}

export async function kickoffRun(
  auth: AuthHeaders,
  experimentId: string,
  run_config: Record<string, unknown> = {}
): Promise<{ id: string; experiment_id: string; status: string }> {
  const res = await apiFetch(`/experiments/${experimentId}/run`, {
    method: "POST",
    authHeaders: auth,
    body: JSON.stringify({ run_config }),
  });
  if (!res.ok) throw new Error(`Kickoff run failed: ${res.status}`);
  return (await res.json()) as { id: string; experiment_id: string; status: string };
}
