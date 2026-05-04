import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { deleteCompany, getCompanies } from "../api/companyApi";
import { EXCHANGES } from "../constants/exchanges";

export default function CompanyListPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const filters = useMemo(
    () => ({
      search: searchParams.get("search") || "",
      exchange: searchParams.get("exchange") || "",
      industry: searchParams.get("industry") || "",
    }),
    [searchParams]
  );

  const fetchCompanies = async () => {
    setLoading(true);
    setError("");

    try {
      const data = await getCompanies({
        search: filters.search || undefined,
        exchange: filters.exchange || undefined,
        industry: filters.industry || undefined,
      });
      setCompanies(data);
    } catch (fetchError) {
      setError("Không thể tải danh sách doanh nghiệp.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanies();
  }, [filters.search, filters.exchange, filters.industry]);

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    const next = new URLSearchParams(searchParams);

    if (value) {
      next.set(name, value);
    } else {
      next.delete(name);
    }

    setSearchParams(next);
  };

  const handleDelete = async (id) => {
    const confirmed = window.confirm("Bạn có chắc muốn xoá doanh nghiệp này?");
    if (!confirmed) {
      return;
    }

    await deleteCompany(id);
    await fetchCompanies();
  };

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold text-slate-900">Danh sách doanh nghiệp</h1>

      <div className="grid gap-3 rounded-xl bg-white p-4 shadow md:grid-cols-3">
        <input
          name="search"
          value={filters.search}
          onChange={handleFilterChange}
          placeholder="Tìm theo mã hoặc tên"
          className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500"
        />

        <select
          name="exchange"
          value={filters.exchange}
          onChange={handleFilterChange}
          className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500"
        >
          <option value="">Tất cả sàn</option>
          {EXCHANGES.map((exchange) => (
            <option key={exchange} value={exchange}>
              {exchange}
            </option>
          ))}
        </select>

        <input
          name="industry"
          value={filters.industry}
          onChange={handleFilterChange}
          placeholder="Lọc theo ngành"
          className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500"
        />
      </div>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <div className="overflow-hidden rounded-xl bg-white shadow">
        {loading ? (
          <p className="p-4 text-sm text-slate-500">Đang tải dữ liệu...</p>
        ) : companies.length === 0 ? (
          <p className="p-4 text-sm text-slate-500">Chưa có doanh nghiệp phù hợp.</p>
        ) : (
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-100">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-600">Mã</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-600">Tên doanh nghiệp</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-600">Sàn</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-600">Ngành</th>
                <th className="px-4 py-3 text-right text-xs font-semibold uppercase text-slate-600">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {companies.map((company) => (
                <tr key={company.id}>
                  <td className="px-4 py-3 font-semibold text-slate-800">{company.code}</td>
                  <td className="px-4 py-3 text-slate-700">{company.name}</td>
                  <td className="px-4 py-3 text-slate-700">{company.exchange}</td>
                  <td className="px-4 py-3 text-slate-700">{company.industry || "-"}</td>
                  <td className="space-x-2 px-4 py-3 text-right">
                    <Link
                      className="text-sm font-medium text-blue-600 hover:underline"
                      to={`/companies/${company.id}`}
                    >
                      Chi tiết
                    </Link>
                    <Link
                      className="text-sm font-medium text-emerald-600 hover:underline"
                      to={`/companies/${company.id}/edit`}
                    >
                      Sửa
                    </Link>
                    <button
                      onClick={() => handleDelete(company.id)}
                      className="text-sm font-medium text-red-600 hover:underline"
                    >
                      Xoá
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
