'use client';

import Link from 'next/link';
import { useDashboard } from '@/lib/api-queries';
import { useAuthStore } from '@/lib/stores';

function centsToDisplay(cents: number): string {
  return (cents / 100).toFixed(2);
}

export default function DashboardPage() {
  const selectedFamilyId = useAuthStore((s) => s.selectedFamilyId);
  const { data, isLoading, isError } = useDashboard(selectedFamilyId ?? '', 'month');

  if (!selectedFamilyId) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-600 mb-4">No family selected.</p>
        <Link href="/family-selection" className="text-blue-600 hover:underline">
          Select a family
        </Link>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div>
        <h1 className="text-3xl font-bold mb-8 text-gray-900">Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white p-6 rounded-lg shadow animate-pulse">
              <div className="h-4 bg-gray-200 rounded mb-3 w-2/3" />
              <div className="h-8 bg-gray-200 rounded w-1/2" />
            </div>
          ))}
        </div>
        <div className="bg-white p-6 rounded-lg shadow animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4 w-1/4" />
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-4 bg-gray-200 rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div>
        <h1 className="text-3xl font-bold mb-8 text-gray-900">Dashboard</h1>
        <div className="bg-red-50 border border-red-200 text-red-700 p-6 rounded-lg">
          Failed to load dashboard data. The dashboard endpoint may not be available yet.
        </div>
      </div>
    );
  }

  const accountCount = data.accounts?.length ?? 0;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8 text-gray-900">Dashboard</h1>
      <p className="text-sm text-gray-500 mb-6">{data.period}</p>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-600 mb-2">Total Income</div>
          <div className="text-3xl font-bold text-green-600">
            ${centsToDisplay(data.total_income_cents)}
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-600 mb-2">Total Expenses</div>
          <div className="text-3xl font-bold text-red-600">
            ${centsToDisplay(data.total_expense_cents)}
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-600 mb-2">Net Savings</div>
          <div className="text-3xl font-bold text-blue-600">
            ${centsToDisplay(data.net_savings_cents)}
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-600 mb-2">Accounts</div>
          <div className="text-3xl font-bold text-gray-900">{accountCount}</div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4 text-gray-900">Recent Transactions</h2>
        {data.recent_transactions?.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No transactions yet. Start by creating an account and recording a transaction.
          </p>
        ) : (
          <ul className="divide-y divide-gray-100">
            {data.recent_transactions?.map((tx, idx) => (
              <li key={idx} className="flex items-center justify-between py-3">
                <div>
                  <span className="text-gray-800 font-medium">{tx.description || '—'}</span>
                  <span className="ml-3 text-sm text-gray-400">{tx.date}</span>
                </div>
                <span
                  className={`font-semibold ${
                    tx.direction === 'in' ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {tx.direction === 'in' ? '+' : '-'}${centsToDisplay(tx.amount_cents)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
