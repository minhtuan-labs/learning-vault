import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
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

const COLOR_BLUE = "#3b82f6";
const COLOR_GREEN = "#10b981";
const COLOR_ORANGE = "#f59e0b";

const TIME_RANGES = [
  { label: "4 quý gần nhất", value: 4 },
  { label: "8 quý gần nhất", value: 8 },
  { label: "Tất cả", value: null },
];

export default function CompanyAnalyticsPage() {
  const { companyId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [timeRange, setTimeRange] = useState(4);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      setError("");
      try {
        const result = await getCompanyAnalytics(companyId, timeRange);
        setData(result);
      } catch {
        setError("Không thể tải dữ liệu phân tích.");
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [companyId, timeRange]);

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

  if (!data || data.periods.length === 0) {
    return (
      <section className="space-y-6">
        <Breadcrumb companyId={companyId} code={data?.company_code} name={data?.company_name} />
        <div className="flex flex-col items-center justify-center rounded-xl bg-white py-16 shadow">
          <p className="text-lg text-slate-500">Chưa có dữ liệu phân tích</p>
          <p className="mt-2 text-sm text-slate-400">Cần upload ít nhất 1 kỳ báo cáo đã trích xuất.</p>
          <Link
            to={`/companies/${companyId}/reports/upload`}
            className="mt-4 rounded-md bg-emerald-500 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-600"
          >
            Upload BCTC
          </Link>
        </div>
      </section>
    );
  }

  const chartData = data.periods.map((p) => ({
    label: p.label,
    revenue: p.revenue ?? 0,
    profit: p.profit_after_tax ?? 0,
    ocf: p.operating_cash_flow ?? 0,
  }));

  return (
    <section className="space-y-6">
      <Breadcrumb companyId={companyId} name={data.company_name} />

      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-900">Biểu đồ tài chính</h2>
        <div className="flex gap-2">
          {TIME_RANGES.map((r) => (
            <button
              key={r.label}
              onClick={() => setTimeRange(r.value)}
              className={`rounded-md px-3 py-1.5 text-sm font-medium ${
                (r.value === timeRange || (r.value === null && timeRange === null))
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
        <h3 className="mb-4 text-sm font-semibold text-slate-800">Doanh thu & Lợi nhuận sau thuế (tỷ VND)</h3>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="label" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip formatter={(v) => v?.toLocaleString("vi-VN")} />
            <Legend />
            <Line type="monotone" dataKey="revenue" stroke={COLOR_BLUE} strokeWidth={2} dot={{ r: 4 }} name="Doanh thu" />
            <Line type="monotone" dataKey="profit" stroke={COLOR_GREEN} strokeWidth={2} dot={{ r: 4 }} name="Lợi nhuận sau thuế" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-800">Doanh thu theo kỳ (tỷ VND)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="label" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v) => v?.toLocaleString("vi-VN")} />
              <Bar dataKey="revenue" fill={COLOR_BLUE} radius={[4, 4, 0, 0]} name="Doanh thu" />
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
                <th className="px-5 py-3 text-right">Biên LN gộp (%)</th>
                <th className="px-5 py-3 text-right">Nợ / Tài sản (%)</th>
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
                  <td className="px-5 py-3 text-right">{p.gross_profit_margin != null ? p.gross_profit_margin.toFixed(2) : "-"}</td>
                  <td className="px-5 py-3 text-right">{p.debt_to_assets != null ? p.debt_to_assets.toFixed(2) : "-"}</td>
                  <td className="px-5 py-3 text-right">{p.total_assets != null ? p.total_assets.toLocaleString("vi-VN") : "-"}</td>
                  <td className="px-5 py-3 text-right">{p.operating_cash_flow != null ? p.operating_cash_flow.toLocaleString("vi-VN") : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
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
