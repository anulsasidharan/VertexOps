import { useState } from "react";
import { CheckCircle2, Clock, Cpu } from "lucide-react";
import { MOCK_INCIDENTS, type Incident } from "@/lib/mockData";

const SEV_STYLE: Record<string, string> = {
  critical: "bg-red-900/40 text-red-300 border-red-700",
  high:     "bg-orange-900/40 text-orange-300 border-orange-700",
  medium:   "bg-amber-900/40 text-amber-300 border-amber-700",
  low:      "bg-slate-800 text-slate-400 border-slate-700",
};

const STATUS_STYLE: Record<string, string> = {
  open:      "bg-red-900/40 text-red-300 border-red-700",
  resolving: "bg-amber-900/40 text-amber-300 border-amber-700",
  resolved:  "bg-green-900/40 text-green-300 border-green-700",
};

const TIMELINE_COLOR: Record<string, string> = {
  info:    "border-slate-500 text-slate-400",
  warning: "border-amber-500 text-amber-400",
  success: "border-green-500 text-green-400",
  ai:      "border-blue-500 text-blue-400",
};

export function IncidentsPage() {
  const [selected, setSelected] = useState<Incident>(MOCK_INCIDENTS[0]);
  const [actions, setActions] = useState(selected.actions);
  const [status, setStatus] = useState(selected.status);

  function selectIncident(inc: Incident) {
    setSelected(inc);
    setActions(inc.actions);
    setStatus(inc.status);
  }

  function approveAction(idx: number) {
    const updated = actions.map((a, i) =>
      i === idx ? { ...a, status: "applied" as const } : a
    );
    setActions(updated);
    if (updated.every((a) => a.status !== "pending")) setStatus("resolved");
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Incidents</h1>
        <div className="flex gap-2 text-xs">
          <span className="bg-red-900/40 text-red-300 border border-red-700 px-2 py-1 rounded-full">1 Open</span>
          <span className="bg-slate-800 text-slate-400 border border-slate-700 px-2 py-1 rounded-full">2 Resolved</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Incident list */}
        <div className="space-y-2">
          {MOCK_INCIDENTS.map((inc) => (
            <button key={inc.id} onClick={() => selectIncident(inc)}
              className={`w-full text-left rounded-xl border p-3 transition-colors ${
                selected.id === inc.id
                  ? "border-indigo-600 bg-indigo-900/20"
                  : "border-slate-800 bg-slate-900 hover:border-slate-700"
              }`}>
              <div className="flex items-start justify-between gap-2 mb-2">
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border uppercase tracking-wide ${SEV_STYLE[inc.severity]}`}>
                  {inc.severity}
                </span>
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border uppercase tracking-wide ${STATUS_STYLE[inc.status]}`}>
                  {inc.status}
                </span>
              </div>
              <div className="text-xs font-semibold text-slate-200 leading-snug">{inc.title}</div>
              <div className="flex items-center gap-2 mt-1.5 text-[10px] text-slate-500">
                <span>{inc.id}</span>
                <span>·</span>
                <span>{inc.cloud}</span>
                <span>·</span>
                <span>{inc.detectedAt}</span>
              </div>
            </button>
          ))}
        </div>

        {/* Incident detail */}
        <div className="lg:col-span-2 space-y-4">
          {/* Header */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className={`text-xs font-bold px-2 py-0.5 rounded border uppercase ${SEV_STYLE[selected.severity]}`}>
                {selected.severity}
              </span>
              <span className={`text-xs font-bold px-2 py-0.5 rounded border uppercase ${STATUS_STYLE[status]}`}>
                {status === "resolving" ? "AUTO-RESOLVING" : status.toUpperCase()}
              </span>
              <span className="text-xs text-slate-500">{selected.id}</span>
            </div>
            <h2 className="text-base font-semibold text-red-300">{selected.title}</h2>
            <div className="flex flex-wrap gap-4 mt-3 text-xs">
              <div className="flex items-center gap-1.5 text-slate-400">
                <Clock className="w-3.5 h-3.5" /> Detected {selected.detectedAt}
              </div>
              <div className="flex items-center gap-1.5 text-slate-400">
                <Cpu className="w-3.5 h-3.5" /> {selected.resource}
              </div>
              {selected.resolvedAt && (
                <div className="flex items-center gap-1.5 text-green-400">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Resolved {selected.resolvedAt}
                </div>
              )}
            </div>
            <div className="mt-3 flex flex-wrap gap-3">
              <div className="bg-slate-800 rounded-lg px-3 py-2">
                <div className="text-[10px] text-slate-500">AI Confidence</div>
                <div className="text-lg font-bold text-green-400">{selected.confidence}%</div>
              </div>
              <div className="bg-slate-800 rounded-lg px-3 py-2 flex-1 min-w-0">
                <div className="text-[10px] text-slate-500">Root Cause</div>
                <div className="text-sm font-semibold text-amber-300">{selected.rootCause}</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Timeline */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Timeline</h3>
              <div className="space-y-3 relative">
                {selected.timeline.map((t, i) => (
                  <div key={i} className="flex items-start gap-3 relative">
                    {i < selected.timeline.length - 1 && (
                      <div className="absolute left-[5px] top-4 bottom-0 w-px bg-slate-700" />
                    )}
                    <div className={`w-3 h-3 rounded-full border-2 flex-shrink-0 mt-0.5 bg-slate-950 ${TIMELINE_COLOR[t.type]}`} />
                    <div>
                      <div className={`text-xs font-semibold ${TIMELINE_COLOR[t.type]}`}>{t.time}</div>
                      <div className="text-xs text-slate-400 mt-0.5">{t.event}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Remediation actions */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Remediation Actions</h3>
              <div className="space-y-2">
                {actions.map((action, i) => (
                  <div key={i} className={`rounded-lg p-3 border-l-2 ${
                    action.status === "applied" ? "border-green-500 bg-green-900/10" :
                    action.status === "pending" ? "border-amber-500 bg-amber-900/10" :
                    "border-slate-600 bg-slate-800/40"
                  }`}>
                    <div className={`text-[10px] font-bold uppercase mb-1 ${
                      action.status === "applied" ? "text-green-400" :
                      action.status === "pending" ? "text-amber-400" : "text-slate-500"
                    }`}>
                      {action.status === "applied" ? "✓ Auto-applied" : action.status === "pending" ? "⏸ Awaiting approval" : "📊 Manual"}
                    </div>
                    <div className="text-xs text-slate-300 mb-2">{action.label}</div>
                    {action.status === "pending" && (
                      <button
                        onClick={() => approveAction(i)}
                        className="w-full rounded bg-green-700/50 border border-green-600 py-1 text-xs text-green-300 font-semibold hover:bg-green-700/70 transition-colors"
                      >
                        ✓ Approve
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
