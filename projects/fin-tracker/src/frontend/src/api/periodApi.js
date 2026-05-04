import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({ baseURL, timeout: 30000 });
const longApi = axios.create({ baseURL, timeout: 600000 });

export const createFinancialPeriod = async (companyId, payload) => {
  const { data } = await api.post(`/api/companies/${companyId}/periods`, payload);
  return data;
};

export const listFinancialPeriods = async (companyId) => {
  const { data } = await api.get(`/api/companies/${companyId}/periods`);
  return data;
};

export const listPeriodFiles = async (periodId) => {
  const { data } = await api.get(`/api/periods/${periodId}/files`);
  return data;
};

export const uploadPeriodPdf = async (periodId, file, reportType, onUploadProgress) => {
  const form = new FormData();
  form.append("file", file);
  form.append("report_type", reportType);
  const { data } = await api.post(`/api/periods/${periodId}/upload`, form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress,
  });
  return data;
};

export const extractPeriodData = async (periodId, body = {}) => {
  const { data } = await longApi.post(`/api/periods/${periodId}/extract`, body);
  return data;
};

export const listFinancialData = async (periodId) => {
  const { data } = await api.get(`/api/periods/${periodId}/data`);
  return data;
};

export const updateFinancialMetric = async (periodId, metricId, payload) => {
  const { data } = await api.put(`/api/periods/${periodId}/data/${metricId}`, payload);
  return data;
};

export const verifyPeriodData = async (periodId) => {
  const { data } = await api.post(`/api/periods/${periodId}/verify`);
  return data;
};

export const pdfFileUrl = (periodId, fileId) =>
  `${baseURL}/api/periods/${periodId}/files/${fileId}`;

export const deletePeriodFile = async (periodId, fileId) => {
  await api.delete(`/api/periods/${periodId}/files/${fileId}`);
};

export const deleteFinancialPeriod = async (companyId, periodId) => {
  await api.delete(`/api/companies/${companyId}/periods/${periodId}`);
};
