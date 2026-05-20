'use client';

export default function AnalyticsPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-8 text-gray-900">Analytics</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4 text-gray-900">
            Expense Breakdown
          </h2>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
            <p className="text-gray-500">Chart placeholder</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4 text-gray-900">
            Income vs Expenses
          </h2>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
            <p className="text-gray-500">Chart placeholder</p>
          </div>
        </div>
      </div>

      <div className="mt-6 bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-4 text-gray-900">
          Category Breakdown
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">
                  Category
                </th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">
                  Amount
                </th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">
                  Percentage
                </th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td colSpan={3} className="py-8 text-center text-gray-500">
                  No data available
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
