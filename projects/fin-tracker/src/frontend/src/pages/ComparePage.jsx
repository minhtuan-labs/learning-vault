import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getCompanies } from "../api/companyApi";
import { compareCompanies } from "../api/analyticsApi";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b"];

export default function ComparePage() {
  const [companies, setCompanies] = useState([]);
  const [selected, setSelected] = useState([]);
  const [year, setYear] = useState(new Date().getFullYear());
  const [quarter, setQuarter] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    getCompanies().then(setCompanies).catch(() => {});
  }, []);

  const filtered = useMemo(() => {
    if (!search) return companies;
    const q = search.toLowerCase();
    return companies.filter((c) => c.code.toLowerCase().includes(q) || c.name.toLowerCase().includes(q));
  }, [companies, search]);

  const handleSelect = (company) => {
    if (selected.length >= 3) return;
    if (selected.some((s) => s.id === company.id)) return;
    setSelected([...selected, company]);
    setSearch("");
  };

  const handleRemove = (id) => {
    setSelected(selected.filter((s) => s.id !== id));
  };

  const handleCompare = async () => {
    if (selected.length < 2) {
      setError("Chọn ít nhất 2 doanh nghiệp để so sánh.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const result = await compareCompanies(
        selected.map((s) => s.id),
        year,
        quarter
      );
      setData(result);
    } catch {
      setError("Không thể tải dữ liệu so sánh.");
    } finally {
      setLoading(false);
    }
  };

  const radarData = useMemo(() => {
    if (!data || data.companies.length === 0) return [];
    const dims = [
      { key: "revenue", label: "Doanh thu" },
      { key: "profit_after_tax", label: "Lợi nhuận" },
      { key: "roe", label: "ROE" },
      { key: "roa", label: "ROA" },
      { key: "operating_cash_flow", label: "Dòng tiền" },
    ];
    return dims.map((d) => {
      const obj = { metric: d.label };
      data.companies.forEach((c, i) => {
        const val = c[d.key];
        obj[`company_${i}`] = val ?? 0;
      });
      return obj;
    });
  }, [data]);

  const barChartData = useMemo(() => {
    if (!data) return [];
    return data.companies.map((c, i) => ({
      name: c.code,
      revenue: c.revenue ?? 0,
      profit: c.profit_after_tax ?? 0,
      color: COLORS[i % COLORS.length],
    }));
  }, [data]);

  const periodLabel = data
    ? data.period_type === "Y"
      ? `Năm ${data.year}`
      : `Quý ${data.quarter}/${data.year}`
    : "";

  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-900">So sánh doanh nghiệp</h1>

      <div className="rounded-xl bg-white p-5 shadow">
        <div className="flex flex-wrap gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <input
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
              placeholder="Tìm doanh nghiệp theo tên hoặc mã CK"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-emerald-500"
            />
            {showDropdown && filtered.length > 0 && (
              <ul className="absolute z-10 mt-1 max-h-48 w-full overflow-auto rounded-md border border-slate-200 bg-white shadow-lg">
                {filtered.slice(0, 10).map((c) => (
                  <li
                    key={c.id}
                    onMouseDown={() => handleSelect(c)}
                    className="cursor-pointer px-3 py-2 text-sm hover:bg-slate-100"
                  >
                    <span className="font-semibold text-slate-800">{c.code}</span>{" "}
                    <span className="text-slate-500">{c.name}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <select
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-emerald-500"
          >
            {Array.from({ length: 10 }, (_, i) => new Date().getFullYear() - i).map((y) => (
              <option key={y} value={y}>
                Năm {y}
              </option>
            ))}
          </select>

          <select
            value={quarter ?? "0"}
            onChange={(e) => setQuarter(e.target.value === "0" ? null : Number(e.target.value))}
            className="rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-emerald-500"
          >
            <option value="0">Cả năm</option>
            {[1, 2, 3, 4].map((q) => (
              <option key={q} value={q}>
                Quý {q}
              </option>
            ))}
          </select>

          <button
            onClick={handleCompare}
            disabled={loading || selected.length < 2}
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {loading ? "Đang tải…" : "So sánh"}
          </button>
        </div>

        {selected.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {selected.map((c, i) => (
              <span
                key={c.id}
                className="inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium text-white"
                style={{ backgroundColor: COLORS[i % COLORS.length] }}
              >
                {c.code}
                <button
                  onClick={() => handleRemove(c.id)}
                  className="ml-1 rounded-full hover:opacity-80"
                >
                  ✕
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {!data && !loading && (
        <div className="flex flex-col items-center justify-center rounded-xl bg-white py-16 shadow">
          <p className="text-lg text-slate-500">Chọn ít nhất 2 doanh nghiệp và nhấn "So sánh"</p>
        </div>
      )}

      {loading && (
        <div className="space-y-4">
          <div className="h-64 animate-pulse rounded-xl bg-slate-200" />
          <div className="h-64 animate-pulse rounded-xl bg-slate-200" />
        </div>
      )}

      {data && !loading && data.companies.length > 0 && (
        <>
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 px-5 py-4">
              <h2 className="text-lg font-semibold text-slate-900">Bảng so sánh — {periodLabel}</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase text-slate-600">
                  <tr>
                    <th className="px-5 py-3">Chỉ số</th>
                    {data.companies.map((c, i) => (
                      <th key={c.id} className="px-5 py-3 text-right" style={{ color: COLORS[i % COLORS.length] }}>
                        <Link to={`/companies/${c.id}`} className="hover:underline">
                          {c.code}
                        </Link>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {[
                    { label: "Doanh thu (tỷ)", key: "revenue", fmt: "billion" },
                    { label: "Lợi nhuận sau thuế (tỷ)", key: "profit_after_tax", fmt: "billion" },
                    { label: "Dòng tiền HĐKD (tỷ)", key: "operating_cash_flow", fmt: "billion" },
                    { label: "Tổng tài sản (tỷ)", key: "total_assets", fmt: "billion" },
                    { label: "ROE (%)", key: "roe", fmt: "pct" },
                    { label: "ROA (%)", key: "roa", fmt: "pct" },
                    { label: "Biên LN gộp (%)", key: "gross_profit_margin", fmt: "pct" },
                    { label: "Nợ / Tài sản (%)", key: "debt_to_assets", fmt: "pct" },
                  ].map((row) => (
                    <tr key={row.key} className="hover:bg-slate-50">
                      <td className="px-5 py-3 font-medium text-slate-700">{row.label}</td>
                      {data.companies.map((c) => {
                        const val = c[row.key];
                        return (
                          <td key={c.id} className="px-5 py-3 text-right font-medium text-slate-800">
                            {val != null
                              ? row.fmt === "pct"
                                ? `${val.toFixed(2)}`
                                : val.toLocaleString("vi-VN")
                              : "-"}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="mb-4 text-sm font-semibold text-slate-800">Radar so sánh đa chiều</h3>
              <ResponsiveContainer width="100%" height={350}>
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="metric" tick={{ fontSize: 12 }} />
                  <Legend />
                  {data.companies.map((c, i) => (
                    <Radar
                      key={c.id}
                      name={c.code}
                      dataKey={`company_${i}`}
                      stroke={COLORS[i % COLORS.length]}
                      fill={COLORS[i % COLORS.length]}
                      fillOpacity={0.2}
                    />
                  ))}
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="mb-4 text-sm font-semibold text-slate-800">Doanh thu & Lợi nhuận (tỷ VND)</h3>
              <ResponsiveContainer width="100%" height={350}>
                <ComposedChart data={barChartData} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Legend />
                  <Tooltip formatter={(v) => v?.toLocaleString("vi-VN")} />
                  <Bar dataKey="revenue" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Doanh thu" />
                  <Bar dataKey="profit" radius={[4, 4, 0, 0]} name="Lợi nhuận">
                    {barChartData.map((entry, idx) => (
                      <Cell key={idx} fill={entry.profit >= 0 ? "#10b981" : "#ef4444"} />
                    ))}
                  </Bar>
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
