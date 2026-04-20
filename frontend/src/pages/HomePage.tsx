import { Link } from "react-router-dom";

const NAV_CARDS = [
  {
    to: "/documents",
    title: "Documents",
    description: "Upload, manage, and track ingestion status of corpus documents.",
  },
  {
    to: "/indexes",
    title: "Indexes",
    description: "Create and rebuild vector indexes for retrieval.",
  },
  {
    to: "/query",
    title: "Query playground",
    description: "Run RAG queries against your indexes interactively.",
  },
  {
    to: "/experiments",
    title: "Experiments",
    description: "Create and run evaluation experiments with configuration tracking.",
  },
  {
    to: "/evaluations",
    title: "Evaluations",
    description: "Start async evaluation runs and download reports.",
  },
  {
    to: "/settings",
    title: "Settings",
    description: "Manage API keys for programmatic access.",
  },
];

export function HomePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Dashboard</h1>
        <p className="mt-1 text-sm text-slate-400">
          Manage your LLMOps pipeline from documents to evaluations.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {NAV_CARDS.map(({ to, title, description }) => (
          <Link
            key={to}
            to={to}
            className="rounded border border-slate-800 bg-slate-900/40 p-4 hover:border-slate-600 hover:bg-slate-900/70 transition-colors"
          >
            <h2 className="text-sm font-semibold text-indigo-400">{title}</h2>
            <p className="mt-1 text-xs text-slate-400 leading-relaxed">{description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
