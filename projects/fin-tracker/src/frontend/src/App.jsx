import { Navigate, Route, Routes } from "react-router-dom";
import { useState, useEffect, Component } from "react";

import MainLayout from "./layouts/MainLayout";
import AlertsPage from "./pages/AlertsPage";
import CompanyAnalyticsPage from "./pages/CompanyAnalyticsPage";
import CompanyDetailPage from "./pages/CompanyDetailPage";
import CompanyFormPage from "./pages/CompanyFormPage";
import CompanyListPage from "./pages/CompanyListPage";
import ComparePage from "./pages/ComparePage";
import DashboardPage from "./pages/DashboardPage";
import ReviewExtractionPage from "./pages/ReviewExtractionPage";
import UploadReportPage from "./pages/UploadReportPage";
import { AlertProvider } from "./contexts/AlertContext";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.log('Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
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

export default function App() {
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleError = (event) => {
      setError({
        message: event.error?.message || "Unknown error",
        stack: event.error?.stack || "No stack trace"
      });
    };
    window.addEventListener("error", handleError);
    return () => window.removeEventListener("error", handleError);
  }, []);

  if (error) {
    return (
      <div style={{ padding: "20px", color: "red" }}>
        <h1>JavaScript Error</h1>
        <p><strong>Message:</strong> {error.message}</p>
        <pre style={{ whiteSpace: "pre-wrap", fontSize: "12px" }}>
          {error.stack}
        </pre>
      </div>
    );
  }

  return (
    <ErrorBoundary>
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
          </Routes>
        </MainLayout>
      </AlertProvider>
    </ErrorBoundary>
  );
}
