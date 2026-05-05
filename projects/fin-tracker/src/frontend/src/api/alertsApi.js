import api from "./config";

export async function getAlerts(params = {}) {
  const res = await api.get("/alerts", { params });
  return res.data;
}

export async function markAlertRead(alertId) {
  const res = await api.put(`/alerts/${alertId}/read`);
  return res.data;
}

export async function markAllAlertsRead(companyId = null) {
  const params = companyId ? { company_id: companyId } : {};
  const res = await api.put("/alerts/read-all", null, { params });
  return res.data;
}

