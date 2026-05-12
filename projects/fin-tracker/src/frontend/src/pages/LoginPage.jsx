import { useState } from "react";
import { useNavigate } from "react-router-dom";

import apiClient from "../api/client";
import { login as loginApi, register as registerApi } from "../api/authApi";
import { useAuth } from "../contexts/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      if (isRegister) {
        await registerApi(username, password, displayName || null);
        setPendingApproval(true);
        return;
      }
      const tokenData = await loginApi(username, password);
      const { data: user } = await apiClient.get("/api/auth/me", {
        headers: { Authorization: `Bearer ${tokenData.access_token}` },
      });
      login(tokenData.access_token, user);
      navigate("/dashboard");
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (err?.response?.status === 403) {
        setError(detail || "Tài khoản chưa được phê duyệt hoặc đã bị vô hiệu hóa.");
      } else {
        setError(detail || (isRegister ? "Không thể tạo tài khoản." : "Tên đăng nhập hoặc mật khẩu không đúng."));
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-900">
      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-2xl">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-slate-900">fin-tracker</h1>
          <p className="mt-1 text-sm text-slate-500">Quản lý báo cáo tài chính doanh nghiệp</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Tên đăng nhập</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          {isRegister && (
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Tên hiển thị</label>
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
              />
            </div>
          )}

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Mật khẩu</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete={isRegister ? "new-password" : "current-password"}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          {pendingApproval && (
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3">
              <p className="text-sm text-emerald-800">
                Đăng ký thành công! Tài khoản của bạn đang chờ quản trị viên phê duyệt. Vui lòng đăng nhập lại sau khi được duyệt.
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
          >
            {submitting ? "Đang xử lý..." : isRegister ? "Tạo tài khoản" : "Đăng nhập"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-500">
          {isRegister ? "Đã có tài khoản?" : "Chưa có tài khoản?"}{" "}
          <button
            type="button"
            onClick={() => { setIsRegister(!isRegister); setError(""); }}
            className="font-medium text-emerald-600 hover:underline"
          >
            {isRegister ? "Đăng nhập" : "Tạo tài khoản"}
          </button>
        </p>
      </div>
    </div>
  );
}