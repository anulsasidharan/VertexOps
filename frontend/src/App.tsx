import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AuthSessionProvider } from "@/context/AuthSessionContext";
import { DashboardLayout } from "@/layout/DashboardLayout";
import { DocumentDetailPage } from "@/pages/DocumentDetailPage";
import { DocumentsPage } from "@/pages/DocumentsPage";
import { EvaluationsPage } from "@/pages/EvaluationsPage";
import { HomePage } from "@/pages/HomePage";
import { IndexesPage } from "@/pages/IndexesPage";
import { LoginPage } from "@/pages/LoginPage";
import { QueryPlaygroundPage } from "@/pages/QueryPlaygroundPage";

export function App() {
  return (
    <AuthSessionProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<DashboardLayout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="/documents/:documentId" element={<DocumentDetailPage />} />
              <Route path="/indexes" element={<IndexesPage />} />
              <Route path="/query" element={<QueryPlaygroundPage />} />
              <Route path="/evaluations" element={<EvaluationsPage />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthSessionProvider>
  );
}
