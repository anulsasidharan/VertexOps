import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard, Server, AlertTriangle, Bot, DollarSign,
  Shield, Bell, Link2, FlaskConical, BarChart3, Settings,
  FileText, Search, ChevronLeft, ChevronRight,
} from "lucide-react";
import { useAuthSession } from "@/context/AuthSessionContext";

const NAV_SECTIONS = [
  {
    label: "Operations",
    items: [
      { to: "/dashboard",       icon: LayoutDashboard, label: "Dashboard"       },
      { to: "/infrastructure",  icon: Server,          label: "Infrastructure"  },
      { to: "/incidents",       icon: AlertTriangle,   label: "Incidents"       },
      { to: "/chatops",         icon: Bot,             label: "ChatOps AI"      },
    ],
  },
  {
    label: "FinOps & Compliance",
    items: [
      { to: "/cost",            icon: DollarSign,      label: "Cost"            },
      { to: "/compliance",      icon: Shield,          label: "Compliance"      },
      { to: "/notifications",   icon: Bell,            label: "Notifications"   },
      { to: "/integrations",    icon: Link2,           label: "Integrations"    },
    ],
  },
  {
    label: "RAG Platform",
    items: [
      { to: "/documents",       icon: FileText,        label: "Documents"       },
      { to: "/indexes",         icon: Search,          label: "Indexes"         },
      { to: "/query",           icon: Bot,             label: "Query"           },
      { to: "/experiments",     icon: FlaskConical,    label: "Experiments"     },
      { to: "/evaluations",     icon: BarChart3,       label: "Evaluations"     },
    ],
  },
  {
    label: "Account",
    items: [
      { to: "/settings",        icon: Settings,        label: "Settings"        },
    ],
  },
];

export function DashboardLayout() {
  const { clearSession } = useAuthSession();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex min-h-screen bg-slate-950">
      {/* Sidebar */}
      <aside className={`flex flex-col border-r border-slate-800 bg-slate-950 transition-all duration-200 flex-shrink-0 ${collapsed ? "w-14" : "w-56"}`}>
        {/* Logo */}
        <div className={`flex items-center gap-2 px-3 py-4 border-b border-slate-800 ${collapsed ? "justify-center" : ""}`}>
          <span className="text-xl">⚡</span>
          {!collapsed && <span className="text-sm font-bold text-slate-100 tracking-tight">VertexOps</span>}
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto py-3 space-y-4 px-2">
          {NAV_SECTIONS.map((section) => (
            <div key={section.label}>
              {!collapsed && (
                <div className="px-2 mb-1 text-[9px] font-bold text-slate-600 uppercase tracking-widest">
                  {section.label}
                </div>
              )}
              <div className="space-y-0.5">
                {section.items.map(({ to, icon: Icon, label }) => (
                  <NavLink
                    key={to}
                    to={to}
                    className={({ isActive }) =>
                      `flex items-center gap-2.5 rounded-lg px-2 py-2 text-xs font-medium transition-colors ${
                        isActive
                          ? "bg-indigo-600/20 text-indigo-300 border border-indigo-600/30"
                          : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                      } ${collapsed ? "justify-center" : ""}`
                    }
                    title={collapsed ? label : undefined}
                  >
                    <Icon className="w-4 h-4 flex-shrink-0" />
                    {!collapsed && <span>{label}</span>}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>

        {/* Bottom */}
        <div className="border-t border-slate-800 p-2 space-y-1">
          <button
            type="button"
            onClick={() => setCollapsed((c) => !c)}
            className="w-full flex items-center justify-center gap-2 rounded-lg px-2 py-2 text-xs text-slate-500 hover:bg-slate-800 hover:text-slate-300 transition-colors"
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <><ChevronLeft className="w-4 h-4" /><span>Collapse</span></>}
          </button>
          <button
            type="button"
            className={`w-full flex items-center gap-2 rounded-lg px-2 py-2 text-xs text-slate-500 hover:bg-slate-800 hover:text-red-400 transition-colors ${collapsed ? "justify-center" : ""}`}
            onClick={() => clearSession()}
            title={collapsed ? "Sign out" : undefined}
          >
            <span className="text-base">↩</span>
            {!collapsed && <span>Sign out</span>}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-w-0 overflow-auto p-6">
        <Outlet />
      </main>
    </div>
  );
}
