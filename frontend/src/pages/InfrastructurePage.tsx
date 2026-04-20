import { useState } from "react";
import { AlertTriangle, CheckCircle2, RefreshCw } from "lucide-react";
import { MOCK_RESOURCES, RESOURCE_EDGES, type Resource } from "@/lib/mockData";

type Cloud = "all" | "GCP" | "AWS" | "Azure";

const CLOUD_STYLE: Record<string, string> = {
  GCP:   "border-blue-500  bg-blue-500/10  text-blue-400",
  AWS:   "border-orange-500 bg-orange-500/10 text-orange-400",
  Azure: "border-cyan-500  bg-cyan-500/10  text-cyan-400",
};

function StatusBadge({ s }: { s: Resource["status"] }) {
  if (s === "healthy") return <span className="inline-flex items-center gap-1 text-xs text-green-400"><CheckCircle2 className="w-3 h-3" />Healthy</span>;
  if (s === "warning") return <span className="inline-flex items-center gap-1 text-xs text-amber-400"><AlertTriangle className="w-3 h-3" />Warning</span>;
  return <span className="text-xs text-red-400">Critical</span>;
}

export function InfrastructurePage() {
  const [cloud, setCloud] = useState<Cloud>("all");
  const [selected, setSelected] = useState<Resource | null>(null);

  const visible = cloud === "all" ? MOCK_RESOURCES : MOCK_RESOURCES.filter((r) => r.cloud === cloud);

  const counts = { GCP: 312, AWS: 289, Azure: 246 };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold">Infrastructure</h1>
          <p className="text-xs text-slate-500 mt-0.5">Auto-discovered · 847 resources across 3 clouds</p>
        </div>
        <button className="flex items-center gap-1.5 rounded border border-slate-600 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800">
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </button>
      </div>

      {/* Cloud filter */}
      <div className="flex gap-2 flex-wrap">
        {(["all", "GCP", "AWS", "Azure"] as Cloud[]).map((c) => (
          <button key={c}
            onClick={() => { setCloud(c); setSelected(null); }}
            className={`px-3 py-1.5 rounded text-xs font-semibold transition-colors ${
              cloud === c
                ? "bg-indigo-600 text-white"
                : "border border-slate-700 text-slate-400 hover:bg-slate-800"
            }`}>
            {c === "all" ? "All Clouds (847)" : `${c} (${counts[c]})`}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Topology */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h2 className="text-sm font-semibold text-slate-400 mb-3">Resource Topology</h2>
          <div className="relative bg-slate-950 rounded-lg" style={{ height: 300 }}>
            <svg className="absolute inset-0 w-full h-full">
              {RESOURCE_EDGES.map(([a, b]) => {
                const ra = MOCK_RESOURCES.find((r) => r.id === a);
                const rb = MOCK_RESOURCES.find((r) => r.id === b);
                if (!ra || !rb) return null;
                const aVisible = cloud === "all" || ra.cloud === cloud;
                const bVisible = cloud === "all" || rb.cloud === cloud;
                return (
                  <line key={`${a}-${b}`}
                    x1={`${ra.x + 2}%`} y1={`${ra.y + 2}%`}
                    x2={`${rb.x + 2}%`} y2={`${rb.y + 2}%`}
                    stroke={aVisible && bVisible ? "#1e3a5f" : "#1e293b"}
                    strokeWidth="1.5"
                  />
                );
              })}
            </svg>
            {MOCK_RESOURCES.map((r) => {
              const isVisible = cloud === "all" || r.cloud === cloud;
              return (
                <button key={r.id}
                  onClick={() => setSelected(r.id === selected?.id ? null : r)}
                  style={{ left: `${r.x}%`, top: `${r.y}%` }}
                  className={`absolute w-11 h-11 rounded-full border-2 flex items-center justify-center text-[10px] font-bold
                    transition-all duration-200 hover:scale-110
                    ${isVisible ? `${CLOUD_STYLE[r.cloud]} cursor-pointer` : "border-slate-700 bg-slate-800/30 text-slate-700 cursor-default"}
                    ${r.status === "warning" && isVisible ? "animate-pulse" : ""}
                    ${selected?.id === r.id ? "ring-2 ring-white ring-offset-1 ring-offset-slate-950 scale-125 z-10" : ""}
                  `}
                  title={r.name}
                  disabled={!isVisible}
                >
                  {r.cloud.slice(0, 3)}
                </button>
              );
            })}
            <div className="absolute bottom-2 left-2 flex gap-3 text-xs">
              <span className="text-blue-400">● GCP</span>
              <span className="text-orange-400">● AWS</span>
              <span className="text-cyan-400">● Azure</span>
            </div>
          </div>
        </div>

        {/* Detail panel */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h2 className="text-sm font-semibold text-slate-400 mb-3">Resource Details</h2>
          {selected ? (
            <div className="space-y-3">
              <div>
                <div className="font-semibold text-slate-100">{selected.name}</div>
                <div className="text-xs text-slate-500 mt-0.5">{selected.type} · {selected.cloud}</div>
              </div>
              <div className="space-y-1.5 text-xs">
                {[["Region", selected.region], ["Provider", selected.cloud], ["Type", selected.type]].map(([k, v]) => (
                  <div key={k} className="flex justify-between">
                    <span className="text-slate-500">{k}</span>
                    <span className="text-slate-300">{v}</span>
                  </div>
                ))}
                <div className="flex justify-between"><span className="text-slate-500">Status</span><StatusBadge s={selected.status} /></div>
              </div>
              <div className="space-y-2 pt-1">
                {[
                  { label: "CPU",    val: selected.cpu,    color: selected.cpu > 80 ? "bg-red-500" : "bg-blue-500" },
                  { label: "Memory", val: selected.memory, color: selected.memory > 80 ? "bg-amber-500" : "bg-teal-500" },
                ].map(({ label, val, color }) => (
                  <div key={label}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-500">{label}</span>
                      <span className={`font-semibold ${val > 80 ? "text-red-400" : "text-slate-300"}`}>{val}%</span>
                    </div>
                    <div className="h-1.5 bg-slate-700 rounded-full">
                      <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${val}%` }} />
                    </div>
                  </div>
                ))}
              </div>
              <button className="w-full rounded border border-slate-700 py-1.5 text-xs text-slate-400 hover:bg-slate-800">
                View full metrics →
              </button>
            </div>
          ) : (
            <div className="text-xs text-slate-600 text-center py-10">
              Click a node to inspect
            </div>
          )}
        </div>
      </div>

      {/* Resources table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-800 text-sm font-semibold text-slate-400">
          {visible.length} Resources {cloud !== "all" && `· ${cloud}`}
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-xs">
            <thead className="bg-slate-900/80">
              <tr>
                {["Name", "Type", "Cloud", "Region", "Status", "CPU", "Memory"].map((h) => (
                  <th key={h} className="px-4 py-2.5 text-left text-slate-500 font-medium uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {visible.map((r) => (
                <tr key={r.id} onClick={() => setSelected(r)} className="border-t border-slate-800 hover:bg-slate-800/50 cursor-pointer">
                  <td className="px-4 py-2.5 font-medium text-slate-200">{r.name}</td>
                  <td className="px-4 py-2.5 text-slate-400">{r.type}</td>
                  <td className="px-4 py-2.5">
                    <span className={`px-2 py-0.5 rounded-full border text-[10px] font-bold ${CLOUD_STYLE[r.cloud]}`}>{r.cloud}</span>
                  </td>
                  <td className="px-4 py-2.5 text-slate-400">{r.region}</td>
                  <td className="px-4 py-2.5"><StatusBadge s={r.status} /></td>
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-slate-700 rounded-full">
                        <div className={`h-full rounded-full ${r.cpu > 80 ? "bg-red-500" : "bg-blue-500"}`} style={{ width: `${r.cpu}%` }} />
                      </div>
                      <span className={r.cpu > 80 ? "text-red-400 font-semibold" : "text-slate-400"}>{r.cpu}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-slate-700 rounded-full">
                        <div className={`h-full rounded-full ${r.memory > 80 ? "bg-amber-500" : "bg-teal-500"}`} style={{ width: `${r.memory}%` }} />
                      </div>
                      <span className={r.memory > 80 ? "text-amber-400 font-semibold" : "text-slate-400"}>{r.memory}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
