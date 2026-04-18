import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it } from "vitest";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AuthSessionProvider } from "@/context/AuthSessionContext";

function Inside() {
  return <div data-testid="inside">protected</div>;
}

afterEach(() => {
  localStorage.clear();
});

describe("ProtectedRoute", () => {
  it("redirects to login when there is no session", () => {
    render(
      <MemoryRouter initialEntries={["/app"]}>
        <AuthSessionProvider>
          <Routes>
            <Route element={<ProtectedRoute />}>
              <Route path="/app" element={<Inside />} />
            </Route>
            <Route path="/login" element={<div>login-page</div>} />
          </Routes>
        </AuthSessionProvider>
      </MemoryRouter>
    );
    expect(screen.getByText("login-page")).toBeInTheDocument();
    expect(screen.queryByTestId("inside")).not.toBeInTheDocument();
  });

  it("renders child routes when JWT is restored from storage", () => {
    localStorage.setItem("vertexops_auth_mode", "jwt");
    localStorage.setItem("vertexops_jwt", "stored.jwt.token");

    render(
      <MemoryRouter initialEntries={["/app"]}>
        <AuthSessionProvider>
          <Routes>
            <Route element={<ProtectedRoute />}>
              <Route path="/app" element={<Inside />} />
            </Route>
            <Route path="/login" element={<div>login-page</div>} />
          </Routes>
        </AuthSessionProvider>
      </MemoryRouter>
    );
    expect(screen.getByTestId("inside")).toBeInTheDocument();
  });

  it("renders child routes when API key is restored from storage", () => {
    localStorage.setItem("vertexops_auth_mode", "api_key");
    localStorage.setItem("vertexops_api_key", "vo_test_key");

    render(
      <MemoryRouter initialEntries={["/app"]}>
        <AuthSessionProvider>
          <Routes>
            <Route element={<ProtectedRoute />}>
              <Route path="/app" element={<Inside />} />
            </Route>
            <Route path="/login" element={<div>login-page</div>} />
          </Routes>
        </AuthSessionProvider>
      </MemoryRouter>
    );
    expect(screen.getByTestId("inside")).toBeInTheDocument();
  });
});
