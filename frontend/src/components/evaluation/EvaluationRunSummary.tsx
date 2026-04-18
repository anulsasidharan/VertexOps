import type { EvaluationDetailDto } from "@/api/types";

type Props = {
  detail: EvaluationDetailDto;
};

export function EvaluationRunSummary({ detail }: Props) {
  return (
    <div data-testid="eval-summary" className="space-y-2">
      <p className="font-mono text-sm">
        <span className="text-slate-500">status</span> {detail.status}
      </p>
      {detail.metrics ? (
        <pre className="max-h-48 overflow-auto rounded bg-slate-950 p-2 text-xs text-slate-300">
          {JSON.stringify(detail.metrics, null, 2)}
        </pre>
      ) : (
        <p className="text-xs text-slate-500">No metrics yet.</p>
      )}
    </div>
  );
}
