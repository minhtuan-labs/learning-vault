import api from "./config";

export async function getCompanyAnalysis(companyId) {
  const res = await api.get(`/companies/${companyId}/analysis`);
  return res.data;
}

export async function triggerAnalysis(periodId) {
  const res = await api.post(`/periods/${periodId}/analyze`);
  return res.data;
}
