import apiClient from "./client";

export const getUsers = async () => {
  const { data } = await apiClient.get("/api/users");
  return data;
};

export const approveUser = async (userId) => {
  const { data } = await apiClient.put(`/api/users/${userId}/approve`);
  return data;
};

export const deactivateUser = async (userId) => {
  const { data } = await apiClient.put(`/api/users/${userId}/deactivate`);
  return data;
};

export const updateUser = async (userId, payload) => {
  const { data } = await apiClient.put(`/api/users/${userId}`, payload);
  return data;
};

export const deleteUser = async (userId) => {
  await apiClient.delete(`/api/users/${userId}`);
};