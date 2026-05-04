import { useEffect, useMemo, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";

import {
  listFinancialData,
  listPeriodFiles,
  pdfFileUrl,
  updateFinancialMetric,
  verifyPeriodData,
} from "../api/periodApi";

export default function ReviewExtractionPage() {
  const { companyId, periodId } = useParams();
  const [searchParams] = useSearchParams();
  const fileIdParam = searchParams.get("fileId");

  const [files, setFiles] = useState([]);
  const [fileId, setFileId] = useState(null);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [savingId, setSavingId] = useState(null);

  const allVerified = useMemo(() => rows.length > 0 && rows.every((r) => r.is_verified), [rows]);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const fList = await listPeriodFiles(periodId);
      setFiles(fList);
      const fid = fileIdParam ? Number(fileIdParam) : fList[0]?.id;
      setFileId(fid || null);

      const data = await listFinancialData(periodId);
      setRows(data);
    } catch (e) {
      setError("Không tải được dữ liệu kỳ báo cáo.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [periodId, fileIdParam]);

  const handleChangeValue = (id, value) => {
    setRows((prev) => prev.map((r) => (r.id === id ? { ...r, metric_value: value } : r)));
  };

  const handleBlurSave = async (row) => {
    const num = Number(row.metric_value);
    if (Number.isNaN(num)) {
      return;
    }
    setSavingId(row.id);
    try {
      const updated = await updateFinancialMetric(periodId, row.id, { metric_value: num });
      setRows((prev) => prev.map((r) => (r.id === row.id ? updated : r)));
    } catch {
      setError("Không lưu được chỉ số. Thử lại.");
    } finally {
      setSavingId(null);
    }
  };

  const handleVerify = async () => {
    setError("");
    try {
      await verifyPeriodData(periodId);
      await load();
    } catch {
      setError("Không xác nhận được. Thử lại.");
    }
  };

  if (loading) {
    return <p className="text-sm text-slate-500">Đang tải…</p>;
  }

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Kiểm tra số liệu AI</h1>
          <p className="text-sm text-slate-500">
            Kỳ báo cáo #{periodId} —{" "}
            <Link className="text-blue-600 hover:underline" to={`/companies/${companyId}`}>
              Về doanh nghiệp
            </Link>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold ${
              allVerified ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"
            }`}
          >
            {allVerified ? "Đã xác nhận" : "Chờ xác nhận"}
          </span>
          <button
            type="button"
            onClick={handleVerify}
            className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
          >
            Xác nhận toàn bộ
          </button>
        </div>
      </div>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      {!fileId ? (
        <p className="text-sm text-slate-600">Chưa có file PDF cho kỳ này.</p>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="min-h-[70vh] overflow-hidden rounded-xl border border-slate-200 bg-white shadow">
            <iframe
              title="PDF gốc"
              src={pdfFileUrl(periodId, fileId)}
              className="h-[70vh] w-full"
            />
          </div>

          <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow">
            <div className="border-b border-slate-200 px-4 py-3">
              <h2 className="text-sm font-semibold text-slate-800">Số liệu đã trích xuất</h2>
              {files.length > 1 ? (
                <label className="mt-2 flex items-center gap-2 text-xs text-slate-600">
                  Chọn file:
                  <select
                    value={fileId}
                    onChange={(e) => setFileId(Number(e.target.value))}
                    className="rounded border border-slate-300 px-2 py-1 text-xs"
                  >
                    {files.map((f) => (
                      <option key={f.id} value={f.id}>
                        {f.file_name}
                      </option>
                    ))}
                  </select>
                </label>
              ) : null}
            </div>
            <div className="max-h-[70vh] overflow-auto">
              <table className="min-w-full text-sm">
                <thead className="sticky top-0 bg-slate-100 text-left text-xs uppercase text-slate-600">
                  <tr>
                    <th className="px-3 py-2">Loại BC</th>
                    <th className="px-3 py-2">Chỉ tiêu</th>
                    <th className="px-3 py-2">Giá trị</th>
                    <th className="px-3 py-2">Đơn vị</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {rows.map((r) => (
                    <tr key={r.id}>
                      <td className="px-3 py-2 text-slate-600">{r.report_type}</td>
                      <td className="px-3 py-2 font-medium text-slate-800">{r.metric_name}</td>
                      <td className="px-3 py-2">
                        <input
                          type="number"
                          step="any"
                          className="w-full rounded border border-slate-300 px-2 py-1"
                          value={r.metric_value}
                          onChange={(e) => handleChangeValue(r.id, e.target.value)}
                          onBlur={() => handleBlurSave(r)}
                          disabled={savingId === r.id}
                        />
                      </td>
                      <td className="px-3 py-2 text-slate-600">{r.unit}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {rows.length === 0 ? (
                <p className="p-4 text-sm text-slate-500">Chưa có số liệu. Hãy chạy trích xuất từ trang upload.</p>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
