import { Shield, Lock, Eye, FileCheck } from "lucide-react";
import { AnimateOnScroll } from "../ui/AnimateOnScroll";

const BADGES = [
  { label: "SOC 2 Type II", sub: "Certified", color: "border-blue-200 bg-blue-50 text-blue-700" },
  { label: "ISO 27001", sub: "Compliant", color: "border-green-200 bg-green-50 text-green-700" },
  { label: "GDPR", sub: "Ready", color: "border-purple-200 bg-purple-50 text-purple-700" },
  { label: "HIPAA", sub: "Compliant", color: "border-red-200 bg-red-50 text-red-700" },
  { label: "GCP Partner", sub: "Technology", color: "border-orange-200 bg-orange-50 text-orange-700" },
  { label: "AWS Advanced", sub: "Technology Partner", color: "border-yellow-200 bg-yellow-50 text-yellow-700" },
];

const SECURITY_FEATURES = [
  {
    icon: Lock,
    title: "Encryption Everywhere",
    description: "AES-256 encryption at rest and TLS 1.3 in transit. All secrets stored in GCP Secret Manager.",
  },
  {
    icon: Shield,
    title: "Network Isolation",
    description: "VPC isolation, private service endpoints, IP allowlisting, and zero-trust network architecture.",
  },
  {
    icon: Eye,
    title: "Comprehensive Audit Logs",
    description: "Every AI agent action and infrastructure change is logged with tamper-proof, append-only audit trails.",
  },
  {
    icon: FileCheck,
    title: "Access Control",
    description: "RBAC, SSO (Google, Okta, Azure AD), MFA, and service account management with least-privilege defaults.",
  },
];

export function SecuritySection() {
  return (
    <section id="security" className="section-padding bg-white">
      <div className="container-max">
        <AnimateOnScroll className="text-center mb-16">
          <div className="section-label">
            <span className="w-1.5 h-1.5 rounded-full bg-success" />
            Security & Compliance
          </div>
          <h2 className="section-heading mb-4">
            Security and Compliance{" "}
            <span className="gradient-text">Built In</span>
          </h2>
          <p className="section-subheading mx-auto">
            VertexOps is built security-first, not security-bolted-on.
            Enterprise controls, continuous compliance, and full auditability — by design.
          </p>
        </AnimateOnScroll>

        {/* Compliance badges */}
        <AnimateOnScroll>
          <div className="flex flex-wrap justify-center gap-4 mb-16">
            {BADGES.map(({ label, sub, color }) => (
              <div
                key={label}
                className={`flex flex-col items-center px-6 py-4 rounded-2xl border-2 ${color} min-w-[120px]`}
              >
                <Shield className="w-7 h-7 mb-2 opacity-70" />
                <div className="text-sm font-bold leading-tight text-center">{label}</div>
                <div className="text-xs opacity-70 text-center">{sub}</div>
              </div>
            ))}
          </div>
        </AnimateOnScroll>

        {/* Security features */}
        <div className="grid md:grid-cols-2 gap-8">
          {SECURITY_FEATURES.map(({ icon: Icon, title, description }, i) => (
            <AnimateOnScroll key={title} delay={i * 80} className="card-base p-7 flex gap-5">
              <div className="w-11 h-11 rounded-xl bg-success/10 flex items-center justify-center flex-shrink-0">
                <Icon className="w-5 h-5 text-success" />
              </div>
              <div>
                <h4 className="text-base font-bold text-gray-900 mb-2">{title}</h4>
                <p className="text-sm text-gray-500 leading-relaxed">{description}</p>
              </div>
            </AnimateOnScroll>
          ))}
        </div>

        <AnimateOnScroll className="mt-10 text-center">
          <a
            href="#"
            className="btn-secondary inline-flex items-center gap-2 text-sm"
          >
            <Shield className="w-4 h-4" />
            View Security Documentation
          </a>
        </AnimateOnScroll>
      </div>
    </section>
  );
}
