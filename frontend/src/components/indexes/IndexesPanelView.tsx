import type { IndexDto } from "@/api/types";

export type IndexLoadState = "idle" | "loading" | "success" | "error";

type Props = {
  state: IndexLoadState;
  items: IndexDto[];
  error: string | null;
  busyId: string | null;
  onRebuild: (id: string) => void;
};

export function IndexesPanelView({
  state,
  items,
  error,
  busyId,
  onRebuild,
}: Props) {
  if (state === "loading") {
    return <p className="text-slate-400">Loading indexes…</p>;
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
      <p className="text-slate-400">
        No indexes yet. Create one below to start vector search for this workspace.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded border border-slate-800">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-900/80 text-slate-400">
          <tr>
            <th className="px-3 py-2">Name</th>
            <th className="px-3 py-2">Backend</th>
            <th className="px-3 py-2">Status</th>
            <th className="px-3 py-2">Updated</th>
            <th className="px-3 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((idx) => (
            <tr key={idx.id} className="border-t border-slate-800">
              <td className="px-3 py-2">{idx.name}</td>
              <td className="px-3 py-2 font-mono text-xs">{idx.vector_backend ?? "—"}</td>
              <td className="px-3 py-2 font-mono text-xs">{idx.status}</td>
              <td className="px-3 py-2 text-slate-400">
                {new Date(idx.updated_at).toLocaleString()}
              </td>
              <td className="px-3 py-2">
                <button
                  type="button"
                  className="rounded bg-slate-800 px-2 py-1 text-xs text-slate-100 hover:bg-slate-700 disabled:opacity-50"
                  disabled={busyId === idx.id}
                  onClick={() => onRebuild(idx.id)}
                >
                  {busyId === idx.id ? "Rebuilding…" : "Rebuild"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
