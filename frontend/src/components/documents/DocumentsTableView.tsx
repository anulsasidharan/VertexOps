import { Link } from "react-router-dom";

import type { DocumentDto } from "@/api/types";

export type LoadState = "idle" | "loading" | "success" | "error";

type Props = {
  state: LoadState;
  items: DocumentDto[];
  error: string | null;
  statusFilter: string;
  onStatusFilterChange: (v: string) => void;
};

export function DocumentsTableView({
  state,
  items,
  error,
  statusFilter,
  onStatusFilterChange,
}: Props) {
  if (state === "loading") {
    return <p className="text-slate-400">Loading documents…</p>;
  }
  if (state === "error" && error) {
    return (
      <div className="rounded border border-red-900/50 bg-red-950/30 px-3 py-2 text-sm text-red-200">
        {error}
      </div>
    );
  }
  if (state === "success" && items.length === 0) {
    return (
      <div className="rounded border border-slate-800 bg-slate-900/40 px-4 py-8 text-center text-slate-400">
        No documents match this filter.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <label className="text-sm text-slate-400" htmlFor="doc-status">
          Status
        </label>
        <select
          id="doc-status"
          className="rounded border border-slate-700 bg-slate-950 px-2 py-1 text-sm"
          value={statusFilter}
          onChange={(e) => onStatusFilterChange(e.target.value)}
        >
          <option value="">All</option>
          <option value="pending">pending</option>
          <option value="parsed">parsed</option>
          <option value="ready">ready</option>
          <option value="failed">failed</option>
        </select>
      </div>
      <div className="overflow-x-auto rounded border border-slate-800">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-900/80 text-slate-400">
            <tr>
              <th className="px-3 py-2">Title</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2">Format</th>
              <th className="px-3 py-2">Updated</th>
              <th className="px-3 py-2" />
            </tr>
          </thead>
          <tbody>
            {items.map((d) => (
              <tr key={d.id} className="border-t border-slate-800">
                <td className="px-3 py-2">{d.title ?? d.id}</td>
                <td className="px-3 py-2 font-mono text-xs">{d.ingest_status}</td>
                <td className="px-3 py-2">{d.format ?? "—"}</td>
                <td className="px-3 py-2 text-slate-400">
                  {new Date(d.updated_at).toLocaleString()}
                </td>
                <td className="px-3 py-2">
                  <Link className="text-indigo-400 hover:underline" to={`/documents/${d.id}`}>
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
