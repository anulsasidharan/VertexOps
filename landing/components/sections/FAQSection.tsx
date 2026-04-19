"use client";
import { useState } from "react";
import { Plus, Minus } from "lucide-react";
import { AnimateOnScroll } from "../ui/AnimateOnScroll";

const FAQS = [
  {
    q: "What cloud providers does VertexOps support?",
    a: "VertexOps natively supports Google Cloud Platform (GCP), Amazon Web Services (AWS), and Microsoft Azure. Starter plans support one provider; Professional and Enterprise cover all three simultaneously with unified dashboards.",
  },
  {
    q: "How long does setup take?",
    a: "Most teams are fully operational within 5 minutes. Connect your cloud accounts via OAuth or IAM role, and VertexOps automatically discovers your resources. First alerts typically fire within 3 minutes of connection.",
  },
  {
    q: "Do you offer a free trial?",
    a: "Yes! All plans start with a 14-day free trial, no credit card required. You get full access to the Professional feature set during the trial period so you can evaluate the complete platform.",
  },
  {
    q: "How does AI-powered incident response work?",
    a: "When an anomaly is detected, VertexOps correlates logs, metrics, and traces to identify the root cause. It then matches the incident pattern against historical runbooks and your knowledge base to propose a remediation. You can configure approval gates for automated fixes or review every action manually.",
  },
  {
    q: "Can VertexOps integrate with our existing monitoring tools?",
    a: "Absolutely. VertexOps integrates with Prometheus, Grafana, Datadog, New Relic, Splunk, and 30+ other tools. It adds AI intelligence on top of your existing observability stack — not a replacement.",
  },
  {
    q: "How does the AI ChatOps assistant work?",
    a: "ChatOps uses Retrieval-Augmented Generation (RAG) to answer questions about your infrastructure in natural language. It searches across your current metrics, logs, incident history, runbooks, and documentation to provide accurate, evidence-backed answers with cited sources.",
  },
  {
    q: "Is my infrastructure data secure?",
    a: "Yes. VertexOps is SOC 2 Type II certified and ISO 27001 compliant. All data is encrypted with AES-256 at rest and TLS 1.3 in transit. We support VPC isolation, private endpoints, and IP allowlisting. For compliance-sensitive deployments, on-premise options are available on the Enterprise tier.",
  },
  {
    q: "What's the difference between Professional and Enterprise?",
    a: "Professional supports up to 1,000 resources, 3 cloud accounts, and 90-day retention — ideal for most growing engineering teams. Enterprise adds unlimited resources, 2-year retention, multi-region deployments, on-premise options, HIPAA/PCI DSS compliance, dedicated support, and custom AI model fine-tuning.",
  },
  {
    q: "Can I cancel anytime?",
    a: "Yes. Monthly plans can be cancelled at any time with no penalty — your access continues until the end of the billing period. Annual plans are non-refundable but can be cancelled to prevent renewal.",
  },
  {
    q: "Do you offer on-premise deployment?",
    a: "On-premise deployment is available on the Enterprise tier. This includes a private cloud or air-gapped deployment with full data residency controls, self-hosted AI models, and dedicated infrastructure management.",
  },
  {
    q: "What kind of support do you provide?",
    a: "Starter includes community support via our forums and documentation. Professional adds priority email support with a 4-hour response SLA. Enterprise includes a dedicated Customer Success Manager, 24/7 phone support, and white-glove onboarding.",
  },
  {
    q: "Do you have an API?",
    a: "Yes. VertexOps exposes a fully documented REST API with OpenAPI/Swagger spec, a Python SDK (vertexops-python on PyPI), a CLI tool (vertexops-cli), and real-time webhooks. All plans have API access.",
  },
];

export function FAQSection() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section id="faq" className="section-padding bg-white">
      <div className="container-max max-w-4xl">
        <AnimateOnScroll className="text-center mb-14">
          <div className="section-label">
            <span className="w-1.5 h-1.5 rounded-full bg-primary-500" />
            FAQ
          </div>
          <h2 className="section-heading mb-4">
            Frequently Asked{" "}
            <span className="gradient-text">Questions</span>
          </h2>
        </AnimateOnScroll>

        <AnimateOnScroll>
          <div className="space-y-2">
            {FAQS.map(({ q, a }, i) => (
              <div
                key={q}
                className={`border rounded-2xl overflow-hidden transition-all duration-200 ${
                  open === i ? "border-primary-200 bg-primary-50/30" : "border-gray-100 bg-white hover:border-gray-200"
                }`}
              >
                <button
                  className="w-full flex items-center justify-between px-6 py-5 text-left gap-4"
                  onClick={() => setOpen(open === i ? null : i)}
                >
                  <span className="text-base font-semibold text-gray-900 leading-snug">{q}</span>
                  <div
                    className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 transition-colors ${
                      open === i ? "bg-primary-500 text-white" : "bg-gray-100 text-gray-500"
                    }`}
                  >
                    {open === i ? <Minus className="w-3.5 h-3.5" /> : <Plus className="w-3.5 h-3.5" />}
                  </div>
                </button>
                {open === i && (
                  <div className="px-6 pb-5">
                    <p className="text-sm text-gray-600 leading-relaxed">{a}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </AnimateOnScroll>

        <AnimateOnScroll className="mt-10 text-center">
          <p className="text-sm text-gray-500">
            Still have questions?{" "}
            <a href="#" className="text-primary-500 font-semibold hover:underline">
              Talk to our team →
            </a>
          </p>
        </AnimateOnScroll>
      </div>
    </section>
  );
}
