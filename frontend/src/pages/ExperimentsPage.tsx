import { FormEvent, useCallback, useEffect, useState } from "react";

import { createExperiment, fetchExperiments, kickoffRun } from "@/api/experiments";
import { fetchIndexes } from "@/api/indexes";
import type { ExperimentDto, IndexDto } from "@/api/types";
import { useAuthSession } from "@/context/AuthSessionContext";

export function ExperimentsPage() {
  const { getAuthHeaders } = useAuthSession();
  const [experiments, setExperiments] = useState<ExperimentDto[]>([]);
  const [indexes, setIndexes] = useState<IndexDto[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  // Create form state
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [indexId, setIndexId] = useState("");

  // Run kickoff state
  const [kickingOff, setKickingOff] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [expData, idxData] = await Promise.all([
        fetchExperiments(getAuthHeaders()),
        fetchIndexes(getAuthHeaders()),
      ]);
      setExperiments(expData.items);
      setIndexes(idxData.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }, [getAuthHeaders]);

  useEffect(() => { void load(); }, [load]);

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    setFeedback(null);
    setError(null);
    if (!name.trim()) return;
    try {
      await createExperiment(getAuthHeaders(), {
        name: name.trim(),
        description: description.trim() || undefined,
        index_id: indexId || undefined,
      });
      setName("");
      setDescription("");
      setIndexId("");
      setFeedback("Experiment created.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Create failed");
    }
  }

  async function onKickoff(experimentId: string) {
    setKickingOff(experimentId);
    setFeedback(null);
    setError(null);
    try {
      const run = await kickoffRun(getAuthHeaders(), experimentId);
      setFeedback(`Run started — ID: ${run.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kickoff failed");
    } finally {
      setKickingOff(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-xl font-semibold">Experiments</h1>
        <button
          type="button"
          className="rounded border border-slate-600 px-3 py-1.5 text-sm hover:bg-slate-800"
          onClick={() => void load()}
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="rounded border border-red-900/50 bg-red-950/30 px-3 py-2 text-sm text-red-200">
          {error}
        </div>
      )}
      {feedback && (
        <div className="rounded border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-slate-200">
          {feedback}
        </div>
      )}

      {/* Create form */}
      <div className="rounded border border-slate-800 bg-slate-900/40 p-4">
        <h2 className="mb-3 text-sm font-medium text-slate-300">New experiment</h2>
        <form className="space-y-3" onSubmit={onCreate}>
          <div className="flex flex-wrap gap-3">
            <div className="flex-1 min-w-[180px]">
              <label className="mb-1 block text-xs text-slate-500" htmlFor="exp-name">
                Name <span className="text-red-400">*</span>
              </label>
              <input
                id="exp-name"
                required
                className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="baseline-v1"
              />
            </div>
            <div className="flex-1 min-w-[180px]">
              <label className="mb-1 block text-xs text-slate-500" htmlFor="exp-desc">
                Description
              </label>
              <input
                id="exp-desc"
                className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Optional description"
              />
            </div>
            <div className="flex-1 min-w-[180px]">
              <label className="mb-1 block text-xs text-slate-500" htmlFor="exp-index">
                Index (optional)
              </label>
              <select
                id="exp-index"
                className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
                value={indexId}
                onChange={(e) => setIndexId(e.target.value)}
              >
                <option value="">— none —</option>
                {indexes.map((idx) => (
                  <option key={idx.id} value={idx.id}>
                    {idx.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <button
            type="submit"
            className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
          >
            Create experiment
          </button>
        </form>
      </div>

      {/* Experiments list */}
      {loading ? (
        <p className="text-sm text-slate-400">Loading…</p>
      ) : experiments.length === 0 ? (
        <div className="rounded border border-slate-800 bg-slate-900/40 px-4 py-8 text-center text-slate-400 text-sm">
          No experiments yet. Create one above.
        </div>
      ) : (
        <div className="overflow-x-auto rounded border border-slate-800">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-900/80 text-slate-400">
              <tr>
                <th className="px-3 py-2">Name</th>
                <th className="px-3 py-2">Description</th>
                <th className="px-3 py-2">Index</th>
                <th className="px-3 py-2">Created</th>
                <th className="px-3 py-2" />
              </tr>
            </thead>
            <tbody>
              {experiments.map((exp) => (
                <tr key={exp.id} className="border-t border-slate-800">
                  <td className="px-3 py-2 font-medium">{exp.name}</td>
                  <td className="px-3 py-2 text-slate-400 text-xs">{exp.description ?? "—"}</td>
                  <td className="px-3 py-2 font-mono text-xs text-slate-400">
                    {exp.index_id ? exp.index_id.slice(0, 8) + "…" : "—"}
                  </td>
                  <td className="px-3 py-2 text-slate-400 text-xs">
                    {new Date(exp.created_at).toLocaleString()}
                  </td>
                  <td className="px-3 py-2">
                    <button
                      type="button"
                      disabled={kickingOff === exp.id}
                      onClick={() => void onKickoff(exp.id)}
                      className="rounded border border-slate-600 px-2 py-1 text-xs hover:bg-slate-800 disabled:opacity-40"
                    >
                      {kickingOff === exp.id ? "Starting…" : "▶ Run"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
