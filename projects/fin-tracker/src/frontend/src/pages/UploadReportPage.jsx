import { useCallback, useMemo, useEffect, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";

import { REPORT_TYPES } from "../constants/reportTypes";
import {
  createFinancialPeriod,
  extractPeriodData,
  listFinancialPeriods,
  uploadPeriodPdf,
} from "../api/periodApi";

const MAX_BYTES = 50 * 1024 * 1024;

export default function UploadReportPage() {
  const { companyId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const existingPeriodId = searchParams.get("periodId");

  const [year, setYear] = useState(new Date().getFullYear());
  const [quarter, setQuarter] = useState("1");
  const [periodType, setPeriodType] = useState("Q");
  const [reportType, setReportType] = useState("KQKD");
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadPct, setUploadPct] = useState(0);
  const [phase, setPhase] = useState("idle");
  const [error, setError] = useState("");
  const [existingPeriods, setExistingPeriods] = useState([]);
  const [showReplaceConfirm, setShowReplaceConfirm] = useState(false);
  const [pendingSubmit, setPendingSubmit] = useState(null);

  const title = useMemo(
    () => (existingPeriodId ? "Tải lên báo cáo PDF" : "Thêm kỳ & tải lên báo cáo PDF"),
    [existingPeriodId]
  );

  useEffect(() => {
    const loadPeriods = async () => {
      try {
        const periods = await listFinancialPeriods(companyId);
        setExistingPeriods(periods);
      } catch {
        // ignore
      }
    };
    loadPeriods();
  }, [companyId]);

  const checkExistingPeriod = (yr, qtr, pType) => {
    return existingPeriods.find((p) => {
      if (pType === "Y") {
        return p.year === Number(yr) && p.period_type === "Y";
      }
      return (
        p.year === Number(yr) &&
        p.quarter === Number(qtr) &&
        p.period_type === "Q"
      );
    });
  };

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragActive(false);
    const f = e.dataTransfer?.files?.[0];
    if (f) {
      setFile(f);
    }
  }, []);

  const onFileInput = (e) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
    }
  };

  const submitForm = async (periodId, repType, fle) => {
    try {
      if (!periodId) {
        setPhase("creating");
        const payload =
          periodType === "Q"
            ? { year: Number(year), quarter: Number(quarter), period_type: periodType }
            : { year: Number(year), quarter: null, period_type: periodType };
        const period = await createFinancialPeriod(companyId, payload);
        periodId = period.id;
      }

      setPhase("uploading");
      setUploadPct(0);
      const uploaded = await uploadPeriodPdf(periodId, fle, repType, (evt) => {
        if (!evt.total) return;
        setUploadPct(Math.round((evt.loaded / evt.total) * 100));
      });

      setPhase("extracting");
      await extractPeriodData(periodId, { file_id: uploaded.id });

      navigate(`/companies/${companyId}/periods/${periodId}/review?fileId=${uploaded.id}`);
    } catch (err) {
      let msg = "Có lỗi xảy ra.";
      if (err?.response?.data) {
        if (typeof err.response.data === "string") {
          msg = err.response.data;
        } else if (err.response.data.detail) {
          msg = err.response.data.detail;
        }
      } else if (err?.message) {
        msg = err.message;
      }
      setError(msg);
      setPhase("idle");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!file) {
      setError("Vui lòng chọn file PDF.");
      return;
    }
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Chỉ chấp nhận file PDF.");
      return;
    }
    if (file.size > MAX_BYTES) {
      setError("Dung lượng tối đa 50MB.");
      return;
    }

    // Check if period already exists (only for new periods)
    if (!existingPeriodId) {
      const existing = checkExistingPeriod(year, quarter, periodType);
      if (existing) {
        setPendingSubmit({
          year,
          quarter,
          periodType,
          reportType,
          file,
        });
        setShowReplaceConfirm(true);
        return;
      }
    }

    await submitForm(existingPeriodId ? Number(existingPeriodId) : null, reportType, file);
  };

  const handleConfirmReplace = async () => {
    if (!pendingSubmit) return;
    const { year, quarter, periodType, reportType, file } = pendingSubmit;
    setShowReplaceConfirm(false);
    setPendingSubmit(null);
    const existing = checkExistingPeriod(year, quarter, periodType);
    if (existing) {
      await submitForm(existing.id, reportType, file);
    }
  };

  const handleCancelReplace = () => {
    setShowReplaceConfirm(false);
    setPendingSubmit(null);
  };

  return (
    <section className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold text-slate-900">{title}</h1>
        <Link to={`/companies/${companyId}`} className="text-sm font-medium text-blue-600 hover:underline">
          ← Quay lại doanh nghiệp
        </Link>
      </div>

      {showReplaceConfirm ? (
        <div className="rounded-xl bg-white p-6 shadow">
          <h2 className="mb-3 text-lg font-semibold text-slate-900">Xác nhận thay thế</h2>
          <p className="mb-4 text-sm text-slate-600">
            Kỳ báo cáo này đã tồn tại. Bạn có muốn thay thế dữ liệu cũ bằng file mới không?
          </p>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleConfirmReplace}
              className="rounded-md bg-red-500 px-4 py-2 text-sm font-medium text-white hover:bg-red-600"
            >
              Thay thế
            </button>
            <button
              type="button"
              onClick={handleCancelReplace}
              className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Hủy
            </button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6 rounded-xl bg-white p-6 shadow">
          {!existingPeriodId ? (
            <div className="grid gap-4 md:grid-cols-2">
              <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
                Năm báo cáo
                <input
                  type="number"
                  min={2000}
                  max={2100}
                  value={year}
                  onChange={(ev) => setYear(ev.target.value)}
                  className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500"
                  required
                />
              </label>

              <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
                Loại kỳ
                <select
                  value={periodType}
                  onChange={(ev) => setPeriodType(ev.target.value)}
                  className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500"
                >
                  <option value="Q">Theo quý</option>
                  <option value="Y">Cả năm</option>
                </select>
              </label>

              {periodType === "Q" ? (
                <label className="flex flex-col gap-2 text-sm font-medium text-slate-700 md:col-span-2">
                  Quý
                  <select
                    value={quarter}
                    onChange={(ev) => setQuarter(ev.target.value)}
                    className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500"
                  >
                    <option value="1">Quý 1</option>
                    <option value="2">Quý 2</option>
                    <option value="3">Quý 3</option>
                    <option value="4">Quý 4</option>
                  </select>
                </label>
              ) : null}
            </div>
          ) : (
            <p className="text-sm text-slate-600">
              Đang tải file cho kỳ báo cáo có sẵn (mã kỳ: <span className="font-mono">{existingPeriodId}</span>).
            </p>
          )}

          <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
            Loại báo cáo
            <select
              value={reportType}
              onChange={(ev) => setReportType(ev.target.value)}
              className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500"
            >
              {REPORT_TYPES.map((rt) => (
                <option key={rt} value={rt}>
                  {rt}
                </option>
              ))}
            </select>
          </label>

          <div>
            <p className="mb-2 text-sm font-medium text-slate-700">File PDF (tối đa 50MB)</p>
            <div
              onDragEnter={(ev) => { ev.preventDefault(); setDragActive(true); }}
              onDragOver={(ev) => ev.preventDefault()}
              onDragLeave={() => setDragActive(false)}
              onDrop={onDrop}
              className={`flex min-h-[160px] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-4 py-8 text-center transition ${
                dragActive ? "border-emerald-500 bg-emerald-50" : "border-slate-300 bg-slate-50"
              }`}
            >
              <input type="file" accept="application/pdf" className="hidden" id="pdf-upload" onChange={onFileInput} />
              <label htmlFor="pdf-upload" className="cursor-pointer text-sm text-slate-600">
                Kéo thả PDF vào đây hoặc <span className="font-medium text-emerald-600">chọn file</span>
              </label>
              {file ? (
                <p className="mt-3 text-sm font-medium text-slate-800">
                  {file.name} — {(file.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              ) : null}
            </div>
          </div>

          {error ? <p className="text-sm text-red-600">{error}</p> : null}

          {phase !== "idle" ? (
            <div className="space-y-2">
              <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
                {phase === "uploading" ? (
                  <div className="h-full bg-emerald-500 transition-all" style={{ width: `${uploadPct}%` }} />
                ) : (
                  <div className="h-full w-full animate-pulse bg-emerald-400" />
                )}
              </div>
              <p className="text-xs text-slate-500">
                {phase === "creating" && "Đang tạo kỳ báo cáo…"}
                {phase === "uploading" && `Đang tải file lên… ${uploadPct}%`}
                {phase === "extracting" && "AI đang trích xuất số liệu (có thể mất vài phút)…"}
              </p>
            </div>
          ) : null}

          <button
            type="submit"
            disabled={phase !== "idle"}
            className="rounded-md bg-emerald-500 px-4 py-2 font-medium text-white hover:bg-emerald-600 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            Tải lên & trích xuất
          </button>
        </form>
      )}
    </section>
  );
}
