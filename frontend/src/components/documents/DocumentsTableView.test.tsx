import { render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import {
  DocumentsTableView,
  type LoadState,
} from "@/components/documents/DocumentsTableView";
import type { DocumentDto } from "@/api/types";

const sampleDoc = (over: Partial<DocumentDto> = {}): DocumentDto => ({
  id: "00000000-0000-0000-0000-000000000001",
  workspace_id: "00000000-0000-0000-0000-000000000002",
  title: "Doc A",
  source_uri: null,
  format: "pdf",
  language: null,
  content_hash: null,
  ingest_status: "ready",
  doc_metadata: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-02T00:00:00Z",
  ...over,
});

function renderView(
  state: LoadState,
  items: DocumentDto[],
  error: string | null = null,
  filter = ""
) {
  return render(
    <MemoryRouter>
      <DocumentsTableView
        state={state}
        items={items}
        error={error}
        statusFilter={filter}
        onStatusFilterChange={() => {}}
      />
    </MemoryRouter>
  );
}

describe("DocumentsTableView", () => {
  it("shows loading", () => {
    renderView("loading", []);
    expect(screen.getByText(/loading documents/i)).toBeInTheDocument();
  });

  it("shows error", () => {
    renderView("error", [], "network down");
    expect(screen.getByText("network down")).toBeInTheDocument();
  });

  it("shows empty success state", () => {
    renderView("success", []);
    expect(screen.getByText(/no documents match/i)).toBeInTheDocument();
  });

  it("renders rows in success state", () => {
    renderView("success", [sampleDoc({ title: "Hello", ingest_status: "queued" })]);
    expect(screen.getByText("Hello")).toBeInTheDocument();
    const table = screen.getByRole("table");
    expect(within(table).getByText("queued")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /view/i })).toHaveAttribute(
      "href",
      "/documents/00000000-0000-0000-0000-000000000001"
    );
  });
});
