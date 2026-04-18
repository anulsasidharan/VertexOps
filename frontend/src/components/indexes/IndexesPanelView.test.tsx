import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { IndexesPanelView } from "@/components/indexes/IndexesPanelView";
import type { IndexDto } from "@/api/types";

const idx = (over: Partial<IndexDto> = {}): IndexDto => ({
  id: "00000000-0000-0000-0000-000000000010",
  workspace_id: "00000000-0000-0000-0000-000000000002",
  name: "main",
  vector_backend: "pinecone",
  namespace: null,
  config_hash: null,
  index_config: null,
  status: "ready",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-02T00:00:00Z",
  ...over,
});

describe("IndexesPanelView", () => {
  it("empty success", () => {
    render(
      <IndexesPanelView
        state="success"
        items={[]}
        error={null}
        busyId={null}
        onRebuild={() => {}}
      />
    );
    expect(screen.getByText(/no indexes yet/i)).toBeInTheDocument();
  });

  it("calls onRebuild", async () => {
    const user = userEvent.setup();
    const onRebuild = vi.fn();
    render(
      <IndexesPanelView
        state="success"
        items={[idx()]}
        error={null}
        busyId={null}
        onRebuild={onRebuild}
      />
    );
    await user.click(screen.getByRole("button", { name: /rebuild/i }));
    expect(onRebuild).toHaveBeenCalledWith("00000000-0000-0000-0000-000000000010");
  });
});
