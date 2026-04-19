import { Star, Quote } from "lucide-react";
import { AnimateOnScroll } from "../ui/AnimateOnScroll";

const TESTIMONIALS = [
  {
    quote:
      "VertexOps transformed our on-call experience. We went from drowning in alerts to having our AI resolve incidents before we even wake up. Our MTTR dropped from 4 hours to 12 minutes.",
    name: "Sarah Chen",
    title: "Principal SRE",
    company: "TechScale Inc.",
    metric: "MTTR: 4h → 12min",
    rating: 5,
    initials: "SC",
    color: "bg-primary-500",
  },
  {
    quote:
      "The FinOps intelligence alone paid for three years of the subscription in the first month. We had $47K/month in idle resources we didn't even know about. VertexOps found them all.",
    name: "Marcus Williams",
    title: "Head of Platform Engineering",
    company: "CloudFirst Corp",
    metric: "$47K/month saved",
    rating: 5,
    initials: "MW",
    color: "bg-secondary-500",
  },
  {
    quote:
      "Our SOC 2 audit prep went from a 6-week all-hands scramble to a 3-day documentation exercise. VertexOps gave us continuous compliance instead of annual panic.",
    name: "Priya Nair",
    title: "VP Engineering",
    company: "FinSec Ltd.",
    metric: "Audit prep: 6 wks → 3 days",
    rating: 5,
    initials: "PN",
    color: "bg-success",
  },
];

export function TestimonialsSection() {
  return (
    <section id="testimonials" className="section-padding bg-gray-50">
      <div className="container-max">
        <AnimateOnScroll className="text-center mb-16">
          <div className="section-label">
            <span className="w-1.5 h-1.5 rounded-full bg-warning" />
            Testimonials
          </div>
          <h2 className="section-heading mb-4">
            Loved by DevOps Teams{" "}
            <span className="gradient-text">Worldwide</span>
          </h2>
          <p className="section-subheading mx-auto">
            Join 200+ engineering teams who&apos;ve transformed their infrastructure operations.
          </p>
        </AnimateOnScroll>

        <div className="grid md:grid-cols-3 gap-8">
          {TESTIMONIALS.map(({ quote, name, title, company, metric, rating, initials, color }, i) => (
            <AnimateOnScroll key={name} delay={i * 100} className="card-base p-8 flex flex-col">
              {/* Stars */}
              <div className="flex gap-1 mb-4">
                {Array.from({ length: rating }).map((_, si) => (
                  <Star key={si} className="w-4 h-4 text-warning fill-warning" />
                ))}
              </div>

              {/* Quote icon */}
              <Quote className="w-8 h-8 text-gray-200 mb-3 flex-shrink-0" />

              <p className="text-gray-600 leading-relaxed mb-6 flex-1 text-sm">
                &ldquo;{quote}&rdquo;
              </p>

              {/* Metric badge */}
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-success/10 rounded-full mb-6 w-fit">
                <div className="w-1.5 h-1.5 rounded-full bg-success" />
                <span className="text-xs font-bold text-success">{metric}</span>
              </div>

              {/* Author */}
              <div className="flex items-center gap-3 pt-4 border-t border-gray-100">
                <div
                  className={`w-10 h-10 rounded-full ${color} flex items-center justify-center flex-shrink-0`}
                >
                  <span className="text-sm font-bold text-white">{initials}</span>
                </div>
                <div>
                  <div className="text-sm font-bold text-gray-900">{name}</div>
                  <div className="text-xs text-gray-500">
                    {title} · {company}
                  </div>
                </div>
              </div>
            </AnimateOnScroll>
          ))}
        </div>
      </div>
    </section>
  );
}
