'use client';

import { useState } from 'react';
import { useAccounts, useCreateAccountMutation, useUpdateAccountMutation } from '@/lib/api-queries';
import { useAuthStore } from '@/lib/stores';
import Link from 'next/link';
import type { Account, AccountType } from '@/lib/types';

function centsToDisplay(cents: number): string {
  return (cents / 100).toFixed(2);
}

const ACCOUNT_TYPES: AccountType[] = ['bank', 'savings', 'investment', 'cash'];

const typeColors: Record<AccountType, string> = {
  bank: 'bg-blue-100 text-blue-700',
  savings: 'bg-green-100 text-green-700',
  investment: 'bg-purple-100 text-purple-700',
  cash: 'bg-yellow-100 text-yellow-700',
};

function AccountRow({
  account,
  familyId,
}: {
  account: Account;
  familyId: string;
}) {
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState(account.name);
  const [editType, setEditType] = useState<AccountType>(account.type);
  const updateMutation = useUpdateAccountMutation(familyId, account.id);

  const handleSave = () => {
    updateMutation.mutate(
      { name: editName, type: editType },
      {
        onSuccess: () => setEditing(false),
      }
    );
  };

  return (
    <li className="flex items-center justify-between py-4 px-4 hover:bg-gray-50 rounded-lg">
      {editing ? (
        <div className="flex items-center gap-3 flex-1">
          <input
            value={editName}
            onChange={(e) => setEditName(e.target.value)}
            className="border rounded px-2 py-1 text-sm flex-1 max-w-xs"
          />
          <select
            value={editType}
            onChange={(e) => setEditType(e.target.value as AccountType)}
            className="border rounded px-2 py-1 text-sm"
          >
            {ACCOUNT_TYPES.map((t) => (
              <option key={t} value={t}>
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </option>
            ))}
          </select>
          <button
            onClick={handleSave}
            disabled={updateMutation.isPending}
            className="text-sm text-white bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded disabled:opacity-50"
          >
            {updateMutation.isPending ? 'Saving…' : 'Save'}
          </button>
          <button
            onClick={() => {
              setEditing(false);
              setEditName(account.name);
              setEditType(account.type);
            }}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Cancel
          </button>
        </div>
      ) : (
        <>
          <div className="flex items-center gap-3">
            <span className="font-medium text-gray-900">{account.name}</span>
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${
                typeColors[account.type] ?? 'bg-gray-100 text-gray-700'
              }`}
            >
              {account.type}
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-700 font-semibold">
              ${centsToDisplay(account.balance_cents)}
              <span className="text-xs text-gray-400 ml-1">{account.currency}</span>
            </span>
            <button
              onClick={() => setEditing(true)}
              className="text-sm text-blue-600 hover:underline"
            >
              Edit
            </button>
          </div>
        </>
      )}
    </li>
  );
}

function NewAccountForm({ familyId }: { familyId: string }) {
  const [name, setName] = useState('');
  const [type, setType] = useState<AccountType>('bank');
  const [initialBalance, setInitialBalance] = useState('');
  const [currency, setCurrency] = useState('USD');
  const [success, setSuccess] = useState(false);

  const createMutation = useCreateAccountMutation(familyId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const balanceCents = Math.round(parseFloat(initialBalance || '0') * 100);
    createMutation.mutate(
      { name, type, initial_balance_cents: balanceCents, currency },
      {
        onSuccess: () => {
          setName('');
          setType('bank');
          setInitialBalance('');
          setCurrency('USD');
          setSuccess(true);
          setTimeout(() => setSuccess(false), 3000);
        },
      }
    );
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">New Account</h2>
      <form onSubmit={handleSubmit} className="flex flex-wrap gap-3 items-end">
        <div className="flex flex-col gap-1">
          <label htmlFor="acc-name" className="text-sm text-gray-600">
            Name
          </label>
          <input
            id="acc-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Checking"
            required
            className="border rounded px-3 py-2 text-sm w-48"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="acc-type" className="text-sm text-gray-600">
            Type
          </label>
          <select
            id="acc-type"
            value={type}
            onChange={(e) => setType(e.target.value as AccountType)}
            className="border rounded px-3 py-2 text-sm"
          >
            {ACCOUNT_TYPES.map((t) => (
              <option key={t} value={t}>
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="acc-balance" className="text-sm text-gray-600">
            Initial Balance ($)
          </label>
          <input
            id="acc-balance"
            type="number"
            min="0"
            step="0.01"
            value={initialBalance}
            onChange={(e) => setInitialBalance(e.target.value)}
            placeholder="0.00"
            className="border rounded px-3 py-2 text-sm w-36"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="acc-currency" className="text-sm text-gray-600">
            Currency
          </label>
          <input
            id="acc-currency"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            placeholder="USD"
            className="border rounded px-3 py-2 text-sm w-20"
          />
        </div>
        <button
          type="submit"
          disabled={createMutation.isPending || !name}
          className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          {createMutation.isPending ? 'Creating…' : 'Create Account'}
        </button>
      </form>
      {success && (
        <p className="mt-3 text-sm text-green-600">Account created successfully.</p>
      )}
      {createMutation.isError && (
        <p className="mt-3 text-sm text-red-600">Failed to create account. Please try again.</p>
      )}
    </div>
  );
}

export default function AccountsPage() {
  const selectedFamilyId = useAuthStore((s) => s.selectedFamilyId);
  const { data: accounts, isLoading, isError } = useAccounts(selectedFamilyId ?? '');

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
      <h1 className="text-3xl font-bold mb-6 text-gray-900">Accounts</h1>

      <NewAccountForm familyId={selectedFamilyId} />

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">All Accounts</h2>

        {isLoading && (
          <div className="space-y-3 animate-pulse">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-100 rounded" />
            ))}
          </div>
        )}

        {isError && (
          <p className="text-red-600">Failed to load accounts. Please refresh.</p>
        )}

        {!isLoading && !isError && (!accounts || accounts.length === 0) && (
          <p className="text-gray-500 text-center py-8">
            No accounts yet. Create your first account above.
          </p>
        )}

        {accounts && accounts.length > 0 && (
          <ul className="divide-y divide-gray-100">
            {accounts.map((account) => (
              <AccountRow key={account.id} account={account} familyId={selectedFamilyId} />
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
