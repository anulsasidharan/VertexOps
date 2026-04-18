import { useCallback, useEffect, useState } from "react";

import { fetchDocuments } from "@/api/documents";
import type { DocumentDto } from "@/api/types";
import {
  DocumentsTableView,
  type LoadState,
} from "@/components/documents/DocumentsTableView";
import { useAuthSession } from "@/context/AuthSessionContext";

export function DocumentsPage() {
  const { getAuthHeaders } = useAuthSession();
  const [state, setState] = useState<LoadState>("idle");
  const [items, setItems] = useState<DocumentDto[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState("");

  const load = useCallback(async () => {
    setState("loading");
    setError(null);
    try {
      const data = await fetchDocuments(getAuthHeaders(), {
        status: statusFilter || undefined,
        limit: 100,
        offset: 0,
      });
      setItems(data.items);
      setState("success");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load documents");
      setState("error");
    }
  }, [getAuthHeaders, statusFilter]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-xl font-semibold">Documents</h1>
        <button
          type="button"
          className="rounded border border-slate-600 px-3 py-1.5 text-sm hover:bg-slate-800"
          onClick={() => void load()}
        >
          Refresh
        </button>
      </div>
      <DocumentsTableView
        state={state}
        items={items}
        error={error}
        statusFilter={statusFilter}
        onStatusFilterChange={(v) => setStatusFilter(v)}
      />
    </div>
  );
}
