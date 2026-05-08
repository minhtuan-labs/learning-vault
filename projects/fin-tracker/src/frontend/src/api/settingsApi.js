import apiClient from "./client";

export const getSettings = async () => {
  const { data } = await apiClient.get("/api/settings");
  return data;
};

export const updateSetting = async (key, value) => {
  const { data } = await apiClient.put(`/api/settings/${key}`, { value });
  return data;
};