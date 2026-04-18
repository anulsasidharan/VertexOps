import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { fetchDocument } from "@/api/documents";
import type { DocumentDto } from "@/api/types";
import { useAuthSession } from "@/context/AuthSessionContext";

export function DocumentDetailPage() {
  const { documentId } = useParams<{ documentId: string }>();
  const { getAuthHeaders } = useAuthSession();
  const [doc, setDoc] = useState<DocumentDto | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!documentId) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const d = await fetchDocument(getAuthHeaders(), documentId);
        if (!cancelled) setDoc(d);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load document");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [documentId, getAuthHeaders]);

  if (loading) {
    return <p className="text-slate-400">Loading document…</p>;
  }
  if (error) {
    return (
      <div className="space-y-2">
        <p className="text-red-300">{error}</p>
        <Link to="/documents" className="text-indigo-400 hover:underline">
          Back to list
        </Link>
      </div>
    );
  }
  if (!doc) {
    return null;
  }

  return (
    <div className="space-y-4">
      <Link to="/documents" className="text-sm text-indigo-400 hover:underline">
        ← Documents
      </Link>
      <h1 className="text-xl font-semibold">{doc.title ?? doc.id}</h1>
      <dl className="grid max-w-xl grid-cols-1 gap-2 text-sm sm:grid-cols-2">
        <dt className="text-slate-500">Status</dt>
        <dd className="font-mono">{doc.ingest_status}</dd>
        <dt className="text-slate-500">Format</dt>
        <dd>{doc.format ?? "—"}</dd>
        <dt className="text-slate-500">Source</dt>
        <dd className="break-all">{doc.source_uri ?? "—"}</dd>
        <dt className="text-slate-500">Updated</dt>
        <dd>{new Date(doc.updated_at).toLocaleString()}</dd>
      </dl>
    </div>
  );
}
