import { useEffect, useState } from "react";

import { getSettings, updateSetting } from "../api/settingsApi";

export default function SettingsPage() {
  const [settings, setSettings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState({});

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
    </section>
  );
}