import { useCallback, useEffect, useState } from "react";

import { deleteDocument, fetchDocuments } from "@/api/documents";
import type { DocumentDto } from "@/api/types";
import {
  DocumentsTableView,
  type LoadState,
} from "@/components/documents/DocumentsTableView";
import { UploadDocumentModal } from "@/components/documents/UploadDocumentModal";
import { useAuthSession } from "@/context/AuthSessionContext";

export function DocumentsPage() {
  const { getAuthHeaders } = useAuthSession();
  const [state, setState] = useState<LoadState>("idle");
  const [items, setItems] = useState<DocumentDto[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [showUpload, setShowUpload] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

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

  async function onDelete(id: string) {
    if (!confirm("Delete this document? This cannot be undone.")) return;
    setDeletingId(id);
    try {
      await deleteDocument(getAuthHeaders(), id);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-xl font-semibold">Documents</h1>
        <div className="flex gap-2">
          <button
            type="button"
            className="rounded bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-500"
            onClick={() => setShowUpload(true)}
          >
            + Upload
          </button>
          <button
            type="button"
            className="rounded border border-slate-600 px-3 py-1.5 text-sm hover:bg-slate-800"
            onClick={() => void load()}
          >
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded border border-red-900/50 bg-red-950/30 px-3 py-2 text-sm text-red-200">
          {error}
        </div>
      )}

      <DocumentsTableView
        state={state}
        items={items}
        error={error}
        statusFilter={statusFilter}
        onStatusFilterChange={(v) => setStatusFilter(v)}
        deletingId={deletingId}
        onDelete={onDelete}
      />

      {showUpload && (
        <UploadDocumentModal
          auth={getAuthHeaders()}
          onClose={() => setShowUpload(false)}
          onSuccess={() => {
            setShowUpload(false);
            void load();
          }}
        />
      )}
    </div>
  );
}
