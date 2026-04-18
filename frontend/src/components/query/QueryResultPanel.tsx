import type { QueryResponseDto } from "@/api/types";

type Props = {
  loading: boolean;
  error: string | null;
  result: QueryResponseDto | null;
};

export function QueryResultPanel({ loading, error, result }: Props) {
  if (loading) {
    return <p className="text-slate-400">Running query…</p>;
  }
  if (error) {
    return (
      <div className="rounded border border-red-900/50 bg-red-950/30 px-3 py-2 text-sm text-red-200">
        {error}
      </div>
    );
  }
  if (!result) {
    return <p className="text-slate-500">Submit a question to see the answer and sources.</p>;
  }

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-sm font-medium text-slate-400">Answer</h2>
        <p className="mt-1 whitespace-pre-wrap rounded border border-slate-800 bg-slate-900/50 p-3 text-slate-100">
          {result.answer}
        </p>
        <p className="mt-2 text-xs text-slate-500">
          Model {result.model} · {result.latency_ms} ms · tokens in/out {result.prompt_tokens}/
          {result.completion_tokens}
        </p>
      </section>
      <section>
        <h2 className="text-sm font-medium text-slate-400">Sources</h2>
        {result.sources.length === 0 ? (
          <p className="text-slate-500">No chunks returned.</p>
        ) : (
          <ul className="mt-2 space-y-2">
            {result.sources.map((s) => (
              <li
                key={`${s.chunk_id}-${s.document_id}`}
                className="rounded border border-slate-800 bg-slate-900/40 p-3 text-sm"
              >
                <div className="flex justify-between gap-2 text-xs text-slate-500">
                  <span>doc {s.document_id}</span>
                  <span>score {s.score.toFixed(3)}</span>
                </div>
                <p className="mt-1 text-slate-200">{s.text}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
