import apiClient from "./client";

export const getCompanies = async (params = {}) => {
  const { data } = await apiClient.get("/api/companies", { params });
  return data;
};

export const getCompanyById = async (id) => {
  const { data } = await apiClient.get(`/api/companies/${id}`);
  return data;
};

export const createCompany = async (payload) => {
  const { data } = await apiClient.post("/api/companies", payload);
  return data;
};

export const updateCompany = async (id, payload) => {
  const { data } = await apiClient.put(`/api/companies/${id}`, payload);
  return data;
};

export const deleteCompany = async (id) => {
  await apiClient.delete(`/api/companies/${id}`);
};