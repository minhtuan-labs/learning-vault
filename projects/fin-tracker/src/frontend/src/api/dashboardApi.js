import apiClient from "./client";

export const getDashboardOverview = async () => {
  const { data } = await apiClient.get("/api/dashboard/overview");
  return data;
};