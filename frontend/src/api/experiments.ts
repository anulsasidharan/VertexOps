import { apiFetch, type AuthHeaders } from "@/api/client";
import type { ExperimentListDto } from "@/api/types";

export async function fetchExperiments(auth: AuthHeaders): Promise<ExperimentListDto> {
  const res = await apiFetch("/experiments", { method: "GET", authHeaders: auth });
  if (!res.ok) {
    throw new Error(`Experiments list failed: ${res.status}`);
  }
  return (await res.json()) as ExperimentListDto;
}
