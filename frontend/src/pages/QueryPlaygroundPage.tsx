import { FormEvent, useState } from "react";

import { runQuery } from "@/api/query";
import { QueryResultPanel } from "@/components/query/QueryResultPanel";
import type { QueryResponseDto } from "@/api/types";
import { useAuthSession } from "@/context/AuthSessionContext";

export function QueryPlaygroundPage() {
  const { getAuthHeaders } = useAuthSession();
  const [question, setQuestion] = useState("");
  const [indexId, setIndexId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<QueryResponseDto | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    if (!indexId.trim()) {
      setError("Index ID is required.");
      return;
    }
    setLoading(true);
    try {
      const data = await runQuery(getAuthHeaders(), {
        question: question.trim(),
        index_id: indexId.trim(),
        top_k: 5,
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
            Index ID (UUID)
          </label>
          <input
            id="idx"
            className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-sm"
            value={indexId}
            onChange={(e) => setIndexId(e.target.value)}
            placeholder="00000000-0000-0000-0000-000000000000"
          />
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
