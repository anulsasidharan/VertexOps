import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuthSession } from "@/context/AuthSessionContext";

/**
 * Wraps nested routes: redirects unauthenticated users to ``/login``.
 */
export function ProtectedRoute() {
  const { isAuthenticated } = useAuthSession();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}
