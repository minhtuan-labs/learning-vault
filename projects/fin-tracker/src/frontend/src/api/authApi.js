import apiClient from "./client";

export const login = async (username, password) => {
  const { data } = await apiClient.post("/api/auth/login", { username, password });
  return data;
};

export const register = async (username, password, displayName) => {
  const { data } = await apiClient.post("/api/auth/register", {
    username,
    password,
    display_name: displayName,
  });
  return data;
};

export const getMe = async () => {
  const { data } = await apiClient.get("/api/auth/me");
  return data;
};