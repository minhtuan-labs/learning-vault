'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useLogoutMutation } from '@/lib/api-queries';
import { apiClient } from '@/lib/api-client';
import type { Family } from '@/lib/types';

function useAdminFamilies() {
  return useQuery({
    queryKey: ['admin', 'families'],
    queryFn: async () => {
      const res = await apiClient.get<{ families: Family[] }>('/admin/families');
      return res.data.families || [];
    },
    retry: 1,
  });
}

interface FamilyRowProps {
  family: Family;
  onRefresh: () => void;
}

function FamilyRow({ family, onRefresh }: FamilyRowProps) {
  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteForm, setInviteForm] = useState({
    email: '',
    first_name: '',
    last_name: '',
    password: '',
  });
  const [inviteMsg, setInviteMsg] = useState('');
  const [inviteError, setInviteError] = useState('');
  const [isInviting, setIsInviting] = useState(false);

  const [editOpen, setEditOpen] = useState(false);
  const [editName, setEditName] = useState(family.name);
  const [editError, setEditError] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  const [isDeleting, setIsDeleting] = useState(false);

  const handleInviteOwner = async (e: React.FormEvent) => {
    e.preventDefault();
    setInviteError('');
    setInviteMsg('');
    setIsInviting(true);
    try {
      await apiClient.post(`/admin/families/${family.id}/invite-owner`, inviteForm);
      setInviteMsg('Owner assigned.');
      setInviteForm({ email: '', first_name: '', last_name: '', password: '' });
      onRefresh();
    } catch (err: any) {
      setInviteError(err.response?.data?.detail || 'Failed to assign owner');
    } finally {
      setIsInviting(false);
    }
  };

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editName.trim()) return;
    setEditError('');
    setIsEditing(true);
    try {
      await apiClient.put(`/families/${family.id}`, { name: editName.trim() });
      setEditOpen(false);
      onRefresh();
    } catch (err: any) {
      setEditError(err.response?.data?.detail || 'Failed to update family');
    } finally {
      setIsEditing(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Delete ${family.name}? This cannot be undone.`)) return;
    setIsDeleting(true);
    try {
      await apiClient.delete(`/admin/families/${family.id}`);
      onRefresh();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete family');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <li className="py-3 px-1">
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="flex items-center gap-2">
            <Link
              href={'/admin/families/' + family.id}
              className="font-medium text-indigo-700 hover:text-indigo-900 hover:underline text-sm"
            >
              {family.name}
            </Link>
            {family.is_active === false ? (
              <span className="px-1.5 py-0.5 text-xs rounded-full bg-yellow-100 text-yellow-700 border border-yellow-200">
                Disabled
              </span>
            ) : (
              <span className="px-1.5 py-0.5 text-xs rounded-full bg-green-100 text-green-700 border border-green-200">
                Active
              </span>
            )}
          </div>
          <div className="text-xs text-gray-400 mt-0.5">
            {family.member_count ?? 0} members
          </div>
        </div>
        <div className="flex gap-1.5 shrink-0">
          <button
            onClick={() => { setInviteOpen((o) => !o); setInviteMsg(''); setInviteError(''); setEditOpen(false); }}
            className="px-2 py-1 text-xs bg-indigo-50 text-indigo-700 rounded hover:bg-indigo-100 border border-indigo-200"
          >
            Invite Owner
          </button>
          <button
            onClick={() => { setEditOpen((o) => !o); setEditName(family.name); setEditError(''); setInviteOpen(false); }}
            className="px-2 py-1 text-xs bg-gray-50 text-gray-700 rounded hover:bg-gray-100 border border-gray-200"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="px-2 py-1 text-xs bg-red-50 text-red-700 rounded hover:bg-red-100 border border-red-200 disabled:opacity-50"
          >
            {isDeleting ? '...' : 'Delete'}
          </button>
        </div>
      </div>

      {/* Invite Owner inline form */}
      {inviteOpen && (
        <div className="mt-2 p-3 bg-indigo-50 border border-indigo-100 rounded-lg">
          {inviteMsg ? (
            <div className="flex items-center justify-between">
              <p className="text-sm text-indigo-700 font-medium">{inviteMsg}</p>
              <button
                onClick={() => { setInviteOpen(false); setInviteMsg(''); }}
                className="text-xs text-indigo-500 hover:text-indigo-700"
              >
                Close
              </button>
            </div>
          ) : (
            <form onSubmit={handleInviteOwner} className="space-y-2">
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="text"
                  placeholder="First Name"
                  value={inviteForm.first_name}
                  onChange={(e) => setInviteForm((f) => ({ ...f, first_name: e.target.value }))}
                  className="px-2 py-1.5 border border-indigo-200 rounded text-sm bg-white text-gray-900 placeholder-gray-400"
                  required
                />
                <input
                  type="text"
                  placeholder="Last Name"
                  value={inviteForm.last_name}
                  onChange={(e) => setInviteForm((f) => ({ ...f, last_name: e.target.value }))}
                  className="px-2 py-1.5 border border-indigo-200 rounded text-sm bg-white text-gray-900 placeholder-gray-400"
                  required
                />
              </div>
              <input
                type="email"
                placeholder="Email"
                value={inviteForm.email}
                onChange={(e) => setInviteForm((f) => ({ ...f, email: e.target.value }))}
                className="w-full px-2 py-1.5 border border-indigo-200 rounded text-sm bg-white text-gray-900 placeholder-gray-400"
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={inviteForm.password}
                onChange={(e) => setInviteForm((f) => ({ ...f, password: e.target.value }))}
                className="w-full px-2 py-1.5 border border-indigo-200 rounded text-sm bg-white text-gray-900 placeholder-gray-400"
                required
              />
              {inviteError && (
                <p className="text-xs text-red-600">{inviteError}</p>
              )}
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={isInviting}
                  className="px-3 py-1.5 bg-indigo-600 text-white text-xs rounded hover:bg-indigo-700 disabled:opacity-50 font-medium"
                >
                  {isInviting ? 'Assigning...' : 'Assign Owner'}
                </button>
                <button
                  type="button"
                  onClick={() => setInviteOpen(false)}
                  className="px-3 py-1.5 text-xs text-gray-600 hover:text-gray-900"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* Edit inline form */}
      {editOpen && (
        <div className="mt-2 p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <form onSubmit={handleEdit} className="flex gap-2">
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              className="flex-1 px-2 py-1.5 border border-gray-300 rounded text-sm bg-white text-gray-900"
              required
            />
            <button
              type="submit"
              disabled={isEditing || !editName.trim()}
              className="px-3 py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:opacity-50 font-medium"
            >
              {isEditing ? 'Saving...' : 'Save'}
            </button>
            <button
              type="button"
              onClick={() => setEditOpen(false)}
              className="px-2 py-1.5 text-xs text-gray-600 hover:text-gray-900"
            >
              Cancel
            </button>
          </form>
          {editError && (
            <p className="mt-1 text-xs text-red-600">{editError}</p>
          )}
        </div>
      )}
    </li>
  );
}

export default function AdminPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const logoutMutation = useLogoutMutation();
  const { data: families, isLoading, isError, error } = useAdminFamilies();
  const [familyName, setFamilyName] = useState('');
  const [createError, setCreateError] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const handleLogout = async () => {
    await logoutMutation.mutateAsync();
    router.push('/login');
  };

  const handleCreateFamily = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!familyName.trim()) return;
    setCreateError('');
    setIsCreating(true);
    try {
      await apiClient.post('/families', { name: familyName.trim() });
      setFamilyName('');
      queryClient.invalidateQueries({ queryKey: ['admin', 'families'] });
    } catch (err: any) {
      setCreateError(err.response?.data?.detail || 'Failed to create family');
    } finally {
      setIsCreating(false);
    }
  };

  const refreshFamilies = () => {
    queryClient.invalidateQueries({ queryKey: ['admin', 'families'] });
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>
        <button
          onClick={handleLogout}
          disabled={logoutMutation.isPending}
          className="px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 text-sm font-medium"
        >
          {logoutMutation.isPending ? 'Logging out...' : 'Logout'}
        </button>
      </div>

      {/* Create Family */}
      <div className="mb-6">
        <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
          Create Family
        </h2>
        <form onSubmit={handleCreateFamily} className="flex gap-2">
          <input
            type="text"
            value={familyName}
            onChange={(e) => setFamilyName(e.target.value)}
            placeholder="Family name"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 text-sm"
            required
          />
          <button
            type="submit"
            disabled={isCreating || !familyName.trim()}
            className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium whitespace-nowrap"
          >
            {isCreating ? 'Creating...' : 'Create'}
          </button>
        </form>
        {createError && (
          <p className="mt-2 text-sm text-red-600">{createError}</p>
        )}
      </div>

      {/* Family List */}
      <div>
        <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
          All Families
        </h2>

        {isLoading && (
          <p className="text-gray-500 text-sm">Loading families...</p>
        )}

        {isError && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded text-yellow-700 text-sm">
            Could not load families — the admin endpoint may not be available yet.
            <br />
            <span className="text-xs text-yellow-600">
              {(error as any)?.response?.data?.detail || (error as Error)?.message}
            </span>
          </div>
        )}

        {!isLoading && !isError && families && families.length === 0 && (
          <p className="text-gray-500 text-sm">No families yet. Create one above.</p>
        )}

        {!isLoading && !isError && families && families.length > 0 && (
          <ul className="divide-y divide-gray-100 -mx-1">
            {families.map((family) => (
              <FamilyRow key={family.id} family={family} onRefresh={refreshFamilies} />
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
