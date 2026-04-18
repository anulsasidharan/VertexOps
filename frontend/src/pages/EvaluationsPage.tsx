import { FormEvent, useCallback, useEffect, useState } from "react";

import { createEvaluation, downloadEvaluationReport, fetchEvaluation } from "@/api/evaluations";
import { fetchExperiments } from "@/api/experiments";
import { EvaluationRunSummary } from "@/components/evaluation/EvaluationRunSummary";
import type { EvaluationDetailDto, ExperimentDto } from "@/api/types";
import { useAuthSession } from "@/context/AuthSessionContext";
import { usePolling } from "@/hooks/usePolling";

const TERMINAL = new Set(["completed", "failed"]);

export function EvaluationsPage() {
  const { getAuthHeaders } = useAuthSession();
  const [experiments, setExperiments] = useState<ExperimentDto[]>([]);
  const [experimentId, setExperimentId] = useState("");
  const [casesJson, setCasesJson] = useState(
    '[{"question":"What is VertexOps?","predicted":"A platform.","ground_truth":"LLMOps platform"}]'
  );
  const [activeId, setActiveId] = useState<string | null>(null);
  const [detail, setDetail] = useState<EvaluationDetailDto | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const loadExperiments = useCallback(async () => {
    try {
      const data = await fetchExperiments(getAuthHeaders());
      setExperiments(data.items);
    } catch {
      /* optional */
    }
  }, [getAuthHeaders]);

  useEffect(() => {
    void loadExperiments();
  }, [loadExperiments]);

  useEffect(() => {
    if (experimentId || experiments.length === 0) return;
    setExperimentId(experiments[0].id);
  }, [experimentId, experiments]);

  const refreshDetail = useCallback(async () => {
    if (!activeId) return;
    try {
      const d = await fetchEvaluation(getAuthHeaders(), activeId);
      setDetail(d);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load evaluation");
    }
  }, [activeId, getAuthHeaders]);

  usePolling(refreshDetail, 2500, !!activeId && !!detail && !TERMINAL.has(detail.status));

  async function onStart(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      let cases: { question: string; predicted?: string; ground_truth?: string | null }[];
      try {
        cases = JSON.parse(casesJson) as typeof cases;
      } catch {
        throw new Error("Cases must be valid JSON array.");
      }
      if (!experimentId.trim()) {
        throw new Error("Select or enter an experiment ID.");
      }
      const created = await createEvaluation(getAuthHeaders(), {
        experiment_id: experimentId.trim(),
        cases,
      });
      setActiveId(created.id);
      const d = await fetchEvaluation(getAuthHeaders(), created.id);
      setDetail(d);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Start failed");
    } finally {
      setBusy(false);
    }
  }

  async function onLoadExisting() {
    const id = activeId?.trim();
    if (!id) return;
    setError(null);
    setBusy(true);
    try {
      const d = await fetchEvaluation(getAuthHeaders(), id);
      setDetail(d);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Load failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-xl font-semibold">Evaluations</h1>
      <p className="text-sm text-slate-400">
        Start an evaluation run (async worker). Status refreshes every few seconds (polling) until
        the run completes.
      </p>

      {error ? (
        <div className="rounded border border-red-900/50 bg-red-950/30 px-3 py-2 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      <form className="space-y-3" onSubmit={onStart}>
        <div>
          <label className="mb-1 block text-xs text-slate-500" htmlFor="exp">
            Experiment
          </label>
          <select
            id="exp"
            className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            value={experimentId}
            onChange={(e) => setExperimentId(e.target.value)}
          >
            <option value="">— select —</option>
            {experiments.map((ex) => (
              <option key={ex.id} value={ex.id}>
                {ex.name} ({ex.id.slice(0, 8)}…)
              </option>
            ))}
          </select>
          <input
            className="mt-2 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-xs"
            value={experimentId}
            onChange={(e) => setExperimentId(e.target.value)}
            placeholder="Or paste experiment UUID"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs text-slate-500" htmlFor="cases">
            Cases JSON
          </label>
          <textarea
            id="cases"
            className="min-h-[140px] w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-xs"
            value={casesJson}
            onChange={(e) => setCasesJson(e.target.value)}
          />
        </div>
        <button
          type="submit"
          disabled={busy}
          className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
        >
          {busy ? "Starting…" : "Start evaluation"}
        </button>
      </form>

      <section className="rounded border border-slate-800 bg-slate-900/40 p-4">
        <h2 className="text-sm font-medium text-slate-300">Load existing run</h2>
        <div className="mt-2 flex flex-wrap gap-2">
          <input
            className="min-w-[240px] flex-1 rounded border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-sm"
            value={activeId ?? ""}
            onChange={(e) => setActiveId(e.target.value || null)}
            placeholder="Evaluation / run UUID"
          />
          <button
            type="button"
            className="rounded border border-slate-600 px-3 py-2 text-sm hover:bg-slate-800"
            onClick={() => void onLoadExisting()}
          >
            Load
          </button>
        </div>
      </section>

      {detail ? (
        <section className="space-y-2 rounded border border-slate-800 bg-slate-900/40 p-4">
          <h2 className="text-sm font-medium text-slate-300">Run status</h2>
          <p className="font-mono text-sm">
            <span className="text-slate-500">id</span> {detail.id}
          </p>
          <EvaluationRunSummary detail={detail} />
          <div className="flex flex-wrap gap-2 pt-2">
            <button
              type="button"
              className="rounded border border-slate-600 px-3 py-1.5 text-xs hover:bg-slate-800"
              onClick={() => activeId && void downloadEvaluationReport(getAuthHeaders(), activeId, "json")}
            >
              Download report (JSON)
            </button>
            <button
              type="button"
              className="rounded border border-slate-600 px-3 py-1.5 text-xs hover:bg-slate-800"
              onClick={() => activeId && void downloadEvaluationReport(getAuthHeaders(), activeId, "html")}
            >
              Download report (HTML)
            </button>
          </div>
        </section>
      ) : null}
    </div>
  );
}
