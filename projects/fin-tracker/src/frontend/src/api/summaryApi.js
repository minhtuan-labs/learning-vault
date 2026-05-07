import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",  // Empty string for Vite proxy to work
  timeout: 60000 // summary generation can take longer than normal requests
});

export const getCompanySummary = async (companyId) => {
  const { data } = await api.get(`/api/companies/${companyId}/summary`);
  return data;
};

export const generateCompanySummary = async (companyId) => {
  const { data } = await api.post(`/api/companies/${companyId}/summary`);
  return data;
};
