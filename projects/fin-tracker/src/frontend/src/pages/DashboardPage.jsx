import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { getDashboardOverview } from "../api/dashboardApi";
import { useAlerts } from "../contexts/AlertContext";

const COLOR_BLUE = "#3b82f6";
const COLOR_GREEN = "#10b981";
const COLOR_RED = "#ef4444";
const COLOR_ORANGE = "#f59e0b";
const COLOR_GRAY = "#64748b";

function KpiCard({ label, value, icon }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500">{label}</p>
          <p className="mt-1 text-2xl font-bold text-slate-900">{value}</p>
        </div>
        <span className="text-2xl">{icon}</span>
      </div>
    </div>
  );
}

function formatBillion(val) {
  if (val == null) return "-";
  return `${val.toLocaleString("vi-VN")}`;
}

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { refreshKey } = useAlerts();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError("");
      try {
        const result = await getDashboardOverview();
        setData(result);
      } catch (err) {
        console.error("Dashboard error:", err);
        setError("Không thể tải dữ liệu dashboard.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [refreshKey]);

  if (loading) {
    return (
      <section className="space-y-6">
        <h1 className="text-2xl font-semibold text-slate-900">Dashboard tổng quan</h1>
        <div className="grid gap-4 md:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-200" />
          ))}
        </div>
        <div className="h-80 animate-pulse rounded-xl bg-slate-200" />
      </section>
    );
  }

  if (error) {
    return <p className="text-sm text-red-600">{error}</p>;
  }

  if (!data || data.total_companies === 0) {
    return (
      <section className="space-y-6">
        <h1 className="text-2xl font-semibold text-slate-900">Dashboard tổng quan</h1>
        <div className="flex flex-col items-center justify-center rounded-xl bg-white py-16 shadow">
          <p className="text-lg text-slate-500">Chưa có dữ liệu</p>
          <p className="mt-2 text-sm text-slate-400">Hãy thêm doanh nghiệp và upload BCTC để bắt đầu.</p>
          <Link
            to="/companies"
            className="mt-4 rounded-md bg-emerald-500 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-600"
          >
            Thêm doanh nghiệp
          </Link>
        </div>
      </section>
    );
  }

  const top5 = data.top_revenue_companies || [];
  const recentAlerts = data.recent_alerts || [];
  const hasBank = top5.some((c) => c.entity_type === "bank");
  const revenueLabel = hasBank ? "TOI (tỷ)" : "Doanh thu (tỷ)";
  const chartData = top5
    .filter((c) => c.revenue != null)
    .map((c) => ({
      name: c.code,
      revenue: c.revenue,
      profit: c.profit,
      isBank: c.entity_type === "bank",
    }))
    .reverse();
  const barRevenueName = hasBank ? "TOI" : "Doanh thu";

  const SEVERITY_ICON = {
    high: "🔴",
    medium: "🟡",
    low: "🟢",
  };

  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-900">Dashboard tổng quan</h1>

      <div className="grid gap-4 md:grid-cols-4">
        <KpiCard label="Tổng doanh nghiệp" value={data.total_companies} icon="🏢" />
        <KpiCard label="DN có BCTC" value={data.companies_with_reports} icon="📊" />
        <KpiCard
          label="Cảnh báo chưa xử lý"
          value={data.total_warnings > 0 ? `${data.total_warnings} 🔴` : "0"}
          icon="⚠️"
        />
        <KpiCard label="Kỳ gần nhất" value={data.latest_period_label} icon="📅" />
      </div>

      {top5.length > 0 && (
        <>
          <div className="overflow-hidden rounded-xl bg-white shadow">
            <div className="border-b border-slate-200 px-5 py-4">
              <h2 className="text-lg font-semibold text-slate-900">Top doanh thu năm gần nhất ({data.latest_period_label})</h2>
            </div>
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase text-slate-600">
                <tr>
                  <th className="px-5 py-3">Mã CK</th>
                  <th className="px-5 py-3">Doanh nghiệp</th>
                  <th className="px-5 py-3 text-right">{revenueLabel}</th>
                  <th className="px-5 py-3 text-right">Lợi nhuận (tỷ)</th>
                  <th className="px-5 py-3 text-right">Tăng trưởng DT</th>
                  <th className="px-5 py-3 text-right">Tăng trưởng LN</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {top5.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-50">
                    <td className="px-5 py-3">
                      <Link to={`/companies/${c.id}`} className="font-semibold text-blue-600 hover:underline">
                        {c.code}
                      </Link>
                    </td>
                    <td className="px-5 py-3 text-slate-700">{c.name}</td>
                    <td className="px-5 py-3 text-right font-medium text-slate-800">
                      {formatBillion(c.revenue)}
                    </td>
                    <td className="px-5 py-3 text-right font-medium text-slate-800">
                      {formatBillion(c.profit)}
                    </td>
                    <td className="px-5 py-3 text-right font-medium">
                      {c.revenue_growth != null ? (
                        <span className={c.revenue_growth >= 0 ? "text-green-600" : "text-red-600"}>
                          {c.revenue_growth >= 0 ? "+" : ""}
                          {c.revenue_growth.toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                    <td className="px-5 py-3 text-right font-medium">
                      {c.profit_growth != null ? (
                        <span className={c.profit_growth >= 0 ? "text-green-600" : "text-red-600"}>
                          {c.profit_growth >= 0 ? "+" : ""}
                          {c.profit_growth.toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="mb-4 text-sm font-semibold text-slate-800">So sánh doanh thu top 5 DN</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `${v}`} />
                  <Tooltip formatter={(v) => `${v?.toLocaleString("vi-VN")}`} />
                  <Bar dataKey="revenue" fill={COLOR_BLUE} radius={[4, 4, 0, 0]} name={barRevenueName} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="mb-4 text-sm font-semibold text-slate-800">So sánh lợi nhuận top 5 DN</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(v) => `${v?.toLocaleString("vi-VN")}`} />
                  <Bar dataKey="profit" radius={[4, 4, 0, 0]} name="Lợi nhuận">
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={(entry.profit ?? 0) >= 0 ? COLOR_GREEN : COLOR_RED} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}

      {recentAlerts.length > 0 && (
        <div className="overflow-hidden rounded-xl bg-white shadow">
          <div className="border-b border-slate-200 px-5 py-4">
            <h2 className="text-lg font-semibold text-slate-900">Cảnh báo gần đây</h2>
          </div>
          <div className="divide-y divide-slate-100">
            {recentAlerts.map((alert) => (
              <Link
                key={alert.id}
                to={`/companies/${alert.company_id}`}
                className={`flex items-start gap-3 px-5 py-3 hover:bg-slate-50 ${alert.is_read ? "" : "bg-red-50"}`}
              >
                <span className="mt-0.5 text-sm">{SEVERITY_ICON[alert.severity] || "⚪"}</span>
                <div className="flex-1">
                  <p className="text-sm text-slate-700">
                    {alert.company_code && (
                      <span className="mr-1 font-medium text-slate-900">{alert.company_code}</span>
                    )}
                    {alert.description}
                  </p>
                  <p className="mt-1 text-xs text-slate-400">
                    {new Date(alert.created_at).toLocaleString("vi-VN")}
                  </p>
                </div>
              </Link>
            ))}
          </div>
          <div className="border-t border-slate-200 px-5 py-3 text-center">
            <Link to="/alerts" className="text-sm font-medium text-blue-600 hover:underline">
              Xem tất cả cảnh báo
            </Link>
          </div>
        </div>
      )}
    </section>
  );
}
