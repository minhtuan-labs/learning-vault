'use client';

import { useState } from 'react';
import {
  useFamilyMembers,
  useCategories,
  useCreateMemberMutation,
  useToggleMemberMutation,
  useCreateCategoryMutation,
} from '@/lib/api-queries';
import { useAuthStore } from '@/lib/stores';
import type { FamilyMember, Category } from '@/lib/types';

// ── Family Members tab ─────────────────────────────────────────────────────

function AddMemberForm({ familyId }: { familyId: string }) {
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [password, setPassword] = useState('');
  const [success, setSuccess] = useState(false);

  const createMutation = useCreateMemberMutation(familyId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(
      { email, first_name: firstName, last_name: lastName, password },
      {
        onSuccess: () => {
          setEmail('');
          setFirstName('');
          setLastName('');
          setPassword('');
          setSuccess(true);
          setTimeout(() => setSuccess(false), 3000);
        },
      }
    );
  };

  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Add Member</h3>
      <form onSubmit={handleSubmit} className="flex flex-wrap gap-3 items-end">
        <div className="flex flex-col gap-1">
          <label htmlFor="mem-email" className="text-xs text-gray-600">
            Email
          </label>
          <input
            id="mem-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="alice@example.com"
            className="border rounded px-2 py-1.5 text-sm w-52"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="mem-first" className="text-xs text-gray-600">
            First Name
          </label>
          <input
            id="mem-first"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            required
            placeholder="Alice"
            className="border rounded px-2 py-1.5 text-sm w-32"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="mem-last" className="text-xs text-gray-600">
            Last Name
          </label>
          <input
            id="mem-last"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            required
            placeholder="Smith"
            className="border rounded px-2 py-1.5 text-sm w-32"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="mem-pass" className="text-xs text-gray-600">
            Password
          </label>
          <input
            id="mem-pass"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="••••••••"
            className="border rounded px-2 py-1.5 text-sm w-32"
          />
        </div>
        <button
          type="submit"
          disabled={createMutation.isPending}
          className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          {createMutation.isPending ? 'Adding…' : 'Add Member'}
        </button>
      </form>
      {success && (
        <p className="mt-2 text-xs text-green-600">Member added successfully.</p>
      )}
      {createMutation.isError && (
        <p className="mt-2 text-xs text-red-600">Failed to add member. Please try again.</p>
      )}
    </div>
  );
}

const roleColors: Record<string, string> = {
  owner: 'bg-purple-100 text-purple-700',
  member: 'bg-blue-100 text-blue-700',
  viewer: 'bg-gray-100 text-gray-600',
  superadmin: 'bg-red-100 text-red-700',
};

function MemberRow({ member, familyId }: { member: FamilyMember; familyId: string }) {
  const toggleMutation = useToggleMemberMutation(familyId);

  return (
    <li className="flex items-center justify-between py-3 px-4 hover:bg-gray-50 rounded-lg">
      <div className="flex items-center gap-3">
        <div>
          <p className="text-sm font-medium text-gray-900">
            {member.first_name} {member.last_name}
          </p>
          <p className="text-xs text-gray-500">{member.email}</p>
        </div>
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${
            roleColors[member.role] ?? 'bg-gray-100 text-gray-600'
          }`}
        >
          {member.role}
        </span>
        {member.status === 'disabled' && (
          <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700">
            Disabled
          </span>
        )}
      </div>
      <button
        onClick={() =>
          toggleMutation.mutate({
            userId: member.user_id,
            status: member.status === 'disabled' ? 'active' : 'disabled',
          })
        }
        disabled={toggleMutation.isPending}
        className={`text-xs px-3 py-1 rounded border disabled:opacity-50 ${
          member.status !== 'disabled'
            ? 'border-yellow-300 text-yellow-700 hover:bg-yellow-50'
            : 'border-green-300 text-green-700 hover:bg-green-50'
        }`}
      >
        {member.status !== 'disabled' ? 'Disable' : 'Enable'}
      </button>
    </li>
  );
}

function MembersTab({ familyId }: { familyId: string }) {
  const [showForm, setShowForm] = useState(false);
  const { data: members, isLoading, isError } = useFamilyMembers(familyId);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-900">Family Members</h2>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="text-sm px-4 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {showForm ? 'Cancel' : '+ Add Member'}
        </button>
      </div>

      {showForm && <AddMemberForm familyId={familyId} />}

      {isLoading && (
        <div className="space-y-2 animate-pulse">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-12 bg-gray-100 rounded" />
          ))}
        </div>
      )}

      {isError && (
        <p className="text-red-600 text-sm">Failed to load members.</p>
      )}

      {!isLoading && !isError && (!members || members.length === 0) && (
        <p className="text-gray-500 text-sm py-4">No members yet.</p>
      )}

      {members && members.length > 0 && (
        <ul className="divide-y divide-gray-100 border border-gray-100 rounded-lg">
          {members.map((m) => (
            <MemberRow key={m.user_id} member={m} familyId={familyId} />
          ))}
        </ul>
      )}
    </div>
  );
}

// ── Categories tab ─────────────────────────────────────────────────────────

const catTypeColors: Record<string, string> = {
  income: 'bg-green-100 text-green-700',
  expense: 'bg-red-100 text-red-700',
  investment: 'bg-purple-100 text-purple-700',
};

function CategoryRow({ category }: { category: Category }) {
  return (
    <li className="flex items-center justify-between py-3 px-4 hover:bg-gray-50 rounded-lg">
      <div className="flex items-center gap-3">
        {!category.is_custom && (
          <span
            title="Default category"
            className="text-xs bg-gray-200 text-gray-500 px-1.5 py-0.5 rounded font-medium"
          >
            lock
          </span>
        )}
        <span className="text-sm font-medium text-gray-900">{category.name}</span>
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${
            catTypeColors[category.type] ?? 'bg-gray-100 text-gray-600'
          }`}
        >
          {category.type}
        </span>
        <span className="text-xs text-gray-400">
          {category.is_custom ? 'Custom' : 'Default'}
        </span>
      </div>
    </li>
  );
}

function AddCategoryForm({ familyId }: { familyId: string }) {
  const [name, setName] = useState('');
  const [type, setType] = useState<'income' | 'expense' | 'investment'>('expense');
  const [success, setSuccess] = useState(false);

  const createMutation = useCreateCategoryMutation(familyId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(
      { name, type },
      {
        onSuccess: () => {
          setName('');
          setType('expense');
          setSuccess(true);
          setTimeout(() => setSuccess(false), 3000);
        },
      }
    );
  };

  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Add Category</h3>
      <form onSubmit={handleSubmit} className="flex flex-wrap gap-3 items-end">
        <div className="flex flex-col gap-1">
          <label htmlFor="cat-name" className="text-xs text-gray-600">
            Name
          </label>
          <input
            id="cat-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            placeholder="e.g. Groceries"
            className="border rounded px-2 py-1.5 text-sm w-48"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="cat-type" className="text-xs text-gray-600">
            Type
          </label>
          <select
            id="cat-type"
            value={type}
            onChange={(e) => setType(e.target.value as 'income' | 'expense' | 'investment')}
            className="border rounded px-2 py-1.5 text-sm"
          >
            <option value="income">Income</option>
            <option value="expense">Expense</option>
            <option value="investment">Investment</option>
          </select>
        </div>
        <button
          type="submit"
          disabled={createMutation.isPending || !name}
          className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          {createMutation.isPending ? 'Adding…' : 'Add Category'}
        </button>
      </form>
      {success && (
        <p className="mt-2 text-xs text-green-600">Category added successfully.</p>
      )}
      {createMutation.isError && (
        <p className="mt-2 text-xs text-red-600">Failed to add category. Please try again.</p>
      )}
    </div>
  );
}

function CategoriesTab({ familyId }: { familyId: string }) {
  const [showForm, setShowForm] = useState(false);
  const { data: categories, isLoading, isError } = useCategories(familyId);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-900">Categories</h2>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="text-sm px-4 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {showForm ? 'Cancel' : '+ Add Category'}
        </button>
      </div>

      {showForm && <AddCategoryForm familyId={familyId} />}

      {isLoading && (
        <div className="space-y-2 animate-pulse">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-10 bg-gray-100 rounded" />
          ))}
        </div>
      )}

      {isError && (
        <p className="text-red-600 text-sm">Failed to load categories.</p>
      )}

      {!isLoading && !isError && (!categories || categories.length === 0) && (
        <p className="text-gray-500 text-sm py-4">No categories yet.</p>
      )}

      {categories && categories.length > 0 && (
        <ul className="divide-y divide-gray-100 border border-gray-100 rounded-lg">
          {categories.map((cat) => (
            <CategoryRow key={cat.id} category={cat} />
          ))}
        </ul>
      )}
    </div>
  );
}

// ── Account tab ────────────────────────────────────────────────────────────

function AccountTab() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="space-y-6 max-w-md">
      <h2 className="text-lg font-semibold text-gray-900">Account</h2>

      <div className="space-y-3">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Name</p>
          <p className="text-sm font-medium text-gray-900">
            {user?.first_name} {user?.last_name}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Email</p>
          <p className="text-sm font-medium text-gray-900">{user?.email}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Role</p>
          <p className="text-sm font-medium text-gray-900 capitalize">{user?.role ?? '—'}</p>
        </div>
      </div>

      <div className="border-t pt-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Change Password</h3>
        <p className="text-sm text-gray-400 italic">Coming soon</p>
      </div>
    </div>
  );
}

// ── Main page ──────────────────────────────────────────────────────────────

const TABS = [
  { id: 'members', label: 'Family Members' },
  { id: 'categories', label: 'Categories' },
  { id: 'account', label: 'Account' },
] as const;

type TabId = (typeof TABS)[number]['id'];

export default function SettingsPage() {
  const selectedFamilyId = useAuthStore((s) => s.selectedFamilyId);
  const [activeTab, setActiveTab] = useState<TabId>('members');

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8 text-gray-900">Settings</h1>

      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <div className="flex gap-0">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 font-medium transition text-sm ${
                  activeTab === tab.id
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'members' && (
            selectedFamilyId ? (
              <MembersTab familyId={selectedFamilyId} />
            ) : (
              <p className="text-gray-500 text-sm">
                No family selected. Select a family from the{' '}
                <a href="/family-selection" className="text-blue-600 hover:underline">
                  family selection page
                </a>
                .
              </p>
            )
          )}

          {activeTab === 'categories' && (
            selectedFamilyId ? (
              <CategoriesTab familyId={selectedFamilyId} />
            ) : (
              <p className="text-gray-500 text-sm">
                No family selected. Select a family to manage categories.
              </p>
            )
          )}

          {activeTab === 'account' && <AccountTab />}
        </div>
      </div>
    </div>
  );
}
