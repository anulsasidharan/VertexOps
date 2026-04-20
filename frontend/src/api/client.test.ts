import { describe, expect, it } from "vitest";

import { normalizeApiBaseUrl } from "./client";

describe("normalizeApiBaseUrl", () => {
  it("defaults to /api/v1 when unset or empty", () => {
    expect(normalizeApiBaseUrl(undefined)).toBe("/api/v1");
    expect(normalizeApiBaseUrl("")).toBe("/api/v1");
    expect(normalizeApiBaseUrl("  ")).toBe("/api/v1");
  });

  it("appends /api/v1 to bare http origin", () => {
    expect(normalizeApiBaseUrl("http://127.0.0.1:8000")).toBe("http://127.0.0.1:8000/api/v1");
    expect(normalizeApiBaseUrl("http://127.0.0.1:8000/")).toBe("http://127.0.0.1:8000/api/v1");
  });

  it("leaves full versioned URL unchanged", () => {
    expect(normalizeApiBaseUrl("https://api.example.com/api/v1/")).toBe("https://api.example.com/api/v1");
    expect(normalizeApiBaseUrl("https://api.example.com/api/v2")).toBe("https://api.example.com/api/v2");
  });

  it("maps relative /api to /api/v1", () => {
    expect(normalizeApiBaseUrl("/api")).toBe("/api/v1");
  });

  it("leaves relative /api/v1 unchanged", () => {
    expect(normalizeApiBaseUrl("/api/v1")).toBe("/api/v1");
  });

  it("in dev, treats localhost:3000 as Next landing and falls back to /api/v1", () => {
    expect(normalizeApiBaseUrl("http://localhost:3000", { dev: true })).toBe("/api/v1");
    expect(normalizeApiBaseUrl("http://127.0.0.1:3000/api/v1", { dev: true })).toBe("/api/v1");
  });

  it("outside dev, localhost:3000 is normalized with /api/v1 suffix only", () => {
    expect(normalizeApiBaseUrl("http://localhost:3000", { dev: false })).toBe(
      "http://localhost:3000/api/v1"
    );
  });
});
