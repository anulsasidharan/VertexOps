import { Link2, Search, Activity, Sparkles, ArrowRight } from "lucide-react";
import { AnimateOnScroll } from "../ui/AnimateOnScroll";

const STEPS = [
  {
    step: "01",
    icon: Link2,
    title: "Connect",
    time: "5 minutes",
    description:
      "Connect your GCP, AWS, or Azure accounts with a single OAuth flow. No agents, no infrastructure changes, no downtime.",
    detail: "Supports service accounts, IAM roles, and workload identity federation.",
  },
  {
    step: "02",
    icon: Search,
    title: "Discover",
    time: "Automated",
    description:
      "VertexOps automatically discovers and maps all your resources, relationships, and dependencies across every region and account.",
    detail: "847 resource types supported across all three major clouds.",
  },
  {
    step: "03",
    icon: Activity,
    title: "Monitor",
    time: "Immediate",
    description:
      "Real-time insights, AI-powered anomaly detection, and intelligent alerting start working the moment discovery completes.",
    detail: "First alert typically fires within 3 minutes of connection.",
  },
  {
    step: "04",
    icon: Sparkles,
    title: "Optimize",
    time: "Ongoing",
    description:
      "Automated remediation handles routine incidents. AI recommendations continuously improve your cost efficiency and reliability posture.",
    detail: "Average team saves $47K/month and resolves 23 incidents automatically per day.",
  },
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="section-padding bg-gray-50">
      <div className="container-max">
        <AnimateOnScroll className="text-center mb-16">
          <div className="section-label">
            <span className="w-1.5 h-1.5 rounded-full bg-secondary-500" />
            How It Works
          </div>
          <h2 className="section-heading mb-4">
            Get Started in{" "}
            <span className="gradient-text">Minutes, Not Weeks</span>
          </h2>
          <p className="section-subheading mx-auto">
            No complex setup. No professional services engagement. VertexOps is
            delivering value in your first session.
          </p>
        </AnimateOnScroll>

        <div className="relative">
          {/* Connecting line */}
          <div className="hidden lg:block absolute top-16 left-[12.5%] right-[12.5%] h-0.5 bg-gradient-to-r from-primary-200 via-primary-400 to-primary-200" />

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {STEPS.map(({ step, icon: Icon, title, time, description, detail }, i) => (
              <AnimateOnScroll key={step} delay={i * 100}>
                <div className="relative">
                  {/* Step number bubble */}
                  <div className="flex justify-center lg:justify-start mb-6">
                    <div className="relative w-14 h-14 rounded-full bg-white border-2 border-primary-200 flex items-center justify-center shadow-sm z-10">
                      <Icon className="w-6 h-6 text-primary-500" />
                      <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-primary-500 flex items-center justify-center">
                        <span className="text-[10px] font-bold text-white">{step.replace("0", "")}</span>
                      </div>
                    </div>
                  </div>

                  <div className="card-base p-6 h-full">
                    <div className="flex items-center gap-2 mb-3">
                      <h3 className="text-lg font-bold text-gray-900">{title}</h3>
                      <span className="text-xs font-medium text-primary-500 bg-primary-50 px-2 py-0.5 rounded-full">
                        {time}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 leading-relaxed mb-3">{description}</p>
                    <p className="text-xs text-gray-400 italic">{detail}</p>
                  </div>
                </div>
              </AnimateOnScroll>
            ))}
          </div>
        </div>

        <AnimateOnScroll className="text-center mt-14">
          <a href="#pricing" className="btn-primary px-8 py-3.5 text-base">
            Start Free Trial
            <ArrowRight className="w-4 h-4" />
          </a>
          <p className="text-sm text-gray-400 mt-3">
            No credit card required · 14-day free trial
          </p>
        </AnimateOnScroll>
      </div>
    </section>
  );
}
