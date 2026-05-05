import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
// Using dangerouslySetInnerHTML to render HTML from backend (markdown converted to HTML with table support)
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getCompanyAnalytics } from "../api/analyticsApi";
import { getCompanyAnalysis, triggerAnalysis } from "../api/analysisApi";
import { generateCompanySummary, getCompanySummary } from "../api/summaryApi";

const COLOR_BLUE = "#3b82f6";
const COLOR_GREEN = "#10b981";
const COLOR_ORANGE = "#f59e0b";

const QUARTERLY_RANGES = [
  { label: "Tất cả", value: null },
  { label: "4 quý gần nhất", value: 4 },
  { label: "8 quý gần nhất", value: 8 },
];

const YEARLY_RANGES = [
  { label: "Tất cả", value: null },
  { label: "5 năm gần nhất", value: 5 },
];

function SummaryCard({ summary, loading, generating, error, onGenerate }) {
  if (loading) {
    return (
      <div className="rounded-xl border border-blue-100 bg-white p-5 shadow-sm">
        <div className="h-5 w-48 animate-pulse rounded bg-slate-200" />
        <div className="mt-3 space-y-2">
          <div className="h-4 animate-pulse rounded bg-slate-100" />
          <div className="h-4 w-5/6 animate-pulse rounded bg-slate-100" />
          <div className="h-4 w-4/6 animate-pulse rounded bg-slate-100" />
        </div>
      </div>
    );
  }

  return (
      <div className="rounded-xl border border-blue-100 bg-blue-50 p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-sm font-semibold text-blue-900">Tóm tắt tình hình kinh doanh</h2>
          <button
            onClick={onGenerate}
            disabled={generating}
            className="flex items-center gap-1.5 rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {generating ? (
              <>
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                Đang tóm tắt...
              </>
            ) : summary ? (
              "Tóm tắt lại"
            ) : (
              "Tóm tắt"
            )}
          </button>
        </div>

        {error && (
          <p className="mt-3 text-sm text-red-600">{error}</p>
        )}

        {!summary && !generating && !error && (
          <p className="mt-3 text-sm text-blue-600">
            Nhấn <strong>Tóm tắt</strong> để AI phân tích và tóm tắt tình hình kinh doanh dựa trên toàn bộ dữ liệu tài chính hiện có.
          </p>
        )}

        {summary && !generating && (
          <div
            className="summary-content"
            dangerouslySetInnerHTML={{ __html: summary.summary_html }}
          />
        )}
      </div>
  );
}

function Breadcrumb({ companyId, name }) {
  return (
      <nav className="flex text-sm text-slate-500">
        <Link to="/" className="hover:text-slate-700">
          Trang chủ
        </Link>
        <span className="mx-2">›</span>
        <Link to="/companies" className="hover:text-slate-700">
          Danh sách DN
        </Link>
        {name && (
          <>
            <span className="mx-2">›</span>
            <Link to={`/companies/${companyId}`} className="text-blue-600 hover:underline">
              {name}
            </Link>
          </>
        )}
        <span className="mx-2">›</span>
        <span className="text-slate-800">Phân tích</span>
      </nav>
  );
}

const renderChartSection = (title, data, chartData, range, setRange, RANGES) => {
  const isBankLocal = data?.entity_type === "bank";
  const revLabel = isBankLocal ? "TOI" : "Doanh thu";
  return (
      <div className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
          <div className="flex gap-2">
            {RANGES.map((r) => (
              <button
                key={r.label}
                onClick={() => setRange(r.value)}
                className={`rounded-md px-3 py-1.5 text-sm font-medium ${
                  (r.value === range || (r.value === null && range === null))
                    ? "bg-slate-900 text-white"
                    : "border border-slate-300 text-slate-700 hover:bg-slate-50"
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-800">{revLabel} & Lợi nhuận sau thuế (tỷ VND)</h3>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="label" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip formatter={(v) => v?.toLocaleString("vi-VN")} />
              <Legend />
              <Line type="monotone" dataKey="revenue" stroke={COLOR_BLUE} strokeWidth={2} dot={{ r: 4 }} name={revLabel} />
              <Line type="monotone" dataKey="profit" stroke={COLOR_GREEN} strokeWidth={2} dot={{ r: 4 }} name="Lợi nhuận sau thuế" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="mb-4 text-sm font-semibold text-slate-800">{revLabel} theo kỳ (tỷ VND)</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => v?.toLocaleString("vi-VN")} />
                <Bar dataKey="revenue" fill={COLOR_BLUE} radius={[4, 4, 0, 0]} name={revLabel} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="mb-4 text-sm font-semibold text-slate-800">Lợi nhuận theo kỳ (tỷ VND)</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => v?.toLocaleString("vi-VN")} />
                <Bar dataKey="profit" radius={[4, 4, 0, 0]} name="Lợi nhuận">
                  {chartData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.profit >= 0 ? COLOR_GREEN : "#ef4444"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-5 py-4">
            <h3 className="text-sm font-semibold text-slate-800">Chỉ số tài chính</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase text-slate-600">
                <tr>
                  <th className="px-5 py-3">Kỳ</th>
                  <th className="px-5 py-3 text-right">ROE (%)</th>
                  <th className="px-5 py-3 text-right">ROA (%)</th>
                  {isBankLocal ? (
                    <>
                      <th className="px-5 py-3 text-right">NIM (%)</th>
                      <th className="px-5 py-3 text-right">NPL (%)</th>
                      <th className="px-5 py-3 text-right">LDR (%)</th>
                      <th className="px-5 py-3 text-right">CASA (%)</th>
                      <th className="px-5 py-3 text-right">CAR (%)</th>
                    </>
                  ) : (
                    <>
                      <th className="px-5 py-3 text-right">Biên LN gộp (%)</th>
                      <th className="px-5 py-3 text-right">Nợ / Tài sản (%)</th>
                    </>
                  )}
                  <th className="px-5 py-3 text-right">Tổng tài sản (tỷ)</th>
                  <th className="px-5 py-3 text-right">Dòng tiền HĐKD (tỷ)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[...data.periods].reverse().map((p) => (
                  <tr key={p.label} className="hover:bg-slate-50">
                    <td className="px-5 py-3 font-medium text-slate-800">{p.label}</td>
                    <td className="px-5 py-3 text-right">{p.roe != null ? p.roe.toFixed(2) : "-"}</td>
                    <td className="px-5 py-3 text-right">{p.roa != null ? p.roa.toFixed(2) : "-"}</td>
                    {isBankLocal ? (
                      <>
                        <td className="px-5 py-3 text-right">{p.nim != null ? p.nim.toFixed(2) : "-"}</td>
                        <td className="px-5 py-3 text-right">{p.npl_ratio != null ? p.npl_ratio.toFixed(2) : "-"}</td>
                        <td className="px-5 py-3 text-right">{p.ldr != null ? p.ldr.toFixed(2) : "-"}</td>
                        <td className="px-5 py-3 text-right">{p.casa_ratio != null ? p.casa_ratio.toFixed(2) : "-"}</td>
                        <td className="px-5 py-3 text-right">{p.car != null ? p.car.toFixed(2) : "-"}</td>
                      </>
                    ) : (
                      <>
                        <td className="px-5 py-3 text-right">{p.gross_profit_margin != null ? p.gross_profit_margin.toFixed(2) : "-"}</td>
                        <td className="px-5 py-3 text-right">{p.debt_to_assets != null ? p.debt_to_assets.toFixed(2) : "-"}</td>
                      </>
                    )}
                    <td className="px-5 py-3 text-right">{p.total_assets != null ? p.total_assets.toLocaleString("vi-VN") : "-"}</td>
                    <td className="px-5 py-3 text-right">{p.operating_cash_flow != null ? p.operating_cash_flow.toLocaleString("vi-VN") : "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
  );
};

export default function CompanyAnalyticsPage() {
  const { companyId } = useParams();
  const [quarterlyData, setQuarterlyData] = useState(null);
  const [yearlyData, setYearlyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [quarterlyRange, setQuarterlyRange] = useState(null);
  const [yearlyRange, setYearlyRange] = useState(null);

  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [summaryGenerating, setSummaryGenerating] = useState(false);
  const [summaryError, setSummaryError] = useState("");

  const [analyses, setAnalyses] = useState([]);
  const [analysesLoading, setAnalysesLoading] = useState(true);
  const [analysesGenerating, setAnalysesGenerating] = useState(false);
  const [hasNewReports, setHasNewReports] = useState(false);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      setError("");
      try {
        const result = await getCompanyAnalytics(companyId, quarterlyRange, "Q");
        setQuarterlyData(result);
      } catch {
        setError("Không thể tải dữ liệu phân tích quý.");
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, [companyId, quarterlyRange]);

  useEffect(() => {
    const fetchYearly = async () => {
      try {
        const result = await getCompanyAnalytics(companyId, yearlyRange, "Y");
        setYearlyData(result);
      } catch {
        setError("Không thể tải dữ liệu phân tích năm.");
      }
    };
    fetchYearly();
  }, [companyId, yearlyRange]);

  useEffect(() => {
    const fetchSummary = async () => {
      setSummaryLoading(true);
      try {
        const result = await getCompanySummary(companyId);
        setSummary(result.summary_text ? result : null);
      } catch {
        setSummary(null);
      } finally {
        setSummaryLoading(false);
      }
    };
    fetchSummary();
  }, [companyId]);

  useEffect(() => {
    const fetchAnalyses = async () => {
      setAnalysesLoading(true);
      try {
        const result = await getCompanyAnalysis(companyId);
        setAnalyses(result);
        // Check if there are new reports that need analysis
        const [quarterlyResult, yearlyResult] = await Promise.all([
          getCompanyAnalytics(companyId, null, "Q"),
          getCompanyAnalytics(companyId, null, "Y"),
        ]);
        const allPeriods = [
          ...(quarterlyResult?.periods || []),
          ...(yearlyResult?.periods || []),
        ];
        const analyzedPeriodIds = result.map((a) => a.period_id);
        const hasUnanalyzed = allPeriods.some((p) => !analyzedPeriodIds.includes(p.period_id));
        setHasNewReports(hasUnanalyzed && result.length > 0);
      } catch {
        setAnalyses([]);
      } finally {
        setAnalysesLoading(false);
      }
    };
    fetchAnalyses();
  }, [companyId]);

  const handleGenerateSummary = async () => {
    setSummaryGenerating(true);
    setSummaryError("");
    try {
      const result = await generateCompanySummary(companyId);
      setSummary(result);
    } catch (err) {
      const msg = err?.response?.data?.detail || "Không thể tạo tóm tắt. Vui lòng thử lại.";
      setSummaryError(msg);
    } finally {
      setSummaryGenerating(false);
    }
  };

  const handleTriggerAnalysis = async (periodId) => {
    setAnalysesGenerating(true);
    try {
      await triggerAnalysis(periodId);
      const result = await getCompanyAnalysis(companyId);
      setAnalyses(result);
      setHasNewReports(false);
    } catch {
      // ignore
    } finally {
      setAnalysesGenerating(false);
    }
  };

  const checkNewReports = async () => {
    try {
      const [quarterlyResult, yearlyResult] = await Promise.all([
        getCompanyAnalytics(companyId, null, "Q"),
        getCompanyAnalytics(companyId, null, "Y"),
      ]);
      const allPeriods = [
        ...(quarterlyResult?.periods || []),
        ...(yearlyResult?.periods || []),
      ];
      const analyzedPeriodIds = analyses.map((a) => a.period_id);
      const hasUnanalyzed = allPeriods.some((p) => !analyzedPeriodIds.includes(p.period_id));
      setHasNewReports(hasUnanalyzed && analyses.length > 0);
    } catch {
      // ignore
    }
  };

  if (loading) {
    return (
      <section className="space-y-6">
        <div className="h-8 w-64 animate-pulse rounded bg-slate-200" />
        <div className="h-80 animate-pulse rounded-xl bg-slate-200" />
        <div className="h-64 animate-pulse rounded-xl bg-slate-200" />
      </section>
    );
  }

  if (error) {
    return <p className="text-sm text-red-600">{error}</p>;
  }

  const quarterlyChartData = quarterlyData?.periods?.map((p) => ({
    label: p.label,
    revenue: p.revenue ?? 0,
    profit: p.profit_after_tax ?? 0,
    ocf: p.operating_cash_flow ?? 0,
  })) || [];

  const yearlyChartData = yearlyData?.periods?.map((p) => ({
    label: p.label,
    revenue: p.revenue ?? 0,
    profit: p.profit_after_tax ?? 0,
    ocf: p.operating_cash_flow ?? 0,
  })) || [];

  return (
    <section className="space-y-8">
      <Breadcrumb companyId={companyId} name={quarterlyData?.company_name || yearlyData?.company_name} />

      {/* Business Summary */}
      <SummaryCard
        summary={summary}
        loading={summaryLoading}
        generating={summaryGenerating}
        error={summaryError}
        onGenerate={handleGenerateSummary}
      />

      {/* Quarterly Charts */}
      {quarterlyData && renderChartSection("Biểu đồ quý", quarterlyData, quarterlyChartData, quarterlyRange, setQuarterlyRange, QUARTERLY_RANGES)}

      {/* Yearly Charts */}
      {yearlyData && renderChartSection("Biểu đồ năm", yearlyData, yearlyChartData, yearlyRange, setYearlyRange, YEARLY_RANGES)}

      {/* AI Analysis */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Nhận xét AI</h2>
          {hasNewReports && (
            <button
              onClick={() => {
                const latestPeriod = [...(quarterlyData?.periods || []), ...(yearlyData?.periods || [])]
                  .sort((a, b) => b.period_id - a.period_id)[0];
                if (latestPeriod) handleTriggerAnalysis(latestPeriod.period_id);
              }}
              disabled={analysesGenerating}
              className="flex items-center gap-1.5 rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {analysesGenerating ? (
                <>
                  <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0c4.418 0 8 3.582 8 8h-4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Đang phân tích...
                </>
              ) : (
                "Phân tích ngay"
              )}
            </button>
          )}
        </div>

        {hasNewReports && analyses.length > 0 && (
          <div className="rounded-lg bg-yellow-50 p-3 text-sm text-yellow-800">
            Có báo cáo mới đã upload. Nhấn "Phân tích ngay" để cập nhật nhận xét AI.
          </div>
        )}

        {analysesLoading ? (
          <div className="space-y-3">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="h-32 animate-pulse rounded-xl bg-slate-200" />
            ))}
          </div>
        ) : analyses.length === 0 ? (
          <div className="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm">
            <p className="text-sm text-slate-500">Chưa có nhận xét AI nào.</p>
            {hasNewReports && (
              <p className="mt-2 text-xs text-slate-400">Có báo cáo mới - hãy nhấn "Phân tích ngay" để tạo nhận xét.</p>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {analyses.map((analysis) => (
              <details
                key={analysis.id}
                className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm"
              >
                <summary className="flex cursor-pointer items-center justify-between px-5 py-4 hover:bg-slate-50">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-slate-900">
                      {analysis.period_label}
                    </span>
                    <span className="text-xs text-slate-400">
                      {new Date(analysis.created_at).toLocaleString("vi-VN")}
                    </span>
                  </div>
                  <span className="text-xs text-slate-400">Click để xem</span>
                </summary>
                <div className="border-t border-slate-200 px-5 py-4">
                  <div
                    className="summary-content"
                    dangerouslySetInnerHTML={{ __html: analysis.analysis_html || analysis.analysis_text }}
                  />
                </div>
              </details>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
