import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getCompanyById } from "../api/companyApi";

export default function CompanyDetailPage() {
  const { id } = useParams();
  const [company, setCompany] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCompany = async () => {
      setLoading(true);
      setError("");
      try {
        const data = await getCompanyById(id);
        setCompany(data);
      } catch (fetchError) {
        setError("Không thể tải chi tiết doanh nghiệp.");
      } finally {
        setLoading(false);
      }
    };

    fetchCompany();
  }, [id]);

  if (loading) {
    return <p className="text-sm text-slate-500">Đang tải dữ liệu...</p>;
  }

  if (error) {
    return <p className="text-sm text-red-600">{error}</p>;
  }

  if (!company) {
    return <p className="text-sm text-slate-500">Không có dữ liệu doanh nghiệp.</p>;
  }

  return (
    <section className="space-y-4 rounded-xl bg-white p-6 shadow">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">{company.name}</h1>
          <p className="mt-1 text-sm text-slate-500">
            Mã: <span className="font-semibold text-slate-700">{company.code}</span>
          </p>
        </div>

        <Link
          to={`/companies/${company.id}/edit`}
          className="rounded-md bg-emerald-500 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-600"
        >
          Cập nhật
        </Link>
      </div>

      <dl className="grid gap-4 md:grid-cols-2">
        <div>
          <dt className="text-sm text-slate-500">Sàn giao dịch</dt>
          <dd className="text-base font-medium text-slate-800">{company.exchange}</dd>
        </div>

        <div>
          <dt className="text-sm text-slate-500">Ngành</dt>
          <dd className="text-base font-medium text-slate-800">{company.industry || "-"}</dd>
        </div>

        <div>
          <dt className="text-sm text-slate-500">Website</dt>
          <dd className="text-base font-medium text-slate-800 break-all">
            {company.website ? (
              <a href={company.website} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
                {company.website}
              </a>
            ) : (
              "-"
            )}
          </dd>
        </div>

        <div>
          <dt className="text-sm text-slate-500">Cập nhật gần nhất</dt>
          <dd className="text-base font-medium text-slate-800">
            {new Date(company.updated_at).toLocaleString("vi-VN")}
          </dd>
        </div>
      </dl>

      <div>
        <h2 className="text-sm text-slate-500">Mô tả</h2>
        <p className="mt-1 whitespace-pre-wrap text-slate-800">{company.description || "-"}</p>
      </div>
    </section>
  );
}
