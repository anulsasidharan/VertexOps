import { FormEvent, useCallback, useEffect, useState } from "react";

import { runQuery } from "@/api/query";
import { fetchIndexes } from "@/api/indexes";
import { QueryResultPanel } from "@/components/query/QueryResultPanel";
import type { QueryResponseDto, IndexDto } from "@/api/types";
import { useAuthSession } from "@/context/AuthSessionContext";

export function QueryPlaygroundPage() {
  const { getAuthHeaders } = useAuthSession();
  const [question, setQuestion] = useState("");
  const [indexId, setIndexId] = useState("");
  const [topK, setTopK] = useState(5);
  const [indexes, setIndexes] = useState<IndexDto[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<QueryResponseDto | null>(null);

  const loadIndexes = useCallback(async () => {
    try {
      const data = await fetchIndexes(getAuthHeaders());
      setIndexes(data.items);
      if (data.items.length > 0 && !indexId) {
        setIndexId(data.items[0].id);
      }
    } catch {
      /* non-fatal */
    }
  }, [getAuthHeaders, indexId]);

  useEffect(() => { void loadIndexes(); }, [loadIndexes]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    if (!indexId.trim()) {
      setError("Select or enter an index ID.");
      return;
    }
    setLoading(true);
    try {
      const data = await runQuery(getAuthHeaders(), {
        question: question.trim(),
        index_id: indexId.trim(),
        top_k: topK,
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <h1 className="text-xl font-semibold">Query playground</h1>
      <form className="space-y-3" onSubmit={onSubmit}>
        <div>
          <label className="mb-1 block text-xs text-slate-500" htmlFor="idx">
            Index
          </label>
          {indexes.length > 0 ? (
            <select
              id="idx"
              className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              value={indexId}
              onChange={(e) => setIndexId(e.target.value)}
            >
              <option value="">— select index —</option>
              {indexes.map((idx) => (
                <option key={idx.id} value={idx.id}>
                  {idx.name} ({idx.status})
                </option>
              ))}
            </select>
          ) : (
            <input
              id="idx"
              className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-sm"
              value={indexId}
              onChange={(e) => setIndexId(e.target.value)}
              placeholder="00000000-0000-0000-0000-000000000000"
            />
          )}
        </div>
        <div>
          <label className="mb-1 block text-xs text-slate-500" htmlFor="q">
            Question
          </label>
          <textarea
            id="q"
            className="min-h-[120px] w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask something about your corpus…"
            required
          />
        </div>
        <div className="flex items-center gap-3">
          <label className="text-xs text-slate-500" htmlFor="top-k">
            Top-K results
          </label>
          <input
            id="top-k"
            type="number"
            min={1}
            max={20}
            className="w-20 rounded border border-slate-700 bg-slate-950 px-3 py-1.5 text-sm"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
        >
          {loading ? "Querying…" : "Run query"}
        </button>
      </form>
      <QueryResultPanel loading={loading} error={error} result={result} />
    </div>
  );
}
