import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getCompanyById } from "../api/companyApi";
import { listFinancialPeriods, listPeriodFiles, deleteFinancialPeriod } from "../api/periodApi";

function truncateFileName(name, maxLen = 40) {
  if (!name || name.length <= maxLen) return name;
  const half = Math.floor((maxLen - 3) / 2);
  return name.slice(0, half) + "..." + name.slice(-half);
}

export default function CompanyDetailPage() {
  const { id } = useParams();
  const [company, setCompany] = useState(null);
  const [periods, setPeriods] = useState([]);
  const [filesByPeriod, setFilesByPeriod] = useState({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [deletingPeriodId, setDeletingPeriodId] = useState(null);

  const fetchAll = async () => {
    setLoading(true);
    setError("");
    try {
      const c = await getCompanyById(id);
      setCompany(c);
      const plist = await listFinancialPeriods(id);
      setPeriods(plist);
      const map = {};
      await Promise.all(
        plist.map(async (p) => {
          try {
            map[p.id] = await listPeriodFiles(p.id);
          } catch {
            map[p.id] = [];
          }
        })
      );
      setFilesByPeriod(map);
    } catch {
      setError("Không thể tải chi tiết doanh nghiệp.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, [id]);

  const handleDeletePeriod = async (periodId) => {
    setError("");
    if (!confirm("Bạn có chắc muốn xoá kỳ báo cáo này cùng toàn bộ file và số liệu?")) return;
    setDeletingPeriodId(periodId);
    try {
      await deleteFinancialPeriod(id, periodId);
      await fetchAll();
    } catch {
      setError("Không xoá được kỳ báo cáo. Thử lại.");
    } finally {
      setDeletingPeriodId(null);
    }
  };

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
    <div className="space-y-6">
      <section className="space-y-4 rounded-xl bg-white p-6 shadow">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">{company.name}</h1>
            <p className="mt-1 text-sm text-slate-500">
              Mã: <span className="font-semibold text-slate-700">{company.code}</span>
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Link
              to={`/companies/${company.id}/analytics`}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Xem phân tích
            </Link>
            <Link
              to={`/companies/${company.id}/edit`}
              className="rounded-md bg-emerald-500 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-600"
            >
              Cập nhật
            </Link>
          </div>
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

      <section className="rounded-xl bg-white p-6 shadow">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-slate-900">Báo cáo tài chính</h2>
          <Link
            to={`/companies/${company.id}/reports/upload`}
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
          >
            Thêm kỳ báo cáo mới
          </Link>
        </div>

        {periods.length === 0 ? (
          <p className="text-sm text-slate-500">Chưa có kỳ báo cáo nào.</p>
        ) : (
          <ul className="divide-y divide-slate-100 rounded-lg border border-slate-200">
            {periods.map((p) => {
              const files = filesByPeriod[p.id] || [];
              const label =
                p.period_type === "Y"
                  ? `Năm ${p.year} (cả năm)`
                  : `Năm ${p.year} — Quý ${p.quarter}`;
              return (
                <li key={p.id} className="flex flex-col gap-2 px-4 py-4 md:flex-row md:items-center md:justify-between">
                  <div>
                    <p className="font-medium text-slate-800">{label}</p>
                    <p className="text-xs text-slate-500">
                      {files.length} file PDF
                      {files[0] ? ` — mới nhất: ${truncateFileName(files[0].file_name)}` : ""}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Link
                      to={`/companies/${company.id}/reports/upload?periodId=${p.id}`}
                      className="rounded border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
                    >
                      Tải PDF
                    </Link>
                    <Link
                      to={`/companies/${company.id}/periods/${p.id}/review`}
                      className="rounded bg-emerald-50 px-3 py-1.5 text-sm font-medium text-emerald-800 hover:bg-emerald-100"
                    >
                      Xem & kiểm tra số liệu
                    </Link>
                    <button
                      type="button"
                      onClick={() => handleDeletePeriod(p.id)}
                      disabled={deletingPeriodId === p.id}
                      className="rounded border border-red-300 px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-red-50 disabled:opacity-50"
                    >
                      {deletingPeriodId === p.id ? "Đang xoá…" : "Xoá kỳ"}
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
}
