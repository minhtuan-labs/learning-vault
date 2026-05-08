import apiClient from "./client";

export async function getAlerts(params = {}) {
  const { data } = await apiClient.get("/api/alerts", { params });
  return data;
}

export async function markAlertRead(alertId) {
  const { data } = await apiClient.put(`/api/alerts/${alertId}/read`);
  return data;
}

export async function deleteAlert(alertId) {
  const { data } = await apiClient.delete(`/api/alerts/${alertId}`);
  return data;
}

export async function markAllAlertsRead(companyId = null) {
  const params = companyId ? { company_id: companyId } : {};
  const { data } = await apiClient.put("/api/alerts/read-all", null, { params });
  return data;
}