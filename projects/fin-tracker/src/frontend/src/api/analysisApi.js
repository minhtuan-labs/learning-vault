import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  timeout: 10000,
});

export async function getCompanyAnalysis(companyId) {
  const res = await api.get(`/api/analysis/companies/${companyId}/analysis`);
  return res.data;
}

export async function triggerAnalysis(companyId) {
  const res = await api.post(`/api/analysis/companies/${companyId}/analyze`);
  return res.data;
}

export async function getAnalysisStatus(companyId) {
  const res = await api.get(`/api/analysis/companies/${companyId}/analysis`);
  return res.data?.[0]?.status || null;
}
