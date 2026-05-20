'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  useAccounts,
  useTransactions,
  useCategories,
  useCreateTransactionMutation,
  useToggleTransactionMutation,
  useDeleteTransactionMutation,
} from '@/lib/api-queries';
import { useAuthStore } from '@/lib/stores';
import type { Account, Category, Transaction } from '@/lib/types';

const today = () => new Date().toISOString().slice(0, 10);

function NewTransactionForm({
  familyId,
  accountId,
  categories,
  onClose,
}: {
  familyId: string;
  accountId: string;
  categories: Category[];
  onClose: () => void;
}) {
  const [categoryId, setCategoryId] = useState(categories[0]?.id ?? '');
  const [amount, setAmount] = useState('');
  const [direction, setDirection] = useState<'in' | 'out'>('out');
  const [date, setDate] = useState(today());
  const [description, setDescription] = useState('');

  const createMutation = useCreateTransactionMutation(familyId, accountId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(
      {
        category_id: categoryId,
        amount_cents: Math.round(parseFloat(amount) * 100),
        direction,
        date,
        description: description || undefined,
      },
      { onSuccess: onClose }
    );
  };

  return (
    <tr>
      <td colSpan={5} className="py-4 px-4 bg-blue-50">
        <form onSubmit={handleSubmit} className="flex flex-wrap gap-3 items-end">
          <div className="flex flex-col gap-1">
            <label htmlFor="tx-category" className="text-xs text-gray-600">
              Category
            </label>
            <select
              id="tx-category"
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
              required
              className="border rounded px-2 py-1.5 text-sm"
            >
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="tx-amount" className="text-xs text-gray-600">
              Amount ($)
            </label>
            <input
              id="tx-amount"
              type="number"
              min="0.01"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00"
              required
              className="border rounded px-2 py-1.5 text-sm w-28"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="tx-direction" className="text-xs text-gray-600">
              Direction
            </label>
            <select
              id="tx-direction"
              value={direction}
              onChange={(e) => setDirection(e.target.value as 'in' | 'out')}
              className="border rounded px-2 py-1.5 text-sm"
            >
              <option value="in">In (+)</option>
              <option value="out">Out (-)</option>
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="tx-date" className="text-xs text-gray-600">
              Date
            </label>
            <input
              id="tx-date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
              className="border rounded px-2 py-1.5 text-sm"
            />
          </div>
          <div className="flex flex-col gap-1 flex-1 min-w-40">
            <label htmlFor="tx-desc" className="text-xs text-gray-600">
              Description (optional)
            </label>
            <input
              id="tx-desc"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add a note…"
              className="border rounded px-2 py-1.5 text-sm w-full"
            />
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={createMutation.isPending || !categoryId || !amount}
              className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Saving…' : 'Save'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="text-sm text-gray-500 hover:text-gray-700 px-2"
            >
              Cancel
            </button>
          </div>
          {createMutation.isError && (
            <p className="w-full text-xs text-red-600 mt-1">
              Failed to save transaction. Please try again.
            </p>
          )}
        </form>
      </td>
    </tr>
  );
}

function TransactionRow({
  tx,
  familyId,
  accountId,
  categories,
}: {
  tx: Transaction;
  familyId: string;
  accountId: string;
  categories: Category[];
}) {
  const toggleMutation = useToggleTransactionMutation(familyId, accountId);
  const deleteMutation = useDeleteTransactionMutation(familyId, accountId);

  const categoryName =
    tx.category_name ??
    categories.find((c) => c.id === tx.category_id)?.name ??
    tx.category_id;

  const isIn = tx.direction === 'in';
  const amountDisplay = (tx.amount_cents / 100).toFixed(2);

  const handleToggle = () => {
    toggleMutation.mutate({ txId: tx.id, is_enabled: !tx.is_enabled });
  };

  const handleDelete = () => {
    if (window.confirm('Delete this transaction? This cannot be undone.')) {
      deleteMutation.mutate(tx.id);
    }
  };

  return (
    <tr
      className={`border-b border-gray-100 hover:bg-gray-50 ${
        !tx.is_enabled ? 'opacity-50' : ''
      }`}
    >
      <td className="py-3 px-4 text-sm text-gray-600">{tx.date}</td>
      <td className="py-3 px-4 text-sm text-gray-900">
        {tx.description || <span className="text-gray-400 italic">—</span>}
      </td>
      <td className="py-3 px-4 text-sm text-gray-600">{categoryName}</td>
      <td
        className={`py-3 px-4 text-sm font-semibold text-right ${
          isIn ? 'text-green-600' : 'text-red-600'
        }`}
      >
        {isIn ? '+' : '-'}${amountDisplay}
      </td>
      <td className="py-3 px-4">
        <div className="flex items-center gap-2">
          <button
            onClick={handleToggle}
            disabled={toggleMutation.isPending}
            className="text-xs text-blue-600 hover:underline disabled:opacity-50"
          >
            {tx.is_enabled ? 'Disable' : 'Enable'}
          </button>
          <button
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="text-xs text-red-600 hover:underline disabled:opacity-50"
          >
            Delete
          </button>
        </div>
      </td>
    </tr>
  );
}

export default function TransactionsPage() {
  const selectedFamilyId = useAuthStore((s) => s.selectedFamilyId);
  const [showNewForm, setShowNewForm] = useState(false);
  const [selectedAccountId, setSelectedAccountId] = useState<string | null>(null);

  const {
    data: accounts,
    isLoading: accountsLoading,
    isError: accountsError,
  } = useAccounts(selectedFamilyId ?? '');

  const resolvedAccountId = selectedAccountId ?? accounts?.[0]?.id ?? '';

  const {
    data: transactions,
    isLoading: txLoading,
    isError: txError,
  } = useTransactions(selectedFamilyId ?? '', resolvedAccountId);

  const { data: categories } = useCategories(selectedFamilyId ?? '');

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

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8 text-gray-900">Transactions</h1>

      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-3 flex-wrap">
            <h2 className="text-xl font-semibold text-gray-900">Transaction List</h2>
            {accountsLoading && (
              <span className="text-sm text-gray-400">Loading accounts…</span>
            )}
            {!accountsLoading && accounts && accounts.length > 0 && (
              <select
                value={selectedAccountId ?? accounts[0]?.id ?? ''}
                onChange={(e) => {
                  setSelectedAccountId(e.target.value);
                  setShowNewForm(false);
                }}
                className="border rounded px-3 py-1.5 text-sm text-gray-700"
              >
                {accounts.map((acc: Account) => (
                  <option key={acc.id} value={acc.id}>
                    {acc.name} (${(acc.balance_cents / 100).toFixed(2)} {acc.currency})
                  </option>
                ))}
              </select>
            )}
          </div>
          <button
            onClick={() => setShowNewForm((v) => !v)}
            disabled={!resolvedAccountId}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm disabled:opacity-50"
          >
            {showNewForm ? 'Cancel' : '+ New Transaction'}
          </button>
        </div>

        {accountsError && (
          <p className="text-red-600 text-sm mb-4">Failed to load accounts.</p>
        )}

        {!accountsLoading && accounts?.length === 0 && (
          <p className="text-gray-500 text-sm mb-4">
            No accounts yet.{' '}
            <Link href="/accounts" className="text-blue-600 hover:underline">
              Create an account first.
            </Link>
          </p>
        )}

        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Date</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Description</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Category</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">Amount</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Actions</th>
            </tr>
          </thead>
          <tbody>
            {showNewForm && resolvedAccountId && categories && categories.length > 0 && (
              <NewTransactionForm
                familyId={selectedFamilyId}
                accountId={resolvedAccountId}
                categories={categories}
                onClose={() => setShowNewForm(false)}
              />
            )}

            {txLoading && (
              <tr>
                <td colSpan={5} className="py-8 text-center text-gray-400">
                  Loading transactions…
                </td>
              </tr>
            )}

            {txError && !txLoading && (
              <tr>
                <td colSpan={5} className="py-8 text-center text-red-600 text-sm">
                  Failed to load transactions.
                </td>
              </tr>
            )}

            {!txLoading && !txError && (!transactions || transactions.length === 0) && (
              <tr>
                <td colSpan={5} className="py-8 text-center text-gray-500">
                  No transactions yet. Click &quot;+ New Transaction&quot; to add one.
                </td>
              </tr>
            )}

            {!txLoading &&
              !txError &&
              transactions?.map((tx) => (
                <TransactionRow
                  key={tx.id}
                  tx={tx}
                  familyId={selectedFamilyId}
                  accountId={resolvedAccountId}
                  categories={categories ?? []}
                />
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
