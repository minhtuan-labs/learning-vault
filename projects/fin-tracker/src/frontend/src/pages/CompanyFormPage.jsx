import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { createCompany, getCompanyById, updateCompany } from "../api/companyApi";
import CompanyForm from "../components/CompanyForm";

export default function CompanyFormPage({ mode }) {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = mode === "edit";

  const [initialData, setInitialData] = useState(null);
  const [loading, setLoading] = useState(isEdit);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isEdit) {
      return;
    }

    const fetchCompany = async () => {
      setLoading(true);
      setError("");

      try {
        const data = await getCompanyById(id);
        setInitialData(data);
      } catch (fetchError) {
        setError("Không thể tải dữ liệu để cập nhật.");
      } finally {
        setLoading(false);
      }
    };

    fetchCompany();
  }, [id, isEdit]);

  const handleSubmit = async (payload) => {
    if (isEdit) {
      const updated = await updateCompany(id, payload);
      navigate(`/companies/${updated.id}`);
      return;
    }

    const created = await createCompany(payload);
    navigate(`/companies/${created.id}`);
  };

  if (loading) {
    return <p className="text-sm text-slate-500">Đang tải dữ liệu...</p>;
  }

  if (error) {
    return <p className="text-sm text-red-600">{error}</p>;
  }

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold text-slate-900">
        {isEdit ? "Cập nhật doanh nghiệp" : "Thêm doanh nghiệp mới"}
      </h1>
      <CompanyForm
        initialData={initialData}
        onSubmit={handleSubmit}
        submitLabel={isEdit ? "Cập nhật" : "Tạo mới"}
      />
    </section>
  );
}
