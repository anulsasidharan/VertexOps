"use client";
import { useState } from "react";
import { Check, Zap, Building2, Star } from "lucide-react";
import { AnimateOnScroll } from "../ui/AnimateOnScroll";

const PLANS = [
  {
    name: "Starter",
    icon: Zap,
    price: { monthly: 499, annual: 399 },
    description: "For small teams taking their first steps in AI ops.",
    limit: "Up to 100 resources",
    cta: "Start Free Trial",
    popular: false,
    features: [
      "100 monitored resources",
      "GCP, AWS, or Azure (pick 1)",
      "30-day data retention",
      "Slack + email alerts",
      "Basic AI incident triage",
      "Python SDK access",
      "Community support",
      "SOC 2 compliant",
    ],
  },
  {
    name: "Professional",
    icon: Star,
    price: { monthly: 1999, annual: 1599 },
    description: "The full platform for growing engineering teams.",
    limit: "Up to 1,000 resources",
    cta: "Request Demo",
    popular: true,
    features: [
      "1,000 monitored resources",
      "All cloud providers",
      "90-day data retention",
      "All integrations (30+)",
      "Advanced AI ChatOps",
      "Cost optimization AI",
      "Automated remediation",
      "Priority support (4h SLA)",
      "MLflow experiment tracking",
      "RBAC + SSO",
    ],
  },
  {
    name: "Enterprise",
    icon: Building2,
    price: { monthly: null, annual: null },
    description: "Custom scale, compliance, and support for large orgs.",
    limit: "Unlimited resources",
    cta: "Contact Sales",
    popular: false,
    features: [
      "Unlimited resources",
      "2-year data retention",
      "Multi-region deployments",
      "On-premise option",
      "Custom integrations",
      "Dedicated CSM",
      "White-glove onboarding",
      "99.95% SLA",
      "HIPAA / PCI DSS",
      "Custom AI model fine-tuning",
    ],
  },
];

export function PricingSection() {
  const [annual, setAnnual] = useState(false);

  return (
    <section id="pricing" className="section-padding bg-gray-50">
      <div className="container-max">
        <AnimateOnScroll className="text-center mb-14">
          <div className="section-label">
            <span className="w-1.5 h-1.5 rounded-full bg-primary-500" />
            Pricing
          </div>
          <h2 className="section-heading mb-4">
            Transparent Pricing for{" "}
            <span className="gradient-text">Teams of All Sizes</span>
          </h2>
          <p className="section-subheading mx-auto mb-8">
            Start with a 14-day free trial. No credit card required.
          </p>

          {/* Toggle */}
          <div className="inline-flex items-center gap-3 p-1 bg-white border border-gray-200 rounded-xl">
            <button
              onClick={() => setAnnual(false)}
              className={`px-5 py-2 rounded-lg text-sm font-semibold transition-all ${
                !annual ? "bg-primary-500 text-white" : "text-gray-500 hover:text-gray-700"
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setAnnual(true)}
              className={`px-5 py-2 rounded-lg text-sm font-semibold transition-all ${
                annual ? "bg-primary-500 text-white" : "text-gray-500 hover:text-gray-700"
              }`}
            >
              Annual
              <span className="ml-2 text-xs font-bold text-success bg-green-50 px-2 py-0.5 rounded-full">
                Save 20%
              </span>
            </button>
          </div>
        </AnimateOnScroll>

        <div className="grid md:grid-cols-3 gap-8">
          {PLANS.map(({ name, icon: Icon, price, description, limit, cta, popular, features }, i) => (
            <AnimateOnScroll key={name} delay={i * 100}>
              <div
                className={`relative flex flex-col h-full rounded-2xl border p-8 transition-all duration-300 ${
                  popular
                    ? "bg-primary-500 border-primary-500 text-white shadow-glow scale-[1.02]"
                    : "bg-white border-gray-200 hover:border-primary-200 hover:shadow-card-hover"
                }`}
              >
                {popular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1 bg-warning text-gray-900 text-xs font-bold rounded-full uppercase tracking-wide whitespace-nowrap">
                    Most Popular
                  </div>
                )}

                <div className={`w-11 h-11 rounded-xl flex items-center justify-center mb-5 ${popular ? "bg-white/20" : "bg-primary-50"}`}>
                  <Icon className={`w-5 h-5 ${popular ? "text-white" : "text-primary-500"}`} />
                </div>

                <h3 className={`text-xl font-bold mb-1 ${popular ? "text-white" : "text-gray-900"}`}>
                  {name}
                </h3>
                <p className={`text-sm mb-6 ${popular ? "text-primary-100" : "text-gray-500"}`}>
                  {description}
                </p>

                <div className="mb-6">
                  {price.monthly ? (
                    <>
                      <span className={`text-4xl font-bold ${popular ? "text-white" : "text-gray-900"}`}>
                        ${annual ? price.annual : price.monthly}
                      </span>
                      <span className={`text-sm font-medium ml-1 ${popular ? "text-primary-200" : "text-gray-400"}`}>
                        /month
                      </span>
                      {annual && (
                        <div className={`text-xs mt-1 ${popular ? "text-primary-200" : "text-gray-400"}`}>
                          Billed annually (${annual ? (price.annual! * 12).toLocaleString() : 0}/yr)
                        </div>
                      )}
                    </>
                  ) : (
                    <span className={`text-3xl font-bold ${popular ? "text-white" : "text-gray-900"}`}>
                      Custom
                    </span>
                  )}
                </div>

                <div className={`text-xs font-semibold uppercase tracking-wide mb-5 ${popular ? "text-primary-200" : "text-gray-400"}`}>
                  {limit}
                </div>

                <a
                  href="#"
                  className={`block text-center py-3 px-6 rounded-xl text-sm font-bold mb-8 transition-all duration-200 ${
                    popular
                      ? "bg-white text-primary-600 hover:bg-primary-50"
                      : "btn-primary"
                  }`}
                >
                  {cta}
                </a>

                <ul className="space-y-3 flex-1">
                  {features.map((f) => (
                    <li key={f} className="flex items-start gap-3">
                      <Check
                        className={`w-4 h-4 flex-shrink-0 mt-0.5 ${popular ? "text-primary-200" : "text-success"}`}
                      />
                      <span className={`text-sm ${popular ? "text-primary-100" : "text-gray-600"}`}>
                        {f}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </AnimateOnScroll>
          ))}
        </div>

        <AnimateOnScroll className="mt-10 text-center">
          <p className="text-sm text-gray-500">
            All plans include a 14-day free trial · No credit card required · Cancel anytime
          </p>
        </AnimateOnScroll>
      </div>
    </section>
  );
}
