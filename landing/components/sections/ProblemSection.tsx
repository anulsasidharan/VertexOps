import { Bell, Cloud, DollarSign } from "lucide-react";
import { AnimateOnScroll } from "../ui/AnimateOnScroll";

const PROBLEMS = [
  {
    icon: Bell,
    color: "text-error",
    bg: "bg-red-50",
    title: "Alert Fatigue",
    description:
      "Engineering teams drown in thousands of low-quality alerts daily. Without AI triage, every on-call rotation burns out your best engineers — and critical incidents get lost in the noise.",
    stat: "73% of engineers report alert fatigue",
  },
  {
    icon: Cloud,
    color: "text-warning",
    bg: "bg-amber-50",
    title: "Multi-Cloud Chaos",
    description:
      "Managing GCP, AWS, and Azure with separate consoles, incompatible APIs, and siloed dashboards creates blind spots, slows incident response, and fragments your operational knowledge.",
    stat: "Average team uses 3.2 cloud providers",
  },
  {
    icon: DollarSign,
    color: "text-primary-500",
    bg: "bg-primary-50",
    title: "Cost Overruns",
    description:
      "Cloud spend grows 30% faster than revenue at most companies. Idle resources, oversized instances, and reserved capacity mismatches drain budgets without anyone noticing until the bill arrives.",
    stat: "32% of cloud spend is wasted",
  },
];

export function ProblemSection() {
  return (
    <section className="section-padding bg-gray-50">
      <div className="container-max">
        <AnimateOnScroll className="text-center mb-16">
          <div className="section-label">
            <span className="w-1.5 h-1.5 rounded-full bg-error" />
            The Problem
          </div>
          <h2 className="section-heading mb-4">
            Infrastructure Complexity Is{" "}
            <span className="gradient-text">Overwhelming Your Team</span>
          </h2>
          <p className="section-subheading mx-auto">
            Modern infrastructure is too complex for legacy monitoring tools.
            The result: slower deployments, reactive operations, and ballooning costs.
          </p>
        </AnimateOnScroll>

        <div className="grid md:grid-cols-3 gap-8 stagger-children">
          {PROBLEMS.map(({ icon: Icon, color, bg, title, description, stat }) => (
            <AnimateOnScroll key={title} className="card-base p-8 group">
              <div
                className={`w-12 h-12 rounded-xl ${bg} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}
              >
                <Icon className={`w-6 h-6 ${color}`} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">{title}</h3>
              <p className="text-gray-500 leading-relaxed mb-5">{description}</p>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-error" />
                <span className="text-xs font-semibold text-gray-600">{stat}</span>
              </div>
            </AnimateOnScroll>
          ))}
        </div>
      </div>
    </section>
  );
}
