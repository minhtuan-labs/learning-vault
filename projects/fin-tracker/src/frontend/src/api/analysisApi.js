import apiClient from "./client";

export async function getCompanyAnalysis(companyId) {
  const { data } = await apiClient.get(`/api/analysis/companies/${companyId}/analysis`);
  return data;
}

export async function triggerAnalysis(companyId) {
  const { data } = await apiClient.post(`/api/analysis/companies/${companyId}/analyze`);
  return data;
}

export async function getAnalysisStatus(companyId) {
  const { data } = await apiClient.get(`/api/analysis/companies/${companyId}/analysis`);
  return data?.[0]?.status || null;
}