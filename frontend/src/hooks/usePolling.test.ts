import { renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { usePolling } from "@/hooks/usePolling";

afterEach(() => {
  vi.useRealTimers();
});

describe("usePolling", () => {
  it("invokes callback on interval when active", async () => {
    vi.useFakeTimers();
    const fn = vi.fn();
    renderHook(() => usePolling(fn, 1000, true));
    expect(fn).not.toHaveBeenCalled();
    vi.advanceTimersByTime(1000);
    expect(fn).toHaveBeenCalledTimes(1);
    vi.advanceTimersByTime(1000);
    expect(fn).toHaveBeenCalledTimes(2);
  });

  it("does not poll when inactive", () => {
    vi.useFakeTimers();
    const fn = vi.fn();
    renderHook(() => usePolling(fn, 500, false));
    vi.advanceTimersByTime(2000);
    expect(fn).not.toHaveBeenCalled();
  });
});
