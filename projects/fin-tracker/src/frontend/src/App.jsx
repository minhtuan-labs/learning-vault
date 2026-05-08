import { Component } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "./contexts/AuthContext";
import MainLayout from "./layouts/MainLayout";
import AlertsPage from "./pages/AlertsPage";
import CompanyAnalyticsPage from "./pages/CompanyAnalyticsPage";
import CompanyDetailPage from "./pages/CompanyDetailPage";
import CompanyFormPage from "./pages/CompanyFormPage";
import CompanyListPage from "./pages/CompanyListPage";
import ComparePage from "./pages/ComparePage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import ReviewExtractionPage from "./pages/ReviewExtractionPage";
import SettingsPage from "./pages/SettingsPage";
import UploadReportPage from "./pages/UploadReportPage";
import { AlertProvider } from "./contexts/AlertContext";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("React error:", error, errorInfo);
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: "20px", color: "red" }}>
          <h1>React Error</h1>
          <p><strong>Message:</strong> {this.state.error?.message}</p>
          <pre style={{ whiteSpace: "pre-wrap", fontSize: "12px" }}>
            {this.state.error?.stack}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-500">Đang tải...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="*"
          element={
            <ProtectedRoute>
              <AlertProvider>
                <MainLayout>
                  <Routes>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/alerts" element={<AlertsPage />} />
                    <Route path="/companies" element={<CompanyListPage />} />
                    <Route path="/companies/new" element={<CompanyFormPage mode="create" />} />
                    <Route path="/companies/:id" element={<CompanyDetailPage />} />
                    <Route path="/companies/:id/edit" element={<CompanyFormPage mode="edit" />} />
                    <Route path="/companies/:companyId/reports/upload" element={<UploadReportPage />} />
                    <Route path="/companies/:companyId/periods/:periodId/review" element={<ReviewExtractionPage />} />
                    <Route path="/companies/:companyId/analytics" element={<CompanyAnalyticsPage />} />
                    <Route path="/analytics/compare" element={<ComparePage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                  </Routes>
                </MainLayout>
              </AlertProvider>
            </ProtectedRoute>
          }
        />
      </Routes>
    </ErrorBoundary>
  );
}