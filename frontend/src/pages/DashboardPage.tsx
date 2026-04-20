import { useEffect, useRef, useState } from "react";
import {
  Activity, AlertTriangle, CheckCircle2, DollarSign, Server,
  Shield, TrendingDown, Zap,
} from "lucide-react";
import {
  MOCK_ACTIVITY, MOCK_METRICS, MOCK_RESOURCES, RESOURCE_EDGES,
} from "@/lib/mockData";

function Counter({ to, prefix = "", suffix = "" }: { to: number; prefix?: string; suffix?: string }) {
  const [val, setVal] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    let active = true;
    const obs = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return;
      obs.disconnect();
      const start = performance.now();
      const dur = 1200;
      const step = (now: number) => {
        if (!active) return;
        const p = Math.min(1, (now - start) / dur);
        const ease = 1 - Math.pow(1 - p, 3);
        setVal(Math.floor(ease * to));
        if (p < 1) { rafRef.current = requestAnimationFrame(step); }
        else setVal(to);
      };
      rafRef.current = requestAnimationFrame(step);
    });
    if (ref.current) obs.observe(ref.current);
    return () => {
      active = false;
      obs.disconnect();
      cancelAnimationFrame(rafRef.current);
    };
  }, [to]);

  return (
    <span ref={ref}>
      {prefix}{val.toLocaleString()}{suffix}
    </span>
  );
}

const ACTIVITY_COLORS: Record<string, string> = {
  resolved: "bg-green-500", alert: "bg-red-500", deploy: "bg-blue-500",
  cost: "bg-amber-500", security: "bg-teal-500",
};

const CLOUD_COLORS: Record<string, string> = {
  GCP: "text-blue-400 border-blue-500 bg-blue-500/10",
  AWS: "text-orange-400 border-orange-500 bg-orange-500/10",
  Azure: "text-cyan-400 border-cyan-500 bg-cyan-500/10",
};

export function DashboardPage() {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [feed, setFeed] = useState(MOCK_ACTIVITY);

  // Simulate live activity feed
  useEffect(() => {
    const msgs = [
      { id: "live1", type: "resolved", message: "Auto-scaled Cloud Run — traffic spike handled", time: "just now", cloud: "GCP" },
      { id: "live2", type: "alert",    message: "Lambda cold start latency > 800ms",             time: "just now", cloud: "AWS" },
    ];
    let i = 0;
    const t = setInterval(() => {
      if (i >= msgs.length) { clearInterval(t); return; }
      setFeed((f) => [msgs[i++], ...f.slice(0, 5)]);
    }, 4000);
    return () => clearInterval(t);
  }, []);

  const selected = MOCK_RESOURCES.find((r) => r.id === selectedNode);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-100">Dashboard</h1>
          <p className="text-xs text-slate-500 mt-0.5">Production · All regions · Live</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-green-400 bg-green-900/20 border border-green-800/50 px-3 py-1.5 rounded-full">
          <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
          All systems healthy
        </div>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Server,       label: "Resources Monitored",     val: MOCK_METRICS.resourcesMonitored, suffix: "",   color: "text-blue-400",   bg: "bg-blue-500/10",   trend: "+12 today" },
          { icon: Zap,          label: "Incidents Auto-Resolved",  val: MOCK_METRICS.incidentsAutoResolved, suffix: "", color: "text-green-400", bg: "bg-green-500/10", trend: "67% MTTR ↓" },
          { icon: DollarSign,   label: "Saved This Month",         val: MOCK_METRICS.monthlySavings, prefix: "$", color: "text-amber-400", bg: "bg-amber-500/10",  trend: "↑ 40% vs last" },
          { icon: Shield,       label: "Compliance Score",         val: Math.floor(MOCK_METRICS.complianceScore), suffix: "%", color: "text-teal-400", bg: "bg-teal-500/10", trend: "SOC2 · ISO27001" },
        ].map(({ icon: Icon, label, val, prefix = "", suffix, color, bg, trend }) => (
          <div key={label} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-start justify-between mb-3">
              <div className={`w-9 h-9 rounded-lg ${bg} flex items-center justify-center`}>
                <Icon className={`w-5 h-5 ${color}`} />
              </div>
            </div>
            <div className="text-2xl font-bold text-slate-100">
              <Counter to={val} prefix={prefix} suffix={suffix} />
            </div>
            <div className="text-xs text-slate-500 mt-0.5">{label}</div>
            <div className="text-xs text-green-400 font-medium mt-1">{trend}</div>
          </div>
        ))}
      </div>

      {/* Topology + Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Topology map */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-slate-300">Multi-Cloud Topology</h2>
            <div className="flex gap-3 text-xs">
              <span className="text-blue-400">● GCP (312)</span>
              <span className="text-orange-400">● AWS (289)</span>
              <span className="text-cyan-400">● Azure (246)</span>
            </div>
          </div>
          <div className="relative bg-slate-950 rounded-lg overflow-hidden" style={{ height: 220 }}>
            <svg className="absolute inset-0 w-full h-full">
              {RESOURCE_EDGES.map(([a, b]) => {
                const ra = MOCK_RESOURCES.find((r) => r.id === a);
                const rb = MOCK_RESOURCES.find((r) => r.id === b);
                if (!ra || !rb) return null;
                return (
                  <line key={`${a}-${b}`}
                    x1={`${ra.x + 2}%`} y1={`${ra.y + 2}%`}
                    x2={`${rb.x + 2}%`} y2={`${rb.y + 2}%`}
                    stroke="#334155" strokeWidth="1" strokeDasharray="4"
                  />
                );
              })}
            </svg>
            {MOCK_RESOURCES.map((r) => (
              <button
                key={r.id}
                onClick={() => setSelectedNode(r.id === selectedNode ? null : r.id)}
                className={`absolute w-10 h-10 rounded-full border-2 flex items-center justify-center text-xs font-bold transition-transform hover:scale-110 cursor-pointer
                  ${r.status === "warning" ? "animate-pulse" : ""}
                  ${selectedNode === r.id ? "scale-125 z-10" : ""}
                  ${CLOUD_COLORS[r.cloud]}`}
                style={{ left: `${r.x}%`, top: `${r.y}%`, transform: selectedNode === r.id ? "scale(1.2)" : undefined }}
                title={r.name}
              >
                {r.cloud.slice(0, 3)}
              </button>
            ))}
            {MOCK_RESOURCES.some((r) => r.status === "warning") && (
              <div className="absolute top-2 right-2 flex items-center gap-1.5 bg-red-900/80 border border-red-700 rounded-full px-2 py-0.5 text-xs text-red-300 font-semibold">
                <AlertTriangle className="w-3 h-3" /> 1 Anomaly
              </div>
            )}
          </div>
          {selected && (
            <div className="mt-3 bg-slate-800 rounded-lg p-3 flex flex-wrap gap-4 text-xs">
              <div><span className="text-slate-500">Resource</span> <span className="text-slate-200 font-medium">{selected.name}</span></div>
              <div><span className="text-slate-500">Region</span> <span className="text-slate-200">{selected.region}</span></div>
              <div><span className="text-slate-500">Status</span> <span className={selected.status === "healthy" ? "text-green-400 font-semibold" : "text-amber-400 font-semibold"}>{selected.status}</span></div>
              <div className="flex items-center gap-2"><span className="text-slate-500">CPU</span>
                <div className="w-20 h-1.5 bg-slate-700 rounded-full"><div className="h-full rounded-full bg-blue-500" style={{ width: `${selected.cpu}%` }} /></div>
                <span className="text-slate-200">{selected.cpu}%</span>
              </div>
              <div className="flex items-center gap-2"><span className="text-slate-500">Mem</span>
                <div className="w-20 h-1.5 bg-slate-700 rounded-full"><div className="h-full rounded-full bg-teal-500" style={{ width: `${selected.memory}%` }} /></div>
                <span className="text-slate-200">{selected.memory}%</span>
              </div>
            </div>
          )}
        </div>

        {/* Activity feed */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h2 className="text-sm font-semibold text-slate-300 mb-3">Live Activity</h2>
          <div className="space-y-2.5">
            {feed.map((item) => (
              <div key={item.id} className="flex items-start gap-2.5 text-xs">
                <div className={`w-2 h-2 rounded-full mt-1 flex-shrink-0 ${ACTIVITY_COLORS[item.type] ?? "bg-slate-500"}`} />
                <div className="min-w-0">
                  <div className="text-slate-300 leading-snug">{item.message}</div>
                  <div className="text-slate-600 mt-0.5">{item.cloud} · {item.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick stats row */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { icon: TrendingDown, label: "MTTR Reduction",        value: "67%",   sub: "vs 3-month baseline",   color: "text-green-400"  },
          { icon: Activity,     label: "Uptime (30 days)",       value: "99.94%",sub: "3 nines · 26 min down", color: "text-blue-400"   },
          { icon: CheckCircle2, label: "Automation Coverage",   value: "95%",   sub: "of runbooks automated", color: "text-teal-400"   },
        ].map(({ icon: Icon, label, value, sub, color }) => (
          <div key={label} className="bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 flex items-center gap-4">
            <Icon className={`w-7 h-7 ${color} flex-shrink-0`} />
            <div>
              <div className={`text-2xl font-bold ${color}`}>{value}</div>
              <div className="text-xs text-slate-500">{label}</div>
              <div className="text-xs text-slate-600">{sub}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
