import apiClient from "./client";

const longTimeout = { timeout: 600000 };

export const createFinancialPeriod = async (companyId, payload) => {
  const { data } = await apiClient.post(`/api/companies/${companyId}/periods`, payload);
  return data;
};

export const listFinancialPeriods = async (companyId) => {
  const { data } = await apiClient.get(`/api/companies/${companyId}/periods`);
  return data;
};

export const listPeriodFiles = async (periodId) => {
  const { data } = await apiClient.get(`/api/periods/${periodId}/files`);
  return data;
};

export const uploadPeriodPdf = async (periodId, file, reportType, onUploadProgress) => {
  const form = new FormData();
  form.append("file", file);
  form.append("report_type", reportType);
  const { data } = await apiClient.post(`/api/periods/${periodId}/upload`, form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress,
  });
  return data;
};

export const extractPeriodData = async (periodId, body = {}) => {
  const { data } = await apiClient.post(`/api/periods/${periodId}/extract`, body, longTimeout);
  return data;
};

export const listFinancialData = async (periodId) => {
  const { data } = await apiClient.get(`/api/periods/${periodId}/data`);
  return data;
};

export const updateFinancialMetric = async (periodId, metricId, payload) => {
  const { data } = await apiClient.put(`/api/periods/${periodId}/data/${metricId}`, payload);
  return data;
};

export const verifyPeriodData = async (periodId) => {
  const { data } = await apiClient.post(`/api/periods/${periodId}/verify`);
  return data;
};

export const fetchPdfBlob = async (periodId, fileId) => {
  const { data } = await apiClient.get(`/api/periods/${periodId}/files/${fileId}`, {
    responseType: "blob",
  });
  return URL.createObjectURL(data);
};

export const deletePeriodFile = async (periodId, fileId) => {
  await apiClient.delete(`/api/periods/${periodId}/files/${fileId}`);
};

export const deleteFinancialPeriod = async (companyId, periodId) => {
  await apiClient.delete(`/api/companies/${companyId}/periods/${periodId}`);
};