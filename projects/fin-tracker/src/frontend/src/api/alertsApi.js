import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  timeout: 10000,
});

export async function getAlerts(params = {}) {
  const res = await api.get("/api/alerts", { params });
  return res.data;
}

export async function markAlertRead(alertId) {
  const res = await api.put(`/api/alerts/${alertId}/read`);
  return res.data;
}

export async function deleteAlert(alertId) {
  const res = await api.delete(`/api/alerts/${alertId}`);
  return res.data;
}

export async function markAllAlertsRead(companyId = null) {
  const params = companyId ? { company_id: companyId } : {};
  const res = await api.put("/api/alerts/read-all", null, { params });
  return res.data;
}
