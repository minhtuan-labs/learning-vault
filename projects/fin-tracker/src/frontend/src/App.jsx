import { Navigate, Route, Routes } from "react-router-dom";

import MainLayout from "./layouts/MainLayout";
import CompanyDetailPage from "./pages/CompanyDetailPage";
import CompanyFormPage from "./pages/CompanyFormPage";
import CompanyListPage from "./pages/CompanyListPage";

export default function App() {
  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/companies" replace />} />
        <Route path="/companies" element={<CompanyListPage />} />
        <Route path="/companies/new" element={<CompanyFormPage mode="create" />} />
        <Route path="/companies/:id" element={<CompanyDetailPage />} />
        <Route path="/companies/:id/edit" element={<CompanyFormPage mode="edit" />} />
      </Routes>
    </MainLayout>
  );
}
