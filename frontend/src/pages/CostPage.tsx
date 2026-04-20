import { useState } from "react";
import { DollarSign, TrendingDown, AlertTriangle, Zap } from "lucide-react";
import { MOCK_COST_RECS, MOCK_COST_BREAKDOWN } from "@/lib/mockData";

const CLOUD_BADGE: Record<string, string> = {
  GCP:   "bg-blue-900/40 text-blue-300 border-blue-700",
  AWS:   "bg-orange-900/40 text-orange-300 border-orange-700",
  Azure: "bg-cyan-900/40 text-cyan-300 border-cyan-700",
};

function DonutChart() {
  const breakdown = MOCK_COST_BREAKDOWN;
  const r = 54; const cx = 70; const cy = 70;
  const circ = 2 * Math.PI * r;
  let offset = 0;
  const segments = breakdown.map((b) => {
    const dash = (b.pct / 100) * circ;
    const seg = { ...b, dash, offset };
    offset += dash;
    return seg;
  });

  return (
    <div className="flex flex-col items-center gap-4">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#1e293b" strokeWidth="16" />
        {segments.map((seg, i) => (
          <circle key={i} cx={cx} cy={cy} r={r} fill="none"
            stroke={seg.color} strokeWidth="16"
            strokeDasharray={`${seg.dash} ${circ - seg.dash}`}
            strokeDashoffset={-seg.offset}
            style={{ transform: "rotate(-90deg)", transformOrigin: `${cx}px ${cy}px`, transition: "stroke-dasharray 1.5s ease" }}
          />
        ))}
        <text x={cx} y={cy - 6} textAnchor="middle" fill="#f1f5f9" fontSize="14" fontWeight="700">$47K</text>
        <text x={cx} y={cy + 10} textAnchor="middle" fill="#94a3b8" fontSize="9">monthly</text>
      </svg>
      <div className="space-y-1.5 w-full">
        {breakdown.map((b) => (
          <div key={b.label} className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ background: b.color }} />
            <span className="text-slate-400 flex-1">{b.label}</span>
            <span className="text-slate-300 font-medium">{b.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function TrendChart() {
  const points = [42, 45, 43, 47, 44, 41, 38, 36, 34, 31, 28, 25];
  const max = Math.max(...points); const min = Math.min(...points);
  const range = max - min || 1;
  const w = 200; const h = 60;
  const coords = points.map((p, i) => `${(i / (points.length - 1)) * w},${h - ((p - min) / range) * (h - 8) - 4}`);
  const polyline = coords.join(" ");

  return (
    <svg width="100%" height="70" viewBox={`0 0 ${w} ${h + 10}`} preserveAspectRatio="none">
      <defs>
        <linearGradient id="cgr" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0A66C2" stopOpacity=".3" />
          <stop offset="100%" stopColor="#0A66C2" stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon points={`0,${h} ${polyline} ${w},${h}`} fill="url(#cgr)" />
      <polyline points={polyline} fill="none" stroke="#0A66C2" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function CostPage() {
  const [recs, setRecs] = useState(MOCK_COST_RECS);

  function approve(id: string) {
    setRecs((r) => r.map((rec) => rec.id === id ? { ...rec, status: "approved" as const } : rec));
  }
  function approveAll() {
    setRecs((r) => r.map((rec) => ({ ...rec, status: "approved" as const })));
  }

  const totalSavings = recs.filter((r) => r.status === "pending").reduce((a, r) => a + r.saving, 0);
  const approved = recs.filter((r) => r.status === "approved").length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Cost Optimization</h1>
          <p className="text-xs text-slate-500 mt-0.5">FinOps · AI-driven recommendations · Updated 5 min ago</p>
        </div>
        <span className="text-xs font-semibold text-green-400 bg-green-900/20 border border-green-800/40 px-3 py-1.5 rounded-full">
          ↓ 40% vs last month
        </span>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: DollarSign,   label: "Monthly Spend",      value: "$47,324",  sub: "↓ 40% vs last month",         color: "text-amber-400",  bg: "bg-amber-500/10" },
          { icon: TrendingDown, label: "Projected Savings",  value: "$23,150",  sub: "AI-optimized recommendations", color: "text-green-400",  bg: "bg-green-500/10" },
          { icon: AlertTriangle,label: "Idle Resources",     value: "17",       sub: "Action needed",                color: "text-red-400",    bg: "bg-red-500/10"   },
          { icon: Zap,          label: "Optimization Score", value: "78 / 100", sub: "↑ +12 this week",              color: "text-blue-400",   bg: "bg-blue-500/10"  },
        ].map(({ icon: Icon, label, value, sub, color, bg }) => (
          <div key={label} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className={`w-9 h-9 ${bg} rounded-lg flex items-center justify-center mb-3`}>
              <Icon className={`w-5 h-5 ${color}`} />
            </div>
            <div className={`text-xl font-bold ${color}`}>{value}</div>
            <div className="text-xs text-slate-500 mt-0.5">{label}</div>
            <div className="text-xs text-slate-600 mt-0.5">{sub}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Donut chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">Spend by Service</h2>
          <DonutChart />
        </div>

        {/* Trend chart */}
        <div className="lg:col-span-3 bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Cost Trend — Last 12 Months</h2>
            <span className="text-xs text-green-400 font-semibold">↓ $22K saved</span>
          </div>
          <TrendChart />
          <div className="flex justify-between text-[10px] text-slate-600 mt-1">
            <span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span>
            <span>Jul</span><span>Aug</span><span>Sep</span><span>Oct</span><span>Nov</span><span>Dec</span>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
          <div>
            <h2 className="text-sm font-semibold text-slate-300">AI Recommendations</h2>
            <p className="text-xs text-slate-500 mt-0.5">{approved}/{recs.length} approved · ${totalSavings.toLocaleString()} / mo savings pending</p>
          </div>
          {recs.some((r) => r.status === "pending") && (
            <button onClick={approveAll}
              className="rounded bg-green-700/50 border border-green-600 px-3 py-1.5 text-xs text-green-300 font-semibold hover:bg-green-700/70">
              ✓ Approve All — ${totalSavings.toLocaleString()}/mo
            </button>
          )}
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-xs">
            <thead className="bg-slate-950/50">
              <tr>
                {["Resource", "Cloud", "Issue", "Savings / mo", "Action", ""].map((h) => (
                  <th key={h} className="px-4 py-2.5 text-left text-slate-500 font-medium uppercase tracking-wider text-[10px]">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {recs.map((rec) => (
                <tr key={rec.id} className="border-t border-slate-800 hover:bg-slate-800/30">
                  <td className="px-4 py-3 font-medium text-slate-200">{rec.resource}</td>
                  <td className="px-4 py-3">
                    <span className={`px-1.5 py-0.5 rounded border text-[10px] font-bold ${CLOUD_BADGE[rec.cloud]}`}>{rec.cloud}</span>
                  </td>
                  <td className="px-4 py-3 text-amber-300">{rec.issue}</td>
                  <td className="px-4 py-3 text-green-400 font-semibold">${rec.saving.toLocaleString()}</td>
                  <td className="px-4 py-3 text-slate-400">{rec.action}</td>
                  <td className="px-4 py-3">
                    {rec.status === "approved" ? (
                      <span className="text-green-400 font-semibold text-xs">✓ Applied</span>
                    ) : (
                      <button onClick={() => approve(rec.id)}
                        className="rounded border border-green-700 bg-green-900/30 px-2.5 py-1 text-xs text-green-300 hover:bg-green-900/50">
                        Approve
                      </button>
                    )}
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
