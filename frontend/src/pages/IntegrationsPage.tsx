import { useState } from "react";
import { Link2, Plus, X } from "lucide-react";
import { MOCK_INTEGRATIONS, type Integration } from "@/lib/mockData";

const CATEGORY_ORDER = ["Cloud", "Comms", "Monitoring", "CI/CD", "IaC"];

function ConnectModal({ integration, onClose, onSave }: {
  integration: Integration;
  onClose: () => void;
  onSave: (id: string) => void;
}) {
  const [token, setToken] = useState("");
  const [testing, setTesting] = useState(false);
  const [tested, setTested] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  function testConnection() {
    if (!token.trim()) return;
    setTesting(true);
    setTimeout(() => { setTesting(false); setTested(true); }, 1500);
  }

  function save() {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      setSaved(true);
      setTimeout(() => { onSave(integration.id); onClose(); }, 800);
    }, 1000);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 w-full max-w-md shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{integration.icon}</span>
            <div>
              <h2 className="text-sm font-semibold text-slate-200">Connect {integration.name}</h2>
              <p className="text-xs text-slate-500">{integration.category}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-300">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-xs font-medium text-slate-400 block mb-1.5">API Token / Credential</label>
            <input
              type="password"
              value={token}
              onChange={(e) => { setToken(e.target.value); setTested(false); }}
              placeholder={`Paste your ${integration.name} API token`}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="flex gap-2">
            <button
              onClick={testConnection}
              disabled={!token.trim() || testing}
              className={`flex-1 rounded-lg border py-2 text-xs font-semibold transition-all ${
                tested
                  ? "border-green-600 bg-green-900/30 text-green-300"
                  : "border-slate-600 text-slate-400 hover:bg-slate-800 disabled:opacity-40"
              }`}
            >
              {testing ? "Testing…" : tested ? "✓ Connection verified" : "⚡ Test Connection"}
            </button>
            <button
              onClick={save}
              disabled={!tested || saving || saved}
              className={`flex-1 rounded-lg py-2 text-xs font-semibold transition-all ${
                saved
                  ? "bg-green-700 text-white"
                  : "bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-40"
              }`}
            >
              {saved ? "✓ Saved!" : saving ? "Saving…" : "Save & Connect"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export function IntegrationsPage() {
  const [integrations, setIntegrations] = useState(MOCK_INTEGRATIONS);
  const [modal, setModal] = useState<Integration | null>(null);
  const [activeCategory, setActiveCategory] = useState("All");

  const categories = ["All", ...CATEGORY_ORDER];
  const filtered = activeCategory === "All"
    ? integrations
    : integrations.filter((i) => i.category === activeCategory);

  const connected = integrations.filter((i) => i.status === "connected").length;

  function handleConnect(id: string) {
    setIntegrations((prev) =>
      prev.map((i) => i.id === id ? { ...i, status: "connected" as const, detail: "Connected just now" } : i)
    );
  }

  function handleDisconnect(id: string) {
    setIntegrations((prev) =>
      prev.map((i) => i.id === id ? { ...i, status: "disconnected" as const, detail: undefined } : i)
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold flex items-center gap-2">
            <Link2 className="w-5 h-5 text-indigo-400" /> Integrations
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {connected} of {integrations.length} connected · Cloud · Monitoring · CI/CD · Comms · IaC
          </p>
        </div>
        <button className="flex items-center gap-1.5 rounded bg-indigo-600 px-3 py-1.5 text-xs text-white font-semibold hover:bg-indigo-500">
          <Plus className="w-3.5 h-3.5" /> Request Integration
        </button>
      </div>

      {/* Summary bar */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {CATEGORY_ORDER.map((cat) => {
          const all = integrations.filter((i) => i.category === cat);
          const conn = all.filter((i) => i.status === "connected").length;
          return (
            <div key={cat} className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-center">
              <div className="text-lg font-bold text-indigo-300">{conn}/{all.length}</div>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider">{cat}</div>
            </div>
          );
        })}
      </div>

      {/* Category filter */}
      <div className="flex gap-2 flex-wrap">
        {categories.map((cat) => (
          <button key={cat} onClick={() => setActiveCategory(cat)}
            className={`px-3 py-1 rounded-full text-xs font-semibold transition-colors ${
              activeCategory === cat
                ? "bg-indigo-600 text-white"
                : "border border-slate-700 text-slate-400 hover:border-slate-500"
            }`}>
            {cat}
          </button>
        ))}
      </div>

      {/* Integration cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((intg) => (
          <div key={intg.id}
            className={`bg-slate-900 border rounded-xl p-4 transition-colors ${
              intg.status === "connected" ? "border-slate-700" : "border-slate-800"
            }`}>
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center text-2xl"
                  style={{ background: `${intg.color}22`, border: `1px solid ${intg.color}44` }}>
                  {intg.icon}
                </div>
                <div>
                  <div className="text-sm font-semibold text-slate-200">{intg.name}</div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-wider">{intg.category}</div>
                </div>
              </div>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                intg.status === "connected"
                  ? "bg-green-900/40 text-green-300 border-green-700"
                  : "bg-slate-800 text-slate-500 border-slate-700"
              }`}>
                {intg.status === "connected" ? "● CONNECTED" : "○ NOT CONNECTED"}
              </span>
            </div>

            {intg.detail && (
              <p className="text-xs text-slate-500 mb-3 bg-slate-800/50 rounded-lg px-2.5 py-1.5">{intg.detail}</p>
            )}

            <div className="flex gap-2">
              {intg.status === "connected" ? (
                <>
                  <button className="flex-1 rounded-lg border border-slate-700 py-1.5 text-xs text-slate-400 hover:bg-slate-800 font-semibold">
                    Manage
                  </button>
                  <button
                    onClick={() => handleDisconnect(intg.id)}
                    className="rounded-lg border border-red-800 px-3 py-1.5 text-xs text-red-400 hover:bg-red-900/20 font-semibold">
                    Disconnect
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setModal(intg)}
                  className="flex-1 rounded-lg bg-indigo-600/80 border border-indigo-500 py-1.5 text-xs text-indigo-200 hover:bg-indigo-600 font-semibold transition-colors">
                  + Connect
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {modal && (
        <ConnectModal
          integration={modal}
          onClose={() => setModal(null)}
          onSave={(id) => { handleConnect(id); setModal(null); }}
        />
      )}
    </div>
  );
}
