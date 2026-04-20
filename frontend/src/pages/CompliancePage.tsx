import { useState } from "react";
import { CheckCircle2, AlertTriangle, Shield, FileText } from "lucide-react";
import { MOCK_COMPLIANCE_FRAMEWORKS, MOCK_AUDIT_LOG } from "@/lib/mockData";

type Framework = keyof typeof MOCK_COMPLIANCE_FRAMEWORKS;

function GaugeChart({ score }: { score: number }) {
  const r = 54; const cx = 70; const cy = 70;
  const circ = 2 * Math.PI * r;
  const fill = (score / 100) * circ;
  return (
    <svg width="140" height="140" viewBox="0 0 140 140">
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#1e293b" strokeWidth="14" />
      <circle cx={cx} cy={cy} r={r} fill="none"
        stroke={score >= 95 ? "#57A639" : score >= 80 ? "#F5C26B" : "#E74C3C"}
        strokeWidth="14" strokeDasharray={`${fill} ${circ - fill}`}
        strokeLinecap="round"
        style={{ transform: "rotate(-90deg)", transformOrigin: `${cx}px ${cy}px`, transition: "stroke-dasharray 1.5s ease" }}
      />
      <text x={cx} y={cy - 6} textAnchor="middle" fill="#f1f5f9" fontSize="20" fontWeight="700">{score}%</text>
      <text x={cx} y={cy + 12} textAnchor="middle" fill="#4ade80" fontSize="10">
        {score >= 95 ? "Excellent" : score >= 80 ? "Good" : "Needs work"}
      </text>
    </svg>
  );
}

export function CompliancePage() {
  const [tab, setTab] = useState<Framework>("soc2");
  const fw = MOCK_COMPLIANCE_FRAMEWORKS[tab];
  const overall = Math.round(
    Object.values(MOCK_COMPLIANCE_FRAMEWORKS).reduce((a, f) => a + f.score, 0) /
    Object.values(MOCK_COMPLIANCE_FRAMEWORKS).length
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold flex items-center gap-2">
            <Shield className="w-5 h-5 text-green-400" /> Compliance
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">Continuous monitoring · Audit-ready 24/7</p>
        </div>
        <button className="flex items-center gap-1.5 rounded bg-indigo-600 px-3 py-1.5 text-xs text-white font-semibold hover:bg-indigo-500">
          <FileText className="w-3.5 h-3.5" /> Generate Report
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Gauge + framework tabs */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col items-center gap-4">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Overall Score</div>
          <GaugeChart score={overall} />
          <div className="w-full space-y-1.5">
            {(Object.keys(MOCK_COMPLIANCE_FRAMEWORKS) as Framework[]).map((key) => {
              const f = MOCK_COMPLIANCE_FRAMEWORKS[key];
              return (
                <button key={key} onClick={() => setTab(key)}
                  className={`w-full flex items-center justify-between rounded-lg px-3 py-2 text-xs font-semibold transition-colors ${
                    tab === key ? "bg-indigo-600 text-white" : "border border-slate-700 text-slate-400 hover:bg-slate-800"
                  }`}>
                  <span>{f.name}</span>
                  <span className={f.score >= 95 ? "text-green-400" : "text-amber-400"}>{f.score}%</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Controls */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h2 className="text-sm font-semibold text-slate-300 mb-3">{fw.name} Controls</h2>
          <div className="space-y-2">
            {fw.controls.map((ctrl) => (
              <div key={ctrl.name} className={`rounded-lg p-3 border ${
                ctrl.status === "pass" ? "border-slate-800 bg-slate-800/30" : "border-amber-800/50 bg-amber-900/10"
              }`}>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2 text-sm font-medium text-slate-200">
                    {ctrl.status === "pass"
                      ? <CheckCircle2 className="w-4 h-4 text-green-400" />
                      : <AlertTriangle className="w-4 h-4 text-amber-400" />}
                    {ctrl.name}
                  </div>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${
                    ctrl.status === "pass"
                      ? "bg-green-900/40 text-green-300 border-green-700"
                      : "bg-amber-900/40 text-amber-300 border-amber-700"
                  }`}>{ctrl.pct}%</span>
                </div>
                <div className="h-1.5 bg-slate-700 rounded-full">
                  <div className={`h-full rounded-full transition-all ${ctrl.status === "pass" ? "bg-green-500" : "bg-amber-500"}`}
                    style={{ width: `${ctrl.pct}%` }} />
                </div>
                {"issue" in ctrl && ctrl.issue && (
                  <p className="text-xs text-amber-300/80 mt-1.5">⚠ {ctrl.issue as string}</p>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Audit log */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h2 className="text-sm font-semibold text-slate-300 mb-3">AI Audit Trail</h2>
          <div className="space-y-2.5">
            {MOCK_AUDIT_LOG.map((entry, i) => (
              <div key={i} className="border-b border-slate-800 pb-2.5 last:border-0 last:pb-0">
                <p className="text-xs text-slate-300 leading-snug">{entry.action}</p>
                <div className="flex justify-between mt-1 text-[10px] text-slate-500">
                  <span>{entry.actor}</span>
                  <span>{entry.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Framework score overview */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {(Object.entries(MOCK_COMPLIANCE_FRAMEWORKS) as [Framework, typeof MOCK_COMPLIANCE_FRAMEWORKS[Framework]][]).map(([key, f]) => (
          <button key={key} onClick={() => setTab(key)}
            className={`bg-slate-900 border rounded-xl p-4 text-left transition-colors hover:border-slate-600 ${tab === key ? "border-indigo-600" : "border-slate-800"}`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-400">{f.name}</span>
              <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${
                f.score >= 95 ? "bg-green-900/40 text-green-300 border-green-700"
                  : "bg-amber-900/40 text-amber-300 border-amber-700"
              }`}>{f.score}%</span>
            </div>
            <div className="h-1.5 bg-slate-700 rounded-full">
              <div className={`h-full rounded-full ${f.score >= 95 ? "bg-green-500" : "bg-amber-500"}`}
                style={{ width: `${f.score}%` }} />
            </div>
            <div className="text-[10px] text-slate-600 mt-1.5">
              {f.controls.filter((c) => c.status === "pass").length}/{f.controls.length} controls passing
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
