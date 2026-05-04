import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 30000,
});

export const getCompanyAnalytics = async (companyId, periods = null) => {
  const params = {};
  if (periods) params.periods = periods;
  const { data } = await api.get(`/api/analytics/companies/${companyId}`, { params });
  return data;
};

export const compareCompanies = async (ids, year, quarter = null) => {
  const params = { ids: ids.join(","), year };
  if (quarter) params.quarter = quarter;
  const { data } = await api.get("/api/analytics/compare", { params });
  return data;
};
