import {
  Radar,
  ShieldCheck,
  TrendingDown,
  MessageSquareCode,
  FileCheck2,
  BellRing,
} from "lucide-react";
import { AnimateOnScroll } from "../ui/AnimateOnScroll";

const FEATURES = [
  {
    icon: Radar,
    color: "text-primary-500",
    bg: "bg-primary-50",
    title: "AI-Powered Monitoring & Discovery",
    description:
      "Automatically map your entire infrastructure topology across clouds. Real-time resource monitoring with multi-modal analysis of logs, metrics, traces, and cost data — all correlated by AI.",
    bullets: [
      "Automated topology mapping across GCP, AWS, Azure",
      "Anomaly detection with confidence scores",
      "Multi-modal analysis: logs, metrics, traces, cost",
      "Real-time alerts with zero manual rule configuration",
    ],
    mockup: (
      <div className="bg-gray-900 rounded-xl p-5 font-mono text-xs space-y-2">
        <div className="flex items-center gap-2 text-green-400">
          <span className="text-gray-500">►</span>
          <span>Scanning 847 resources across 3 clouds...</span>
        </div>
        <div className="flex items-center gap-2 text-yellow-400">
          <span className="text-gray-500">⚠</span>
          <span>Anomaly detected: GKE node cpu=94%</span>
        </div>
        <div className="flex items-center gap-2 text-blue-400">
          <span className="text-gray-500">→</span>
          <span>Root cause: memory leak in payment-svc</span>
        </div>
        <div className="flex items-center gap-2 text-green-400">
          <span className="text-gray-500">✓</span>
          <span>Auto-remediation triggered (confidence: 97%)</span>
        </div>
      </div>
    ),
    imageLeft: false,
  },
  {
    icon: ShieldCheck,
    color: "text-secondary-500",
    bg: "bg-teal-50",
    title: "Intelligent Incident Response",
    description:
      "AI-powered root cause analysis surfaces the exact source of every incident. Automated remediation workflows with customizable approval gates resolve issues before users notice.",
    bullets: [
      "Root cause analysis in seconds, not hours",
      "Automated remediation with approval workflows",
      "Timeline-based incident tracking",
      "23 incidents auto-resolved daily on average",
    ],
    mockup: (
      <div className="bg-white rounded-xl border border-gray-100 p-4 space-y-3">
        {[
          { severity: "P1", service: "payment-svc", status: "Resolved", time: "12:04:32", color: "bg-error text-white" },
          { severity: "P2", service: "auth-api", status: "Auto-fixed", time: "12:01:19", color: "bg-warning text-white" },
          { severity: "P3", service: "analytics-worker", status: "Monitoring", time: "11:58:44", color: "bg-primary-500 text-white" },
        ].map((i) => (
          <div key={i.service} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-3">
              <span className={`text-xs font-bold px-2 py-0.5 rounded ${i.color}`}>{i.severity}</span>
              <span className="text-sm font-medium text-gray-800">{i.service}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-500">{i.time}</span>
              <span className="text-xs font-semibold text-success">{i.status}</span>
            </div>
          </div>
        ))}
      </div>
    ),
    imageLeft: true,
  },
  {
    icon: TrendingDown,
    color: "text-success",
    bg: "bg-green-50",
    title: "Cost Optimization Intelligence",
    description:
      "FinOps intelligence that directly impacts your bottom line. AI-driven rightsizing, idle resource detection, and reserved capacity optimization deliver measurable savings from day one.",
    bullets: [
      "Idle resource detection and auto-shutdown",
      "Rightsizing recommendations with ROI forecasts",
      "Reserved instance and commitment optimization",
      "Multi-cloud cost comparison and chargeback",
    ],
    mockup: (
      <div className="bg-white rounded-xl border border-gray-100 p-4">
        <div className="text-sm font-semibold text-gray-700 mb-3">Cost Savings Opportunities</div>
        {[
          { resource: "8x m5.2xlarge (idle)", saving: "$4,200/mo", action: "Rightsizing" },
          { resource: "Unattached EBS volumes", saving: "$890/mo", action: "Cleanup" },
          { resource: "Reserved capacity gap", saving: "$11,400/mo", action: "Commit" },
        ].map((r) => (
          <div key={r.resource} className="flex items-center justify-between py-2.5 border-b border-gray-50 last:border-0">
            <div>
              <div className="text-xs font-medium text-gray-800">{r.resource}</div>
              <div className="text-xs text-gray-400">{r.action}</div>
            </div>
            <div className="text-sm font-bold text-success">{r.saving}</div>
          </div>
        ))}
        <div className="mt-3 pt-3 border-t border-gray-100 flex justify-between">
          <span className="text-xs font-semibold text-gray-500">Total potential</span>
          <span className="text-base font-bold text-success">$16,490/mo</span>
        </div>
      </div>
    ),
    imageLeft: false,
  },
  {
    icon: MessageSquareCode,
    color: "text-purple-500",
    bg: "bg-purple-50",
    title: "AI ChatOps Assistant",
    description:
      "Ask questions about your infrastructure in plain English. RAG-powered search across logs, runbooks, documentation, and incident history gives instant, contextually-aware answers.",
    bullets: [
      "Natural language queries across all infrastructure",
      "Automated runbook execution from chat",
      "Conversational troubleshooting with context memory",
      "Knowledge base search across logs and docs",
    ],
    mockup: (
      <div className="bg-gray-900 rounded-xl p-4 space-y-3">
        <div className="flex gap-3">
          <div className="w-7 h-7 rounded-full bg-gray-700 flex items-center justify-center text-xs text-gray-300 flex-shrink-0">U</div>
          <div className="bg-gray-800 rounded-xl rounded-tl-sm px-3 py-2 text-sm text-gray-200 max-w-[85%]">
            Why is production latency high right now?
          </div>
        </div>
        <div className="flex gap-3">
          <div className="w-7 h-7 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
            <span className="text-[10px] text-white font-bold">AI</span>
          </div>
          <div className="bg-primary-900/40 border border-primary-800/50 rounded-xl rounded-tl-sm px-3 py-2 text-sm text-gray-200 max-w-[85%]">
            P95 latency spiked 340ms at 12:04 UTC. Root cause:{" "}
            <span className="text-primary-300 font-medium">payment-svc</span> has a goroutine leak (3.2k goroutines, normal: ~120). I can restart the pod — want me to proceed?
          </div>
        </div>
      </div>
    ),
    imageLeft: true,
  },
  {
    icon: FileCheck2,
    color: "text-orange-500",
    bg: "bg-orange-50",
    title: "Compliance & Audit Trail",
    description:
      "Continuous compliance monitoring across SOC 2, ISO 27001, GDPR, and HIPAA frameworks. Every AI action and infrastructure change is logged with tamper-proof audit trails.",
    bullets: [
      "Continuous compliance for SOC 2, ISO 27001, GDPR",
      "Infrastructure-as-Code drift detection",
      "AI agent activity audit logs",
      "Automated PDF compliance reports",
    ],
    mockup: (
      <div className="bg-white rounded-xl border border-gray-100 p-4">
        <div className="text-sm font-semibold text-gray-700 mb-3">Compliance Posture</div>
        {[
          { framework: "SOC 2 Type II", score: 98, passing: "147/150" },
          { framework: "ISO 27001", score: 94, passing: "89/94" },
          { framework: "GDPR", score: 100, passing: "62/62" },
        ].map((f) => (
          <div key={f.framework} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
            <div>
              <div className="text-xs font-semibold text-gray-800">{f.framework}</div>
              <div className="text-xs text-gray-400">{f.passing} controls passing</div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full bg-success rounded-full" style={{ width: `${f.score}%` }} />
              </div>
              <span className="text-xs font-bold text-success">{f.score}%</span>
            </div>
          </div>
        ))}
      </div>
    ),
    imageLeft: false,
  },
  {
    icon: BellRing,
    color: "text-blue-500",
    bg: "bg-blue-50",
    title: "Multi-Channel Alerts & Escalation",
    description:
      "Intelligent alert routing that gets the right information to the right person at the right time. Integrate with Slack, PagerDuty, Teams, and email with customizable escalation policies.",
    bullets: [
      "Slack, PagerDuty, Teams, email integration",
      "Smart deduplication — no more alert storms",
      "On-call rotation management and SLA tracking",
      "Customizable escalation rules per service tier",
    ],
    mockup: (
      <div className="bg-gray-900 rounded-xl p-4 space-y-2">
        {[
          { channel: "#infra-alerts", msg: "✅ GKE autoscale triggered — 3→5 nodes", time: "now", color: "text-green-400" },
          { channel: "#on-call", msg: "🔥 P1: payment-svc latency > 2s — PD triggered", time: "2m", color: "text-red-400" },
          { channel: "#cost-alerts", msg: "💰 New saving: $4,200/mo — idle instances", time: "15m", color: "text-yellow-400" },
        ].map((n) => (
          <div key={n.channel} className="flex items-start gap-2 p-2.5 bg-gray-800 rounded-lg">
            <span className={`text-xs font-bold ${n.color} flex-shrink-0 pt-0.5`}>
              {n.channel}
            </span>
            <div>
              <div className="text-xs text-gray-200">{n.msg}</div>
              <div className="text-xs text-gray-500 mt-0.5">{n.time} ago</div>
            </div>
          </div>
        ))}
      </div>
    ),
    imageLeft: true,
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="section-padding bg-white">
      <div className="container-max">
        <AnimateOnScroll className="text-center mb-20">
          <div className="section-label">
            <span className="w-1.5 h-1.5 rounded-full bg-primary-500" />
            Platform Features
          </div>
          <h2 className="section-heading mb-4">
            One Platform to Monitor, Optimize,{" "}
            <span className="gradient-text">and Automate</span>
          </h2>
          <p className="section-subheading mx-auto">
            Every capability you need to run world-class infrastructure operations —
            powered by AI, designed for reliability.
          </p>
        </AnimateOnScroll>

        <div className="space-y-24">
          {FEATURES.map(({ icon: Icon, color, bg, title, description, bullets, mockup, imageLeft }) => (
            <div
              key={title}
              className={`grid lg:grid-cols-2 gap-16 items-center ${imageLeft ? "lg:flex-row-reverse" : ""}`}
            >
              <AnimateOnScroll direction={imageLeft ? "right" : "left"}>
                <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-6 ${bg}">
                  <div className={`w-12 h-12 rounded-xl ${bg} flex items-center justify-center`}>
                    <Icon className={`w-6 h-6 ${color}`} />
                  </div>
                </div>
                <h3 className="text-3xl font-bold text-gray-900 mb-4 leading-tight">
                  {title}
                </h3>
                <p className="text-gray-500 leading-relaxed mb-6">{description}</p>
                <ul className="space-y-3">
                  {bullets.map((b) => (
                    <li key={b} className="flex items-start gap-3">
                      <div className="w-5 h-5 rounded-full bg-primary-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                      </div>
                      <span className="text-sm text-gray-600">{b}</span>
                    </li>
                  ))}
                </ul>
              </AnimateOnScroll>

              <AnimateOnScroll
                direction={imageLeft ? "left" : "right"}
                className={imageLeft ? "lg:order-first" : ""}
              >
                {mockup}
              </AnimateOnScroll>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
