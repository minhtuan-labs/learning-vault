import apiClient from "./client";

export const getCompanyAnalytics = async (companyId, periods = null, periodType = null) => {
  const params = {};
  if (periods) params.periods = periods;
  if (periodType) params.period_type = periodType;
  const { data } = await apiClient.get(`/api/analytics/companies/${companyId}`, { params });
  return data;
};

export const compareCompanies = async (ids, year, quarter = null) => {
  const params = { ids: ids.join(","), year };
  if (quarter) params.quarter = quarter;
  const { data } = await apiClient.get("/api/analytics/compare", { params });
  return data;
};