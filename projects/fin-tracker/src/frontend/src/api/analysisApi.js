import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 10000,
});

export async function getCompanyAnalysis(companyId) {
  const res = await api.get(`/analysis/companies/${companyId}/analysis`);
  return res.data;
}

export async function triggerAnalysis(periodId) {
  const res = await api.post(`/analysis/periods/${periodId}/analyze`);
  return res.data;
}
