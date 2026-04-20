import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AuthSessionProvider } from "@/context/AuthSessionContext";
import { DashboardLayout } from "@/layout/DashboardLayout";
import { ChatOpsPage } from "@/pages/ChatOpsPage";
import { CompliancePage } from "@/pages/CompliancePage";
import { CostPage } from "@/pages/CostPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { DocumentDetailPage } from "@/pages/DocumentDetailPage";
import { DocumentsPage } from "@/pages/DocumentsPage";
import { EvaluationsPage } from "@/pages/EvaluationsPage";
import { ExperimentsPage } from "@/pages/ExperimentsPage";
import { HomePage } from "@/pages/HomePage";
import { IncidentsPage } from "@/pages/IncidentsPage";
import { IndexesPage } from "@/pages/IndexesPage";
import { InfrastructurePage } from "@/pages/InfrastructurePage";
import { IntegrationsPage } from "@/pages/IntegrationsPage";
import { LoginPage } from "@/pages/LoginPage";
import { NotificationsPage } from "@/pages/NotificationsPage";
import { QueryPlaygroundPage } from "@/pages/QueryPlaygroundPage";
import { SettingsPage } from "@/pages/SettingsPage";

export function App() {
  return (
    <AuthSessionProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<DashboardLayout />}>
              {/* Legacy home → redirect to dashboard */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/home" element={<HomePage />} />

              {/* Operations */}
              <Route path="/dashboard"      element={<DashboardPage />} />
              <Route path="/infrastructure" element={<InfrastructurePage />} />
              <Route path="/incidents"      element={<IncidentsPage />} />
              <Route path="/chatops"        element={<ChatOpsPage />} />

              {/* FinOps & Compliance */}
              <Route path="/cost"           element={<CostPage />} />
              <Route path="/compliance"     element={<CompliancePage />} />
              <Route path="/notifications"  element={<NotificationsPage />} />
              <Route path="/integrations"   element={<IntegrationsPage />} />

              {/* RAG Platform */}
              <Route path="/documents"                    element={<DocumentsPage />} />
              <Route path="/documents/:documentId"        element={<DocumentDetailPage />} />
              <Route path="/indexes"                      element={<IndexesPage />} />
              <Route path="/query"                        element={<QueryPlaygroundPage />} />
              <Route path="/experiments"                  element={<ExperimentsPage />} />
              <Route path="/evaluations"                  element={<EvaluationsPage />} />

              {/* Account */}
              <Route path="/settings"       element={<SettingsPage />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthSessionProvider>
  );
}
