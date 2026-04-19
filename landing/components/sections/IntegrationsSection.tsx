import { ArrowRight } from "lucide-react";
import { AnimateOnScroll } from "../ui/AnimateOnScroll";

const INTEGRATION_CATEGORIES = [
  {
    label: "Cloud Providers",
    color: "bg-blue-50 text-blue-700 border-blue-100",
    items: ["Google Cloud", "AWS", "Microsoft Azure"],
  },
  {
    label: "Monitoring",
    color: "bg-purple-50 text-purple-700 border-purple-100",
    items: ["Prometheus", "Grafana", "Datadog", "New Relic", "Splunk"],
  },
  {
    label: "Communication",
    color: "bg-green-50 text-green-700 border-green-100",
    items: ["Slack", "Microsoft Teams", "PagerDuty", "Opsgenie"],
  },
  {
    label: "Infrastructure as Code",
    color: "bg-orange-50 text-orange-700 border-orange-100",
    items: ["Terraform", "Pulumi", "CloudFormation", "Ansible"],
  },
  {
    label: "CI/CD",
    color: "bg-teal-50 text-teal-700 border-teal-100",
    items: ["GitHub Actions", "GitLab CI", "Jenkins", "CircleCI"],
  },
  {
    label: "Ticketing",
    color: "bg-indigo-50 text-indigo-700 border-indigo-100",
    items: ["Jira", "ServiceNow", "Linear"],
  },
];

export function IntegrationsSection() {
  return (
    <section id="integrations" className="section-padding bg-gray-50">
      <div className="container-max">
        <AnimateOnScroll className="text-center mb-16">
          <div className="section-label">
            <span className="w-1.5 h-1.5 rounded-full bg-secondary-500" />
            Integrations
          </div>
          <h2 className="section-heading mb-4">
            Integrates with Your{" "}
            <span className="gradient-text">Existing Stack</span>
          </h2>
          <p className="section-subheading mx-auto">
            VertexOps connects to the tools your team already uses.
            No ripping and replacing — just intelligence layered on top.
          </p>
        </AnimateOnScroll>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {INTEGRATION_CATEGORIES.map(({ label, color, items }, i) => (
            <AnimateOnScroll key={label} delay={i * 60} className="card-base p-6">
              <div className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold border mb-4 ${color}`}>
                {label}
              </div>
              <div className="flex flex-wrap gap-2">
                {items.map((item) => (
                  <div
                    key={item}
                    className="flex items-center gap-2 px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg cursor-default transition-colors group"
                  >
                    {/* Placeholder icon */}
                    <div className="w-5 h-5 rounded bg-gray-200 group-hover:bg-primary-100 flex items-center justify-center transition-colors">
                      <span className="text-[8px] font-bold text-gray-500 group-hover:text-primary-600">
                        {item[0]}
                      </span>
                    </div>
                    <span className="text-sm font-medium text-gray-700">{item}</span>
                  </div>
                ))}
              </div>
            </AnimateOnScroll>
          ))}
        </div>

        <AnimateOnScroll className="text-center">
          <p className="text-sm text-gray-500 mb-4">
            30+ integrations available. REST API and webhooks for custom connections.
          </p>
          <a href="#api" className="btn-secondary inline-flex items-center gap-2">
            View All Integrations
            <ArrowRight className="w-4 h-4" />
          </a>
        </AnimateOnScroll>
      </div>
    </section>
  );
}
