import { AnimateOnScroll } from "../ui/AnimateOnScroll";

const LOGOS = [
  { name: "Google Cloud", abbr: "GCP" },
  { name: "Amazon Web Services", abbr: "AWS" },
  { name: "Microsoft Azure", abbr: "Azure" },
  { name: "Terraform", abbr: "TF" },
  { name: "Kubernetes", abbr: "K8s" },
  { name: "PagerDuty", abbr: "PD" },
  { name: "Datadog", abbr: "DD" },
  { name: "Slack", abbr: "Slack" },
];

export function LogoCloud() {
  return (
    <section className="py-14 border-y border-gray-100 bg-white">
      <div className="max-w-7xl mx-auto px-6">
        <AnimateOnScroll>
          <p className="text-center text-sm font-medium text-gray-400 uppercase tracking-widest mb-10">
            Trusted by 200+ engineering teams and integrates with your stack
          </p>
        </AnimateOnScroll>
        <AnimateOnScroll>
          <div className="flex flex-wrap justify-center items-center gap-x-12 gap-y-6">
            {LOGOS.map(({ name, abbr }) => (
              <div
                key={name}
                className="flex items-center gap-2 text-gray-300 hover:text-gray-500 transition-colors cursor-default group"
                title={name}
              >
                {/* Abstract logo placeholder — replace with real SVG logos */}
                <div className="w-7 h-7 rounded-md bg-gray-100 group-hover:bg-primary-50 flex items-center justify-center transition-colors">
                  <span className="text-[9px] font-bold text-gray-400 group-hover:text-primary-500">
                    {abbr.slice(0, 2)}
                  </span>
                </div>
                <span className="text-sm font-semibold hidden sm:block">{name}</span>
              </div>
            ))}
          </div>
        </AnimateOnScroll>
      </div>
    </section>
  );
}
