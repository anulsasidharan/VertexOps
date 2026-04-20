"use client";
import { useState } from "react";
import { ArrowRight, Play, CheckCircle2, TrendingDown, Clock, Cpu } from "lucide-react";
import { AnimatedCounter } from "../ui/AnimatedCounter";
import { DemoModal } from "../ui/DemoModal";

const STATS = [
  { value: 67, suffix: "%", label: "MTTR Reduction", icon: Clock },
  { value: 40, suffix: "%", label: "Cost Savings", icon: TrendingDown },
  { value: 95, suffix: "%", label: "Automation Coverage", icon: Cpu },
];

const TRUST_ITEMS = [
  "No credit card required",
  "14-day free trial",
  "Setup in 5 minutes",
];

export function HeroSection() {
  const [demoOpen, setDemoOpen] = useState(false);

  return (
    <>
    <section className="relative min-h-screen flex items-center pt-16 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-primary-50/60 via-white to-white" />
      <div
        className="absolute inset-0 bg-grid-pattern bg-grid-size opacity-50"
        style={{ maskImage: "linear-gradient(to bottom, transparent, black 20%, black 80%, transparent)" }}
      />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-primary-500/8 rounded-full blur-3xl" />

      <div className="relative max-w-7xl mx-auto px-6 py-20">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left: Copy */}
          <div>
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-primary-50 border border-primary-100 rounded-full mb-6 animate-fade-in">
              <span className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" />
              <span className="text-xs font-semibold text-primary-600 uppercase tracking-wide">
                AI-Powered LLMOps Platform
              </span>
            </div>

            <h1
              className="text-5xl md:text-6xl font-bold text-gray-900 leading-[1.1] tracking-tight mb-6"
              style={{ animationDelay: "100ms" }}
            >
              AI-Powered{" "}
              <span className="gradient-text">Infrastructure Intelligence</span>{" "}
              for Modern DevOps Teams
            </h1>

            <p className="text-xl text-gray-500 leading-relaxed mb-8 max-w-xl">
              Transform multi-cloud chaos into clarity with automated monitoring,
              intelligent incident response, and proactive cost optimization
              across GCP, AWS, and Azure.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-3 mb-10">
              <a href="#pricing" className="btn-primary px-7 py-3.5 text-base rounded-xl">
                Request Demo
                <ArrowRight className="w-4 h-4" />
              </a>
              <button
                onClick={() => setDemoOpen(true)}
                className="btn-secondary px-7 py-3.5 text-base rounded-xl group"
              >
                <div className="w-7 h-7 rounded-full bg-primary-100 flex items-center justify-center group-hover:bg-primary-200 transition-colors">
                  <Play className="w-3 h-3 text-primary-600 fill-primary-600" />
                </div>
                Watch Demo
              </button>
            </div>

            {/* Trust line */}
            <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
              {TRUST_ITEMS.map((item) => (
                <div key={item} className="flex items-center gap-1.5 text-sm text-gray-500">
                  <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />
                  {item}
                </div>
              ))}
            </div>
          </div>

          {/* Right: Dashboard mockup */}
          <div className="relative hidden lg:block">
            {/* Floating stat cards */}
            <div className="absolute -top-4 -left-6 z-10 bg-white rounded-xl shadow-card border border-gray-100 px-4 py-3 flex items-center gap-3 animate-float">
              <div className="w-9 h-9 rounded-lg bg-success/10 flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-success" />
              </div>
              <div>
                <div className="text-xs font-medium text-gray-500">Incident Resolved</div>
                <div className="text-sm font-bold text-gray-900">CPU spike — Auto-fixed</div>
              </div>
            </div>

            <div className="absolute -bottom-4 -right-4 z-10 bg-white rounded-xl shadow-card border border-gray-100 px-4 py-3"
              style={{ animationDelay: "1.5s" }}>
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-primary-50 flex items-center justify-center">
                  <TrendingDown className="w-5 h-5 text-primary-500" />
                </div>
                <div>
                  <div className="text-xs font-medium text-gray-500">Monthly Savings</div>
                  <div className="text-sm font-bold text-gray-900">$47,000+</div>
                </div>
              </div>
            </div>

            {/* Main dashboard card */}
            <div className="dashboard-glow rounded-2xl overflow-hidden border border-gray-200 bg-white">
              {/* Top bar */}
              <div className="bg-gray-900 px-4 py-3 flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-400" />
                  <div className="w-3 h-3 rounded-full bg-yellow-400" />
                  <div className="w-3 h-3 rounded-full bg-green-400" />
                </div>
                <div className="flex-1 mx-4 bg-gray-800 rounded px-3 py-1 text-xs text-gray-400 font-mono">
                  vertexops.dashboard
                </div>
              </div>
              {/* Dashboard body */}
              <div className="bg-gray-50 p-5">
                {/* Header row */}
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <div className="text-xs text-gray-500 font-medium mb-0.5">Infrastructure Overview</div>
                    <div className="text-base font-bold text-gray-900">Production — All Regions</div>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-success font-medium bg-success/10 px-2.5 py-1 rounded-full">
                    <div className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
                    All systems healthy
                  </div>
                </div>

                {/* Metric grid */}
                <div className="grid grid-cols-3 gap-3 mb-4">
                  {[
                    { label: "Resources Monitored", value: "847", trend: "+12%" },
                    { label: "Active Incidents", value: "0", trend: "—" },
                    { label: "Monthly Savings", value: "$47K", trend: "↑ 23%" },
                  ].map((m) => (
                    <div key={m.label} className="bg-white rounded-xl p-3 border border-gray-100">
                      <div className="text-xs text-gray-500 mb-1 truncate">{m.label}</div>
                      <div className="text-xl font-bold text-gray-900">{m.value}</div>
                      <div className="text-xs text-success font-medium">{m.trend}</div>
                    </div>
                  ))}
                </div>

                {/* Service list */}
                <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
                  {[
                    { name: "GKE Cluster (prod)", region: "us-central1", status: "healthy", cpu: 42 },
                    { name: "Cloud SQL PostgreSQL", region: "us-east1", status: "healthy", cpu: 28 },
                    { name: "Redis (Memorystore)", region: "us-central1", status: "healthy", cpu: 15 },
                    { name: "Cloud Run API Gateway", region: "global", status: "healthy", cpu: 67 },
                  ].map((svc, i) => (
                    <div
                      key={svc.name}
                      className={`flex items-center justify-between px-4 py-3 ${
                        i < 3 ? "border-b border-gray-50" : ""
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <div className="w-2 h-2 rounded-full bg-success" />
                        <div>
                          <div className="text-xs font-semibold text-gray-800">{svc.name}</div>
                          <div className="text-xs text-gray-400">{svc.region}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-20 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary-500 rounded-full"
                            style={{ width: `${svc.cpu}%` }}
                          />
                        </div>
                        <div className="text-xs text-gray-500 w-8 text-right">{svc.cpu}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats bar */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6">
          {STATS.map(({ value, suffix, label, icon: Icon }) => (
            <div
              key={label}
              className="flex items-center gap-5 bg-white rounded-2xl border border-gray-100 shadow-card px-6 py-5"
            >
              <div className="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center flex-shrink-0">
                <Icon className="w-6 h-6 text-primary-500" />
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">
                  <AnimatedCounter value={value} suffix={suffix} />
                </div>
                <div className="text-sm text-gray-500 font-medium">{label}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>

    {demoOpen && <DemoModal onClose={() => setDemoOpen(false)} />}
    </>
  );
}
