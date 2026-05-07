import { useState, useEffect, useRef, useCallback } from "react";
import { Link } from "react-router-dom";
import { getAlerts, markAlertRead } from "../api/alertsApi";
import { useAlerts } from "../contexts/AlertContext";

const SEVERITY_ICON = {
  high: "🔴",
  medium: "🟡",
  low: "🟢",
};

const SEVERITY_BG = {
  high: "bg-red-50",
  medium: "bg-yellow-50",
  low: "bg-green-50",
};

export default function AlertDropdown() {
  const [open, setOpen] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);
  const { unreadCount, setUnreadCount, refreshAlerts } = useAlerts();

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getAlerts({ is_read: false, limit: 5 });
      setAlerts(data);
      setUnreadCount(data.length);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, [setUnreadCount]);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchAlerts]);

  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleMarkRead = async (e, alertId) => {
    e.stopPropagation();
    try {
      await markAlertRead(alertId);
      fetchAlerts();
      refreshAlerts();
    } catch {
      // ignore
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setOpen(!open)}
        className="relative rounded-full p-2 text-slate-600 hover:bg-slate-100"
      >
        <span className="text-xl">🔔</span>
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs text-white">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-96 rounded-xl border border-slate-200 bg-white shadow-lg z-50">
          <div className="border-b border-slate-200 px-4 py-3">
            <h3 className="text-sm font-semibold text-slate-900">Cảnh báo gần đây</h3>
          </div>

          <div className="max-h-80 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-sm text-slate-500">Đang tải...</div>
            ) : alerts.length === 0 ? (
              <div className="p-4 text-center text-sm text-slate-500">Không có cảnh báo mới</div>
            ) : (
              alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`flex items-start gap-3 border-b border-slate-100 px-4 py-3 ${SEVERITY_BG[alert.severity] || ""}`}
                >
                  <span className="mt-0.5 text-sm">{SEVERITY_ICON[alert.severity] || "⚪"}</span>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <Link
                        to={`/companies/${alert.company_id}`}
                        className="text-sm font-medium text-blue-600 hover:underline"
                        onClick={() => setOpen(false)}
                      >
                        {alert.company_code}
                      </Link>
                      <button
                        onClick={(e) => handleMarkRead(e, alert.id)}
                        className="text-xs text-slate-400 hover:text-slate-600"
                      >
                        Đã đọc
                      </button>
                    </div>
                    <p className="mt-1 text-xs text-slate-600 line-clamp-2">{alert.description}</p>
                    <p className="mt-1 text-xs text-slate-400">
                      {new Date(alert.created_at).toLocaleString("vi-VN")}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="border-t border-slate-200 px-4 py-3">
            <Link
              to="/alerts"
              className="block text-center text-sm font-medium text-blue-600 hover:underline"
              onClick={() => setOpen(false)}
            >
              Xem tất cả
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
