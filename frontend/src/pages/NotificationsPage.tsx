import { useState } from "react";
import { Bell, Plus, Trash2 } from "lucide-react";
import { MOCK_ALERT_RULES, MOCK_ALERTS_INBOX, type AlertRule } from "@/lib/mockData";

const SEV_STYLE: Record<string, string> = {
  critical: "bg-red-900/40 text-red-300 border-red-700",
  warning:  "bg-amber-900/40 text-amber-300 border-amber-700",
  info:     "bg-blue-900/40 text-blue-300 border-blue-700",
  resolved: "bg-green-900/40 text-green-300 border-green-700",
};

const CHANNEL_ICONS: Record<string, string> = {
  Slack: "💬", PagerDuty: "📟", Email: "📧", "In-App": "🔔", Teams: "🟦",
};

const ALL_CHANNELS = ["Slack", "PagerDuty", "Email", "In-App", "Teams"];

export function NotificationsPage() {
  const [rules, setRules] = useState(MOCK_ALERT_RULES);
  const [inbox] = useState(MOCK_ALERTS_INBOX);
  const [selected, setSelected] = useState<AlertRule>(rules[0]);
  const [testSent, setTestSent] = useState(false);

  function toggleRule(id: string) {
    setRules((r) => r.map((rule) => rule.id === id ? { ...rule, enabled: !rule.enabled } : rule));
    if (selected.id === id) setSelected((r) => ({ ...r, enabled: !r.enabled }));
  }

  function toggleChannel(ch: string) {
    const updated = selected.channels.includes(ch)
      ? selected.channels.filter((c) => c !== ch)
      : [...selected.channels, ch];
    const updatedRule = { ...selected, channels: updated };
    setSelected(updatedRule);
    setRules((r) => r.map((rule) => rule.id === selected.id ? updatedRule : rule));
  }

  function sendTest() {
    setTestSent(true);
    setTimeout(() => setTestSent(false), 3000);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold flex items-center gap-2">
            <Bell className="w-5 h-5 text-indigo-400" /> Notifications
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">Alert rules · escalation policies · multi-channel routing</p>
        </div>
        <button className="flex items-center gap-1.5 rounded bg-indigo-600 px-3 py-1.5 text-xs text-white font-semibold hover:bg-indigo-500">
          <Plus className="w-3.5 h-3.5" /> New Rule
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Alert rules list */}
        <div className="space-y-2">
          <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Alert Rules ({rules.length})</h2>
          {rules.map((rule) => (
            <button key={rule.id} onClick={() => setSelected(rule)}
              className={`w-full text-left rounded-xl border p-3 transition-colors ${
                selected.id === rule.id ? "border-indigo-600 bg-indigo-900/20" : "border-slate-800 bg-slate-900 hover:border-slate-700"
              }`}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-slate-200">{rule.name}</span>
                <button
                  onClick={(e) => { e.stopPropagation(); toggleRule(rule.id); }}
                  className={`w-8 h-4 rounded-full transition-colors relative flex-shrink-0 ${rule.enabled ? "bg-green-600" : "bg-slate-700"}`}>
                  <span className={`absolute top-0.5 w-3 h-3 bg-white rounded-full transition-all ${rule.enabled ? "left-4" : "left-0.5"}`} />
                </button>
              </div>
              <div className="font-mono text-[10px] text-slate-500 mb-1.5 bg-slate-800 rounded px-1.5 py-0.5 truncate">{rule.condition}</div>
              <div className="flex flex-wrap gap-1">
                {rule.channels.map((ch) => (
                  <span key={ch} className="text-[10px] text-slate-400">{CHANNEL_ICONS[ch]}</span>
                ))}
              </div>
            </button>
          ))}
        </div>

        {/* Rule editor */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-300">{selected.name}</h2>
              <div className="flex gap-2">
                <button onClick={sendTest}
                  className={`rounded border px-3 py-1 text-xs font-semibold transition-all ${testSent ? "border-green-600 bg-green-900/30 text-green-300" : "border-slate-600 text-slate-400 hover:bg-slate-800"}`}>
                  {testSent ? "✓ Test sent!" : "⚡ Test Alert"}
                </button>
                <button className="rounded border border-red-800 p-1 text-red-400 hover:bg-red-900/20">
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <div className="bg-slate-950 rounded-lg p-3">
              <div className="text-xs text-slate-500 mb-1.5 font-semibold uppercase tracking-wider">Trigger Condition</div>
              <div className="font-mono text-xs text-indigo-300">{selected.condition}</div>
            </div>

            <div>
              <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-2">Notification Channels</div>
              <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
                {ALL_CHANNELS.map((ch) => {
                  const active = selected.channels.includes(ch);
                  return (
                    <button key={ch} onClick={() => toggleChannel(ch)}
                      className={`flex flex-col items-center gap-1 rounded-xl border p-2.5 text-xs transition-all ${
                        active ? "border-indigo-600 bg-indigo-900/20 text-indigo-300" : "border-slate-700 text-slate-500 hover:border-slate-600"
                      }`}>
                      <span className="text-xl">{CHANNEL_ICONS[ch]}</span>
                      <span className="font-medium">{ch}</span>
                      {active && <span className="text-[9px] text-indigo-400">✓</span>}
                    </button>
                  );
                })}
              </div>
            </div>

            <div>
              <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-2">Escalation Policy</div>
              <div className="space-y-2">
                {selected.escalation.map((step, i) => (
                  <div key={i} className="flex items-center gap-3 bg-slate-950 rounded-lg px-3 py-2.5">
                    <span className={`text-xs font-bold min-w-[28px] ${i === 0 ? "text-blue-400" : i === 1 ? "text-amber-400" : "text-red-400"}`}>
                      {step.delay}
                    </span>
                    <span className="text-xs text-slate-300 flex-1">{step.target}</span>
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${
                      i === 0 ? "bg-blue-900/40 text-blue-300 border-blue-700"
                        : i === 1 ? "bg-amber-900/40 text-amber-300 border-amber-700"
                        : "bg-red-900/40 text-red-300 border-red-700"
                    }`}>{i === 0 ? "immediate" : "if unacked"}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Inbox */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-300">Recent Alerts</h2>
          <span className="text-xs text-slate-500">{inbox.length} alerts</span>
        </div>
        <div className="divide-y divide-slate-800">
          {inbox.map((alert) => (
            <div key={alert.id} className="flex items-center gap-4 px-4 py-3 hover:bg-slate-800/30">
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase flex-shrink-0 ${SEV_STYLE[alert.severity]}`}>
                {alert.severity}
              </span>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-medium text-slate-200 truncate">{alert.title}</div>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <span className="text-xs text-slate-500">{CHANNEL_ICONS[alert.channel]} {alert.channel}</span>
                <span className="text-xs text-slate-600">{alert.time}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
