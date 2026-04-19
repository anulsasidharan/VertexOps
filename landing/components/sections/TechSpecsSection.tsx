import { CheckCircle2, ArrowRight } from "lucide-react";
import { AnimateOnScroll } from "../ui/AnimateOnScroll";

const SPECS = [
  { label: "API Latency", value: "<200ms", note: "average response time" },
  { label: "Uptime SLA", value: "99.95%", note: "guaranteed availability" },
  { label: "Alert Latency", value: "<5 sec", note: "real-time processing" },
  { label: "Resources Supported", value: "10,000+", note: "per deployment" },
  { label: "Data Retention", value: "2 years", note: "enterprise tier" },
  { label: "AI Response", value: "<3 sec", note: "ChatOps queries" },
];

const HIGHLIGHTS = [
  "Microservices on GKE — horizontally scalable",
  "Event-driven Celery task queues",
  "LangGraph orchestration + GPT-4o & Gemini",
  "Pinecone / Vertex AI Vector Search",
  "WebSocket support for live dashboard updates",
  "API-first design — REST OpenAPI with full SDK",
  "AES-256 encryption at rest, TLS 1.3 in transit",
  "Multi-region deployments available (Enterprise)",
];

export function TechSpecsSection() {
  return (
    <section id="tech-specs" className="section-padding bg-white">
      <div className="container-max">
        <AnimateOnScroll className="text-center mb-16">
          <div className="section-label">
            <span className="w-1.5 h-1.5 rounded-full bg-primary-500" />
            Architecture
          </div>
          <h2 className="section-heading mb-4">
            Enterprise-Grade{" "}
            <span className="gradient-text">Architecture</span>
          </h2>
          <p className="section-subheading mx-auto">
            Built on battle-tested cloud-native patterns. Every component is
            designed for the reliability requirements of mission-critical infrastructure.
          </p>
        </AnimateOnScroll>

        <div className="grid lg:grid-cols-2 gap-16 items-start">
          {/* Architecture diagram (ASCII/SVG mockup) */}
          <AnimateOnScroll direction="left">
            <div className="bg-gray-900 rounded-2xl p-6 font-mono text-xs text-gray-300 leading-loose">
              <div className="text-primary-400 font-bold mb-4">// VertexOps Architecture</div>
              <pre className="text-gray-400 overflow-x-auto">{`┌─────────────────────────────────┐
│     API Client / Dashboard      │
└──────────────┬──────────────────┘
               │ HTTPS / WSS
┌──────────────▼──────────────────┐
│   FastAPI Gateway (Cloud Run)   │
│   JWT + API Key Auth  │  RBAC   │
└────┬─────────┬────────┬─────────┘
     │         │        │
┌────▼──┐  ┌──▼───┐ ┌──▼─────┐
│Ingest │  │Query │ │Metrics │
│Service│  │ RAG  │ │  /OTel │
└───┬───┘  └──┬───┘ └────────┘
    │          │
┌───▼──────────▼───────────────┐
│  Celery Workers (GKE)        │
│  embed · chunk · eval · scan │
└──────────┬───────────────────┘
           │
┌──────────▼───────────────────┐
│  AI Pipeline (LangGraph)     │
│  GPT-4o · Gemini · Pinecone  │
└──────────────────────────────┘
┌───────────────────────────────┐
│  PostgreSQL (Cloud SQL)       │
│  Redis (Memorystore)  │  GCS  │
└───────────────────────────────┘`}</pre>
            </div>
          </AnimateOnScroll>

          {/* Specs & highlights */}
          <AnimateOnScroll direction="right">
            {/* Performance specs */}
            <div className="grid grid-cols-2 gap-4 mb-8">
              {SPECS.map(({ label, value, note }) => (
                <div key={label} className="card-base p-4">
                  <div className="text-2xl font-bold text-primary-500 mb-1">{value}</div>
                  <div className="text-sm font-semibold text-gray-700 mb-0.5">{label}</div>
                  <div className="text-xs text-gray-400">{note}</div>
                </div>
              ))}
            </div>

            {/* Feature highlights */}
            <div className="space-y-3">
              {HIGHLIGHTS.map((h) => (
                <div key={h} className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-gray-600">{h}</span>
                </div>
              ))}
            </div>

            <a href="#api" className="btn-secondary mt-8 inline-flex items-center gap-2">
              Read Technical Docs
              <ArrowRight className="w-4 h-4" />
            </a>
          </AnimateOnScroll>
        </div>
      </div>
    </section>
  );
}
