"use client";
import { useState } from "react";
import { Globe, TrendingDown, Terminal, Shield } from "lucide-react";
import { AnimateOnScroll } from "../ui/AnimateOnScroll";

const CASES = [
  {
    id: "multicloud",
    icon: Globe,
    label: "Multi-Cloud Ops",
    title: "Unified Multi-Cloud Operations",
    description:
      "Stop context-switching between GCP, AWS, and Azure consoles. VertexOps gives you a single pane of glass for all three clouds with standardized incident response and unified compliance reporting.",
    outcomes: [
      { metric: "67%", label: "Faster incident resolution" },
      { metric: "3×", label: "Fewer escalations" },
      { metric: "100%", label: "Resource visibility" },
    ],
    industries: ["E-commerce", "SaaS", "Media"],
    quote: "We went from managing 3 cloud consoles to a single interface in a day.",
  },
  {
    id: "finops",
    icon: TrendingDown,
    label: "FinOps Teams",
    title: "Continuous Cost Optimization",
    description:
      "Give your FinOps team AI-powered tools to identify waste, model commitment options, and allocate costs across teams — automatically, every day, without manual spreadsheet work.",
    outcomes: [
      { metric: "40%", label: "Infrastructure cost savings" },
      { metric: "$47K", label: "Avg monthly savings" },
      { metric: "100%", label: "Spend visibility" },
    ],
    industries: ["Financial Services", "Healthcare", "Retail"],
    quote: "VertexOps paid for itself in the first week of cost recommendations.",
  },
  {
    id: "platform",
    icon: Terminal,
    label: "Platform Engineering",
    title: "Platform Engineering Enablement",
    description:
      "Accelerate your internal platform with self-service infrastructure insights, automated runbook execution, and developer-friendly APIs. Reduce toil so your team can build features, not fight fires.",
    outcomes: [
      { metric: "95%", label: "Routine ops automated" },
      { metric: "4×", label: "Faster runbook execution" },
      { metric: "0", label: "Toil tickets per week" },
    ],
    industries: ["Tech Companies", "SaaS", "Fintech"],
    quote: "Our on-call load dropped from 40 hours/week to under 5.",
  },
  {
    id: "compliance",
    icon: Shield,
    label: "Security & Compliance",
    title: "Automated Compliance & Security",
    description:
      "Stay continuously compliant across SOC 2, HIPAA, and GDPR without dedicated audit sprints. AI-powered posture assessment, IaC drift detection, and automated evidence collection.",
    outcomes: [
      { metric: "98%", label: "SOC 2 control passing" },
      { metric: "10×", label: "Faster audit prep" },
      { metric: "0", label: "Compliance findings" },
    ],
    industries: ["Healthcare", "Financial Services", "Gov"],
    quote: "Our SOC 2 audit went from 6 weeks to 3 days of prep.",
  },
];

export function UseCasesSection() {
  const [active, setActive] = useState(CASES[0].id);
  const current = CASES.find((c) => c.id === active)!;
  const Icon = current.icon;

  return (
    <section id="use-cases" className="section-padding bg-white">
      <div className="container-max">
        <AnimateOnScroll className="text-center mb-14">
          <div className="section-label">
            <span className="w-1.5 h-1.5 rounded-full bg-primary-500" />
            Use Cases
          </div>
          <h2 className="section-heading mb-4">
            Built for Modern{" "}
            <span className="gradient-text">Infrastructure Teams</span>
          </h2>
        </AnimateOnScroll>

        {/* Tab row */}
        <AnimateOnScroll>
          <div className="flex flex-wrap justify-center gap-2 mb-14">
            {CASES.map(({ id, label, icon: TabIcon }) => (
              <button
                key={id}
                onClick={() => setActive(id)}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 ${
                  active === id
                    ? "bg-primary-500 text-white shadow-sm"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                <TabIcon className="w-4 h-4" />
                {label}
              </button>
            ))}
          </div>
        </AnimateOnScroll>

        {/* Content */}
        <AnimateOnScroll key={active}>
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center mb-6">
                <Icon className="w-6 h-6 text-primary-500" />
              </div>
              <h3 className="text-3xl font-bold text-gray-900 mb-4 leading-tight">
                {current.title}
              </h3>
              <p className="text-gray-500 leading-relaxed mb-8">{current.description}</p>

              {/* Quote */}
              <blockquote className="border-l-4 border-primary-200 pl-5 mb-8">
                <p className="text-gray-600 italic text-base">&ldquo;{current.quote}&rdquo;</p>
              </blockquote>

              {/* Industries */}
              <div className="flex flex-wrap gap-2">
                <span className="text-xs font-medium text-gray-400">Popular in:</span>
                {current.industries.map((ind) => (
                  <span
                    key={ind}
                    className="text-xs font-semibold text-primary-600 bg-primary-50 px-2.5 py-1 rounded-full"
                  >
                    {ind}
                  </span>
                ))}
              </div>
            </div>

            {/* Outcome cards */}
            <div className="grid grid-cols-1 gap-4">
              {current.outcomes.map(({ metric, label }) => (
                <div
                  key={label}
                  className="card-base px-7 py-5 flex items-center gap-5"
                >
                  <div className="text-4xl font-bold gradient-text w-24 flex-shrink-0">
                    {metric}
                  </div>
                  <div className="text-base font-medium text-gray-600">{label}</div>
                </div>
              ))}
            </div>
          </div>
        </AnimateOnScroll>
      </div>
    </section>
  );
}
