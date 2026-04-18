import { NavLink, Outlet } from "react-router-dom";

import { useAuthSession } from "@/context/AuthSessionContext";

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `rounded px-3 py-2 text-sm font-medium ${
    isActive ? "bg-slate-800 text-white" : "text-slate-300 hover:bg-slate-800/80"
  }`;

export function DashboardLayout() {
  const { clearSession } = useAuthSession();

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="border-b border-slate-800 md:w-56 md:border-b-0 md:border-r md:p-4">
        <div className="mb-6 px-2 text-lg font-semibold tracking-tight">VertexOps</div>
        <nav className="flex flex-wrap gap-1 md:flex-col">
          <NavLink to="/" end className={linkClass}>
            Home
          </NavLink>
        </nav>
        <button
          type="button"
          className="mt-6 w-full rounded border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800"
          onClick={() => clearSession()}
        >
          Sign out
        </button>
      </aside>
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  );
}
