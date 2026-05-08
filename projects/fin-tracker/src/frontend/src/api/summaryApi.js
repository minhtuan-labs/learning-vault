import apiClient from "./client";

export const getCompanySummary = async (companyId) => {
  const { data } = await apiClient.get(`/api/companies/${companyId}/summary`);
  return data;
};

export const generateCompanySummary = async (companyId) => {
  const { data } = await apiClient.post(`/api/companies/${companyId}/summary`);
  return data;
};