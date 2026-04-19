import { ArrowRight, CheckCircle2 } from "lucide-react";
import { AnimateOnScroll } from "../ui/AnimateOnScroll";

export function FinalCTASection() {
  return (
    <section className="section-padding bg-gradient-to-br from-primary-600 via-primary-500 to-secondary-500 relative overflow-hidden">
      {/* Background pattern */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage: "radial-gradient(circle at 2px 2px, white 1px, transparent 0)",
          backgroundSize: "32px 32px",
        }}
      />
      <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />

      <div className="container-max relative">
        <AnimateOnScroll className="text-center max-w-3xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
            Transform Your Infrastructure Operations Today
          </h2>
          <p className="text-xl text-primary-100 mb-10 leading-relaxed">
            Join hundreds of engineering teams reducing MTTR by 67% and cutting
            infrastructure costs by 40% with AI-powered DevOps intelligence.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <a
              href="#pricing"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-primary-600 font-bold rounded-xl hover:bg-primary-50 transition-all duration-200 text-base shadow-lg hover:shadow-xl"
            >
              Request Demo
              <ArrowRight className="w-5 h-5" />
            </a>
            <a
              href="#pricing"
              className="btn-outline px-8 py-4 text-base"
            >
              Start Free Trial
            </a>
          </div>

          <div className="flex flex-wrap justify-center gap-x-6 gap-y-2">
            {[
              "No credit card required",
              "14-day free trial",
              "Setup in 5 minutes",
              "Cancel anytime",
            ].map((item) => (
              <div key={item} className="flex items-center gap-2 text-sm text-primary-100">
                <CheckCircle2 className="w-4 h-4 text-white/70 flex-shrink-0" />
                {item}
              </div>
            ))}
          </div>
        </AnimateOnScroll>
      </div>
    </section>
  );
}
