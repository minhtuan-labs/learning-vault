import { Link } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import AlertDropdown from "../components/AlertDropdown";

export default function MainLayout({ children }) {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-slate-900 text-white shadow">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-6">
            <Link to="/" className="text-lg font-semibold tracking-wide">
              fin-tracker
            </Link>
            <nav className="flex gap-4 text-sm">
              <Link to="/dashboard" className="hover:text-emerald-400">
                Dashboard
              </Link>
              <Link to="/companies" className="hover:text-emerald-400">
                Doanh nghiệp
              </Link>
              <Link to="/analytics/compare" className="hover:text-emerald-400">
                So sánh DN
              </Link>
              <Link to="/settings" className="hover:text-emerald-400">
                Cài đặt
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <AlertDropdown />
            <Link
              to="/companies/new"
              className="rounded-md bg-emerald-500 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-600"
            >
              Thêm doanh nghiệp
            </Link>
            <div className="flex items-center gap-3 border-l border-slate-600 pl-4">
              <span className="text-sm text-slate-300">{user?.display_name || user?.username}</span>
              <button
                onClick={logout}
                className="rounded-md px-3 py-2 text-sm text-slate-300 hover:bg-slate-700 hover:text-white"
              >
                Đăng xuất
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
    </div>
  );
}