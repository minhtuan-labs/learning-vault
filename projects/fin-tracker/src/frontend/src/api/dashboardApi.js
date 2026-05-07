import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  timeout: 30000,
});

export const getDashboardOverview = async () => {
  const { data } = await api.get("/api/dashboard/overview");
  return data;
};
