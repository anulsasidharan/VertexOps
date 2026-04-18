import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EvaluationRunSummary } from "@/components/evaluation/EvaluationRunSummary";
import type { EvaluationDetailDto } from "@/api/types";

const base = (): EvaluationDetailDto => ({
  id: "r1",
  experiment_id: "e1",
  status: "queued",
  started_at: null,
  finished_at: null,
  artifact_uri: null,
  metrics: null,
});

describe("EvaluationRunSummary", () => {
  it("shows status without metrics", () => {
    render(<EvaluationRunSummary detail={base()} />);
    expect(screen.getByTestId("eval-summary")).toHaveTextContent("queued");
    expect(screen.getByText(/no metrics yet/i)).toBeInTheDocument();
  });

  it("renders metrics JSON", () => {
    const d = base();
    d.metrics = { case_count: 2, avg_relevance: 0.5 };
    render(<EvaluationRunSummary detail={d} />);
    expect(screen.getByText(/case_count/i)).toBeInTheDocument();
  });
});
