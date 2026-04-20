import { FormEvent, useCallback, useEffect, useState } from "react";

import { createApiKey, listApiKeys, revokeApiKey } from "@/api/auth";
import type { ApiKeyDto } from "@/api/types";
import { useAuthSession } from "@/context/AuthSessionContext";

export function SettingsPage() {
  const { getAuthHeaders } = useAuthSession();
  const [keys, setKeys] = useState<ApiKeyDto[]>([]);
  const [loading, setLoading] = useState(false);
  const [label, setLabel] = useState("");
  const [newKey, setNewKey] = useState<string | null>(null);
  const [revokingId, setRevokingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listApiKeys(getAuthHeaders());
      setKeys(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load API keys");
    } finally {
      setLoading(false);
    }
  }, [getAuthHeaders]);

  useEffect(() => { void load(); }, [load]);

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setNewKey(null);
    setFeedback(null);
    try {
      const created = await createApiKey(getAuthHeaders(), label.trim() || undefined);
      setNewKey(created.raw_key);
      setLabel("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Create failed");
    }
  }

  async function onRevoke(id: string) {
    if (!confirm("Revoke this API key? Any integrations using it will stop working.")) return;
    setRevokingId(id);
    setError(null);
    setFeedback(null);
    try {
      await revokeApiKey(getAuthHeaders(), id);
      setFeedback("API key revoked.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Revoke failed");
    } finally {
      setRevokingId(null);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-xl font-semibold">Settings</h1>

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

      {/* New key revealed */}
      {newKey && (
        <div className="rounded border border-green-800 bg-green-950/30 p-4 space-y-2">
          <p className="text-sm font-medium text-green-300">
            API key created — copy it now. It will not be shown again.
          </p>
          <code className="block break-all rounded bg-slate-950 px-3 py-2 font-mono text-xs text-green-200 select-all">
            {newKey}
          </code>
          <button
            type="button"
            onClick={() => void navigator.clipboard.writeText(newKey)}
            className="rounded border border-green-700 px-3 py-1 text-xs text-green-300 hover:bg-green-900/40"
          >
            Copy to clipboard
          </button>
        </div>
      )}

      {/* API Keys section */}
      <div className="rounded border border-slate-800 bg-slate-900/40 p-4 space-y-4">
        <h2 className="text-sm font-medium text-slate-200">API Keys</h2>
        <p className="text-xs text-slate-400">
          Use API keys to authenticate from scripts or CI/CD pipelines. Pass the key as the{" "}
          <code className="font-mono text-slate-300">X-API-Key</code> header.
        </p>

        <form className="flex flex-wrap gap-2 items-end" onSubmit={onCreate}>
          <div>
            <label className="mb-1 block text-xs text-slate-500" htmlFor="key-label">
              Label (optional)
            </label>
            <input
              id="key-label"
              className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder="my-ci-pipeline"
            />
          </div>
          <button
            type="submit"
            className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
          >
            Generate key
          </button>
        </form>

        {loading ? (
          <p className="text-sm text-slate-400">Loading…</p>
        ) : keys.length === 0 ? (
          <p className="text-sm text-slate-500">No API keys yet.</p>
        ) : (
          <div className="overflow-x-auto rounded border border-slate-800">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-slate-900/80 text-slate-400">
                <tr>
                  <th className="px-3 py-2">ID</th>
                  <th className="px-3 py-2">Label</th>
                  <th className="px-3 py-2" />
                </tr>
              </thead>
              <tbody>
                {keys.map((k) => (
                  <tr key={k.id} className="border-t border-slate-800">
                    <td className="px-3 py-2 font-mono text-xs text-slate-400">
                      {k.id.slice(0, 8)}…
                    </td>
                    <td className="px-3 py-2">{k.label ?? <span className="text-slate-500">—</span>}</td>
                    <td className="px-3 py-2">
                      <button
                        type="button"
                        disabled={revokingId === k.id}
                        onClick={() => void onRevoke(k.id)}
                        className="text-xs text-red-400 hover:underline disabled:opacity-40"
                      >
                        {revokingId === k.id ? "Revoking…" : "Revoke"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
