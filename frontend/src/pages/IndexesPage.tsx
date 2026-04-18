import { FormEvent, useCallback, useEffect, useState } from "react";

import { createIndex, fetchIndexes, rebuildIndex } from "@/api/indexes";
import type { IndexDto } from "@/api/types";
import {
  IndexesPanelView,
  type IndexLoadState,
} from "@/components/indexes/IndexesPanelView";
import { useAuthSession } from "@/context/AuthSessionContext";

export function IndexesPage() {
  const { getAuthHeaders } = useAuthSession();
  const [state, setState] = useState<IndexLoadState>("idle");
  const [items, setItems] = useState<IndexDto[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setError(null);
    try {
      const data = await fetchIndexes(getAuthHeaders());
      setItems(data.items);
      setState("success");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load indexes");
      setState("error");
    }
  }, [getAuthHeaders]);

  useEffect(() => {
    void load();
  }, [load]);

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    setFeedback(null);
    if (!name.trim()) return;
    try {
      await createIndex(getAuthHeaders(), { name: name.trim(), vector_backend: "pinecone" });
      setName("");
      setFeedback("Index created.");
      await load();
    } catch (err) {
      setFeedback(err instanceof Error ? err.message : "Create failed");
    }
  }

  async function onRebuild(id: string) {
    setBusyId(id);
    setFeedback(null);
    try {
      await rebuildIndex(getAuthHeaders(), id);
      setFeedback("Rebuild requested.");
      await load();
    } catch (err) {
      setFeedback(err instanceof Error ? err.message : "Rebuild failed");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-xl font-semibold">Indexes</h1>
        <button
          type="button"
          className="rounded border border-slate-600 px-3 py-1.5 text-sm hover:bg-slate-800"
          onClick={() => void load()}
        >
          Refresh
        </button>
      </div>

      {feedback ? (
        <div className="rounded border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-slate-200">
          {feedback}
        </div>
      ) : null}

      <form className="flex flex-wrap items-end gap-2" onSubmit={onCreate}>
        <div>
          <label className="mb-1 block text-xs text-slate-500" htmlFor="idx-name">
            New index name
          </label>
          <input
            id="idx-name"
            className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="production-corpus"
          />
        </div>
        <button
          type="submit"
          className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
        >
          Create index
        </button>
      </form>

      <IndexesPanelView
        state={state}
        items={items}
        error={error}
        busyId={busyId}
        onRebuild={onRebuild}
      />
    </div>
  );
}
