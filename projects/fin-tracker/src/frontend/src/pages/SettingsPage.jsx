import { useEffect, useState } from "react";

import { getSettings, updateSetting } from "../api/settingsApi";
import { useAuth } from "../contexts/AuthContext";
import { approveUser, deactivateUser, deleteUser, getUsers, updateUser } from "../api/usersApi";

export default function SettingsPage() {
  const { user: currentUser, isAdmin } = useAuth();
  const [settings, setSettings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState({});

  const [users, setUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(false);
  const [usersError, setUsersError] = useState("");
  const [actionLoading, setActionLoading] = useState({});

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const data = await getSettings();
        setSettings(data);
      } catch {
        setError("Không thể tải cài đặt.");
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, []);

  useEffect(() => {
    if (!isAdmin) return;
    const fetchUsers = async () => {
      setUsersLoading(true);
      try {
        const data = await getUsers();
        setUsers(data);
      } catch {
        setUsersError("Không thể tải danh sách người dùng.");
      } finally {
        setUsersLoading(false);
      }
    };
    fetchUsers();
  }, [isAdmin]);

  const handleToggle = async (key, currentValue) => {
    const newValue = currentValue === "true" ? "false" : "true";
    setSaving((prev) => ({ ...prev, [key]: true }));
    setError("");
    try {
      const updated = await updateSetting(key, newValue);
      setSettings((prev) => prev.map((s) => (s.key === key ? updated : s)));
    } catch {
      setError("Không thể cập nhật cài đặt.");
    } finally {
      setSaving((prev) => ({ ...prev, [key]: false }));
    }
  };

  const refreshUsers = async () => {
    try {
      const data = await getUsers();
      setUsers(data);
    } catch {}
  };

  const handleApprove = async (userId) => {
    setActionLoading((prev) => ({ ...prev, [userId]: true }));
    setUsersError("");
    try {
      await approveUser(userId);
      await refreshUsers();
    } catch (err) {
      setUsersError(err?.response?.data?.detail || "Không thể phê duyệt người dùng.");
    } finally {
      setActionLoading((prev) => ({ ...prev, [userId]: false }));
    }
  };

  const handleDeactivate = async (userId) => {
    setActionLoading((prev) => ({ ...prev, [userId]: true }));
    setUsersError("");
    try {
      await deactivateUser(userId);
      await refreshUsers();
    } catch (err) {
      setUsersError(err?.response?.data?.detail || "Không thể vô hiệu hóa người dùng.");
    } finally {
      setActionLoading((prev) => ({ ...prev, [userId]: false }));
    }
  };

  const handleToggleAdmin = async (userId, isAdminVal) => {
    setActionLoading((prev) => ({ ...prev, [userId]: true }));
    setUsersError("");
    try {
      await updateUser(userId, { is_admin: !isAdminVal });
      await refreshUsers();
    } catch (err) {
      setUsersError(err?.response?.data?.detail || "Không thể cập nhật quyền.");
    } finally {
      setActionLoading((prev) => ({ ...prev, [userId]: false }));
    }
  };

  const handleDelete = async (userId) => {
    if (!window.confirm("Bạn có chắc muốn xoá người dùng này?")) return;
    setActionLoading((prev) => ({ ...prev, [userId]: true }));
    setUsersError("");
    try {
      await deleteUser(userId);
      await refreshUsers();
    } catch (err) {
      setUsersError(err?.response?.data?.detail || "Không thể xoá người dùng.");
    } finally {
      setActionLoading((prev) => ({ ...prev, [userId]: false }));
    }
  };

  if (loading) {
    return (
      <section className="space-y-6">
        <h1 className="text-2xl font-semibold text-slate-900">Cài đặt hệ thống</h1>
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-16 animate-pulse rounded-xl bg-slate-200" />
          ))}
        </div>
      </section>
    );
  }

  if (error && settings.length === 0) {
    return <p className="text-sm text-red-600">{error}</p>;
  }

  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-900">Cài đặt hệ thống</h1>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="space-y-4">
        {settings.map((s) => {
          const isEnabled = s.value === "true";
          const isSaving = saving[s.key];
          return (
            <div
              key={s.key}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-900">{s.label}</p>
                {s.description && (
                  <p className="mt-1 text-sm text-slate-500">{s.description}</p>
                )}
              </div>
              <button
                onClick={() => handleToggle(s.key, s.value)}
                disabled={isSaving}
                className={`relative ml-4 inline-flex h-6 w-11 flex-shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                  isEnabled ? "bg-emerald-500" : "bg-slate-300"
                } ${isSaving ? "opacity-50" : ""}`}
              >
                <span
                  className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    isEnabled ? "translate-x-5" : "translate-x-0"
                  }`}
                />
              </button>
            </div>
          );
        })}
      </div>

      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
        <p className="text-sm text-amber-800">
          <strong>Lưu ý:</strong> Tắt các chức năng AI sẽ giúp tiết kiệm chi phí gọi Anthropic API.
          Các tác vụ đã lên lịch sẽ không thực thi cho đến khi bật lại.
        </p>
      </div>

      {isAdmin && (
        <>
          <h2 className="mt-10 text-2xl font-semibold text-slate-900">Quản lý người dùng</h2>

          {usersError && <p className="text-sm text-red-600">{usersError}</p>}

          {usersLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-16 animate-pulse rounded-xl bg-slate-200" />
              ))}
            </div>
          ) : users.length === 0 ? (
            <p className="text-sm text-slate-500">Chưa có người dùng nào.</p>
          ) : (
            <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Tên đăng nhập</th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Hiển thị</th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Trạng thái</th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Quản trị</th>
                    <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Thao tác</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {users.map((u) => {
                    const isSelf = u.id === currentUser?.id;
                    const busy = actionLoading[u.id];
                    return (
                      <tr key={u.id} className="hover:bg-slate-50">
                        <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-slate-900">{u.username}</td>
                        <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">{u.display_name || "—"}</td>
                        <td className="whitespace-nowrap px-4 py-3 text-sm">
                          {u.is_active ? (
                            <span className="inline-flex rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-800">Hoạt động</span>
                          ) : (
                            <span className="inline-flex rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800">Chờ phê duyệt</span>
                          )}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 text-sm">
                          {u.is_admin ? (
                            <span className="inline-flex rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800">Quản trị</span>
                          ) : null}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 text-right text-sm">
                          {isSelf ? (
                            <span className="text-xs text-slate-400 italic">Bạn</span>
                          ) : (
                            <div className="flex items-center justify-end gap-2">
                              {!u.is_active && (
                                <button
                                  onClick={() => handleApprove(u.id)}
                                  disabled={busy}
                                  className="inline-block w-24 rounded-md bg-emerald-500 py-1 text-xs font-medium text-white hover:bg-emerald-600 disabled:opacity-50"
                                >
                                  Phê duyệt
                                </button>
                              )}
                              {u.is_active && (
                                <button
                                  onClick={() => handleDeactivate(u.id)}
                                  disabled={busy}
                                  className="inline-block w-24 rounded-md bg-amber-500 py-1 text-xs font-medium text-white hover:bg-amber-600 disabled:opacity-50"
                                >
                                  Vô hiệu
                                </button>
                              )}
                              <button
                                onClick={() => handleToggleAdmin(u.id, u.is_admin)}
                                disabled={busy}
                                className={`inline-block w-24 rounded-md py-1 text-xs font-medium text-white disabled:opacity-50 ${u.is_admin ? "bg-slate-500 hover:bg-slate-600" : "bg-blue-500 hover:bg-blue-600"}`}
                              >
                                {u.is_admin ? "Bỏ QTrị" : "Cấp QTrị"}
                              </button>
                              <button
                                onClick={() => handleDelete(u.id)}
                                disabled={busy}
                                className="inline-block w-24 rounded-md bg-red-500 py-1 text-xs font-medium text-white hover:bg-red-600 disabled:opacity-50"
                              >
                                Xoá
                              </button>
                            </div>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </section>
  );
}