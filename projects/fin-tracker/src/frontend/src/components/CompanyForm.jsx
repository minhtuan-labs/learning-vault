import { useMemo, useState } from "react";

import { EXCHANGES } from "../constants/exchanges";

const defaultForm = {
  code: "",
  name: "",
  exchange: "HOSE",
  industry: "",
  website: "",
  description: "",
};

export default function CompanyForm({ initialData, onSubmit, submitLabel = "Lưu" }) {
  const normalizedData = useMemo(() => {
    if (!initialData) {
      return defaultForm;
    }

    return {
      code: initialData.code || "",
      name: initialData.name || "",
      exchange: initialData.exchange || "HOSE",
      industry: initialData.industry || "",
      website: initialData.website || "",
      description: initialData.description || "",
    };
  }, [initialData]);

  const [formData, setFormData] = useState(normalizedData);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await onSubmit({
        ...formData,
        code: formData.code.trim().toUpperCase(),
        name: formData.name.trim(),
        industry: formData.industry.trim() || null,
        website: formData.website.trim() || null,
        description: formData.description.trim() || null,
      });
    } catch (submitError) {
      setError(
        submitError?.response?.data?.detail ||
          "Có lỗi xảy ra. Vui lòng kiểm tra dữ liệu và thử lại."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-xl bg-white p-6 shadow">
      <h2 className="text-xl font-semibold text-slate-800">Thông tin doanh nghiệp</h2>

      {error ? (
        <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2">
        <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
          Mã chứng khoán *
          <input
            name="code"
            value={formData.code}
            onChange={handleChange}
            required
            maxLength={20}
            className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500"
          />
        </label>

        <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
          Tên doanh nghiệp *
          <input
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500"
          />
        </label>

        <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
          Sàn giao dịch *
          <select
            name="exchange"
            value={formData.exchange}
            onChange={handleChange}
            className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500"
          >
            {EXCHANGES.map((exchange) => (
              <option key={exchange} value={exchange}>
                {exchange}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
          Ngành
          <input
            name="industry"
            value={formData.industry}
            onChange={handleChange}
            className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500"
          />
        </label>
      </div>

      <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
        Website
        <input
          name="website"
          value={formData.website}
          onChange={handleChange}
          placeholder="https://example.com"
          className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500"
        />
      </label>

      <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
        Mô tả
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={4}
          className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500"
        />
      </label>

      <button
        type="submit"
        disabled={isSubmitting}
        className="rounded-md bg-emerald-500 px-4 py-2 font-medium text-white hover:bg-emerald-600 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {isSubmitting ? "Đang lưu..." : submitLabel}
      </button>
    </form>
  );
}
