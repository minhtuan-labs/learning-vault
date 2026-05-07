import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAlerts, markAlertRead, markAllAlertsRead, deleteAlert } from "../api/alertsApi";
import { useAlerts } from "../contexts/AlertContext";

const SEVERITY_ICON = {
  high: "🔴",
  medium: "🟡",
  low: "🟢",
};

const SEVERITY_LABEL = {
  high: "Cao",
  medium: "Trung bình",
  low: "Thấp",
};

const ALERT_TYPE_LABEL = {
  revenue_drop: "Doanh thu giảm",
  negative_profit: "Lợi nhuận âm",
  debt_surge: "Nợ tăng đột biến",
  cost_anomaly: "Chi phí bất thường",
  npl_surge: "Nợ xấu tăng",
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("unread");
  const [companyFilter, setCompanyFilter] = useState("");
  const { refreshAlerts } = useAlerts();

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filter === "unread") {
        params.is_read = false;
      }
      if (companyFilter && companyFilter !== "") {
        params.company_id = companyFilter;
      }
      console.log('Fetching alerts with params:', params);
      const data = await getAlerts(params);
      console.log('Alerts data:', data);
      setAlerts(data);
    } catch (err) {
      console.error('Error fetching alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [filter, companyFilter]);

  const handleMarkRead = async (alertId) => {
    try {
      await markAlertRead(alertId);
      fetchAlerts();
      refreshAlerts();
    } catch (err) {
      console.error('Error marking alert as read:', err);
    }
  };

  const handleDelete = async (alertId) => {
    try {
      await deleteAlert(alertId);
      fetchAlerts();
      refreshAlerts();
    } catch (err) {
      console.error('Error deleting alert:', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllAlertsRead();
      fetchAlerts();
      refreshAlerts();
    } catch (err) {
      console.error('Error marking all as read:', err);
    }
  };

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Cảnh báo tự động</h1>
        <button
          onClick={handleMarkAllRead}
          className="rounded-md bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-200"
        >
          Đánh dấu tất cả đã đọc
        </button>
      </div>

      <div className="flex gap-4 rounded-xl bg-white p-4 shadow-sm">
        <button
          onClick={() => setFilter("all")}
          className={`rounded-md px-3 py-1.5 text-sm font-medium ${
            filter === "all"
              ? "bg-blue-100 text-blue-700"
              : "bg-slate-100 text-slate-600 hover:bg-slate-200"
          }`}
        >
          Tất cả
        </button>
        <button
          onClick={() => setFilter("unread")}
          className={`rounded-md px-3 py-1.5 text-sm font-medium ${
            filter === "unread"
              ? "bg-blue-100 text-blue-700"
              : "bg-slate-100 text-slate-600 hover:bg-slate-200"
          }`}
        >
          Chưa đọc
        </button>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-200" />
          ))}
        </div>
      ) : alerts.length === 0 ? (
        <div className="rounded-xl bg-white p-8 text-center shadow-sm">
          <p className="text-slate-500">Không có cảnh báo nào</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`rounded-xl border p-4 shadow-sm ${
                alert.is_read ? "bg-white" : "bg-red-50"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-lg">⚪</span>
                  <div>
                    <Link
                      to={`/companies/${alert.company_id}`}
                      className="font-semibold text-blue-600 hover:underline"
                    >
                      {alert.company_code}
                    </Link>
                    <span className="ml-2 text-sm text-slate-500">
                      {ALERT_TYPE_LABEL[alert.alert_type] || alert.alert_type}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                    {SEVERITY_LABEL[alert.severity]}
                  </span>
                  {!alert.is_read && (
                    <button
                      onClick={() => handleMarkRead(alert.id)}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      Đã đọc
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(alert.id)}
                    className="text-xs text-red-600 hover:underline"
                  >
                    Xóa
                  </button>
                </div>
              </div>
              <p className="mt-2 text-sm text-slate-700">{alert.description}</p>
              <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
                <span>{alert.period_label}</span>
                <span>{new Date(alert.created_at).toLocaleString("vi-VN")}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
