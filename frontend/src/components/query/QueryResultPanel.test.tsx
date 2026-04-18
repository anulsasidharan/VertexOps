import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { QueryResultPanel } from "@/components/query/QueryResultPanel";
import type { QueryResponseDto } from "@/api/types";

const sample: QueryResponseDto = {
  answer: "It works.",
  sources: [
    {
      chunk_id: "c1",
      document_id: "d1",
      score: 0.9,
      text: "Context line",
      section_path: null,
    },
  ],
  model: "gpt-test",
  latency_ms: 42,
  prompt_tokens: 10,
  completion_tokens: 5,
};

describe("QueryResultPanel", () => {
  it("loading", () => {
    render(<QueryResultPanel loading error={null} result={null} />);
    expect(screen.getByText(/running query/i)).toBeInTheDocument();
  });

  it("error", () => {
    render(<QueryResultPanel loading={false} error="boom" result={null} />);
    expect(screen.getByText("boom")).toBeInTheDocument();
  });

  it("empty", () => {
    render(<QueryResultPanel loading={false} error={null} result={null} />);
    expect(screen.getByText(/submit a question/i)).toBeInTheDocument();
  });

  it("success", () => {
    render(<QueryResultPanel loading={false} error={null} result={sample} />);
    expect(screen.getByText("It works.")).toBeInTheDocument();
    expect(screen.getByText("Context line")).toBeInTheDocument();
  });
});
