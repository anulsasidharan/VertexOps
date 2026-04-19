import { Terminal, Book, Package, Webhook, ArrowRight } from "lucide-react";
import { AnimateOnScroll } from "../ui/AnimateOnScroll";

const CODE_EXAMPLE = `<span class="token-keyword">from</span> <span class="token-plain">vertexops</span> <span class="token-keyword">import</span> <span class="token-plain">Client</span>

<span class="token-comment"># Initialize client</span>
<span class="token-var">client</span> <span class="token-punct">=</span> <span class="token-fn">Client</span><span class="token-punct">(</span><span class="token-var">api_key</span><span class="token-punct">=</span><span class="token-string">"vops_sk_..."</span><span class="token-punct">)</span>

<span class="token-comment"># Get infrastructure health</span>
<span class="token-var">health</span> <span class="token-punct">=</span> <span class="token-var">client</span><span class="token-punct">.</span><span class="token-fn">infrastructure</span><span class="token-punct">.</span><span class="token-fn">get_health</span><span class="token-punct">(</span><span class="token-punct">)</span>
<span class="token-fn">print</span><span class="token-punct">(</span><span class="token-var">health</span><span class="token-punct">.</span><span class="token-var">status</span><span class="token-punct">)</span>  <span class="token-comment"># "healthy"</span>

<span class="token-comment"># Natural language query</span>
<span class="token-var">response</span> <span class="token-punct">=</span> <span class="token-var">client</span><span class="token-punct">.</span><span class="token-fn">chatops</span><span class="token-punct">.</span><span class="token-fn">query</span><span class="token-punct">(</span>
    <span class="token-string">"Why is production GKE latency high?"</span>
<span class="token-punct">)</span>
<span class="token-fn">print</span><span class="token-punct">(</span><span class="token-var">response</span><span class="token-punct">.</span><span class="token-var">answer</span><span class="token-punct">)</span>
<span class="token-fn">print</span><span class="token-punct">(</span><span class="token-var">response</span><span class="token-punct">.</span><span class="token-var">sources</span><span class="token-punct">)</span>  <span class="token-comment"># cited evidence</span>

<span class="token-comment"># Trigger remediation</span>
<span class="token-var">job</span> <span class="token-punct">=</span> <span class="token-var">client</span><span class="token-punct">.</span><span class="token-fn">incidents</span><span class="token-punct">.</span><span class="token-fn">remediate</span><span class="token-punct">(</span>
    <span class="token-var">incident_id</span><span class="token-punct">=</span><span class="token-string">"inc_8fKd92"</span><span class="token-punct">,</span>
    <span class="token-var">auto_approve</span><span class="token-punct">=</span><span class="token-keyword">False</span>  <span class="token-comment"># require human approval</span>
<span class="token-punct">)</span>
<span class="token-fn">print</span><span class="token-punct">(</span><span class="token-var">job</span><span class="token-punct">.</span><span class="token-var">status</span><span class="token-punct">)</span>  <span class="token-comment"># "awaiting_approval"</span>`;

const FEATURES = [
  { icon: Package, label: "Python SDK", desc: "vertexops-python on PyPI" },
  { icon: Terminal, label: "CLI Tool", desc: "vertexops-cli for terminal" },
  { icon: Book, label: "REST API", desc: "OpenAPI / Swagger spec" },
  { icon: Webhook, label: "Webhooks", desc: "Real-time event streams" },
];

export function APISection() {
  return (
    <section id="api" className="section-padding bg-gray-50">
      <div className="container-max">
        <AnimateOnScroll className="text-center mb-16">
          <div className="section-label">
            <span className="w-1.5 h-1.5 rounded-full bg-primary-500" />
            Developer Experience
          </div>
          <h2 className="section-heading mb-4">
            Built for Developers,{" "}
            <span className="gradient-text">by Developers</span>
          </h2>
          <p className="section-subheading mx-auto">
            A complete API ecosystem so your team can integrate VertexOps into
            any workflow, pipeline, or internal tool.
          </p>
        </AnimateOnScroll>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Code block */}
          <AnimateOnScroll direction="left">
            <div className="code-block relative">
              <div className="flex items-center gap-2 mb-5">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/70" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
                  <div className="w-3 h-3 rounded-full bg-green-500/70" />
                </div>
                <span className="text-xs text-gray-500 font-mono ml-2">quickstart.py</span>
              </div>
              <pre
                className="text-sm leading-relaxed overflow-x-auto"
                dangerouslySetInnerHTML={{ __html: CODE_EXAMPLE }}
              />
            </div>
          </AnimateOnScroll>

          {/* Feature list */}
          <AnimateOnScroll direction="right">
            <div className="grid grid-cols-2 gap-4 mb-8">
              {FEATURES.map(({ icon: Icon, label, desc }) => (
                <div key={label} className="card-base p-5">
                  <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center mb-3">
                    <Icon className="w-5 h-5 text-primary-500" />
                  </div>
                  <div className="text-sm font-bold text-gray-900 mb-1">{label}</div>
                  <div className="text-xs text-gray-500">{desc}</div>
                </div>
              ))}
            </div>

            <div className="space-y-4 mb-8">
              {[
                {
                  method: "GET",
                  path: "/api/v1/health",
                  desc: "Liveness probe",
                  color: "bg-green-100 text-green-700",
                },
                {
                  method: "POST",
                  path: "/api/v1/query",
                  desc: "RAG query with citations",
                  color: "bg-blue-100 text-blue-700",
                },
                {
                  method: "POST",
                  path: "/api/v1/incidents/{id}/remediate",
                  desc: "Trigger auto-remediation",
                  color: "bg-blue-100 text-blue-700",
                },
                {
                  method: "GET",
                  path: "/api/v1/metrics",
                  desc: "Prometheus export",
                  color: "bg-green-100 text-green-700",
                },
              ].map(({ method, path, desc, color }) => (
                <div
                  key={path}
                  className="flex items-center gap-3 p-3 bg-white rounded-xl border border-gray-100"
                >
                  <span
                    className={`text-xs font-bold px-2.5 py-1 rounded-md font-mono flex-shrink-0 ${color}`}
                  >
                    {method}
                  </span>
                  <code className="text-xs text-gray-600 font-mono truncate">{path}</code>
                  <span className="text-xs text-gray-400 ml-auto flex-shrink-0 hidden sm:block">
                    {desc}
                  </span>
                </div>
              ))}
            </div>

            <a href="#" className="btn-primary inline-flex items-center gap-2">
              Explore API Docs
              <ArrowRight className="w-4 h-4" />
            </a>
          </AnimateOnScroll>
        </div>
      </div>
    </section>
  );
}
