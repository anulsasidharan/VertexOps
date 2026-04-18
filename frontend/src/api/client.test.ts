import { describe, expect, it } from "vitest";

import { buildAuthHeaders } from "@/api/client";

describe("buildAuthHeaders", () => {
  it("returns Bearer header for jwt mode", () => {
    expect(buildAuthHeaders("jwt", "abc", null)).toEqual({ Authorization: "Bearer abc" });
  });

  it("returns X-API-Key for api_key mode", () => {
    expect(buildAuthHeaders("api_key", null, "secret")).toEqual({ "X-API-Key": "secret" });
  });

  it("returns empty object when mode is none", () => {
    expect(buildAuthHeaders("none", "x", "y")).toEqual({});
  });
});
