'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter, useParams } from 'next/navigation';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { AdminFamilyDetail, FamilyMember } from '@/lib/types';

function useAdminFamilyDetail(id: string) {
  return useQuery({
    queryKey: ['admin', 'families', id],
    queryFn: async () => {
      const res = await apiClient.get<AdminFamilyDetail>(`/admin/families/${id}`);
      return res.data;
    },
    retry: 1,
  });
}

function StatusBadge({ active }: { active: boolean }) {
  return active ? (
    <span className="px-2 py-0.5 text-xs rounded-full bg-green-100 text-green-700 border border-green-200 font-medium">
      Active
    </span>
  ) : (
    <span className="px-2 py-0.5 text-xs rounded-full bg-yellow-100 text-yellow-700 border border-yellow-200 font-medium">
      Disabled
    </span>
  );
}

function RoleBadge({ role }: { role: string }) {
  const colorMap: Record<string, string> = {
    owner: 'bg-indigo-100 text-indigo-700 border-indigo-200',
    member: 'bg-gray-100 text-gray-700 border-gray-200',
    viewer: 'bg-blue-50 text-blue-600 border-blue-100',
    superadmin: 'bg-purple-100 text-purple-700 border-purple-200',
  };
  return (
    <span className={`px-2 py-0.5 text-xs rounded-full border font-medium ${colorMap[role] ?? colorMap.member}`}>
      {role}
    </span>
  );
}

interface MemberRowProps {
  member: FamilyMember;
  isOwner: boolean;
  familyId: string;
  onRefresh: () => void;
}

function MemberRow({ member, isOwner, familyId, onRefresh }: MemberRowProps) {
  const [isToggling, setIsToggling] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);

  const handleToggle = async () => {
    setIsToggling(true);
    try {
      const newStatus = member.status === 'active' ? 'disabled' : 'active';
      await apiClient.patch(`/families/${familyId}/members/${member.user_id}`, { status: newStatus });
      onRefresh();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update member status');
    } finally {
      setIsToggling(false);
    }
  };

  const handleRemove = async () => {
    if (!window.confirm(`Remove ${member.first_name} ${member.last_name} from family?`)) return;
    setIsRemoving(true);
    try {
      await apiClient.delete(`/admin/families/${familyId}/members/${member.user_id}`);
      onRefresh();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to remove member');
    } finally {
      setIsRemoving(false);
    }
  };

  return (
    <tr className="border-b border-gray-100 hover:bg-gray-50">
      <td className="py-2.5 px-3">
        <div className="font-medium text-sm text-gray-900">
          {member.first_name} {member.last_name}
        </div>
        <div className="text-xs text-gray-400">{member.email}</div>
      </td>
      <td className="py-2.5 px-3">
        <RoleBadge role={member.role} />
      </td>
      <td className="py-2.5 px-3">
        <StatusBadge active={member.status !== 'disabled'} />
      </td>
      <td className="py-2.5 px-3 text-xs text-gray-500">
        {member.joined_at ? new Date(member.joined_at).toLocaleDateString() : '—'}
      </td>
      <td className="py-2.5 px-3">
        <div className="flex gap-1.5">
          {isOwner ? (
            <span
              className="px-2 py-1 text-xs text-gray-400 bg-gray-50 border border-gray-200 rounded cursor-not-allowed"
              title="Must change owner first"
            >
              Remove
            </span>
          ) : (
            <>
              <button
                onClick={handleToggle}
                disabled={isToggling}
                className="px-2 py-1 text-xs bg-amber-50 text-amber-700 border border-amber-200 rounded hover:bg-amber-100 disabled:opacity-50"
              >
                {isToggling ? '...' : member.status === 'active' ? 'Disable' : 'Enable'}
              </button>
              <button
                onClick={handleRemove}
                disabled={isRemoving}
                className="px-2 py-1 text-xs bg-red-50 text-red-700 border border-red-200 rounded hover:bg-red-100 disabled:opacity-50"
              >
                {isRemoving ? '...' : 'Remove'}
              </button>
            </>
          )}
        </div>
      </td>
    </tr>
  );
}

export default function AdminFamilyDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: family, isLoading, isError, error } = useAdminFamilyDetail(id);

  // Edit name state
  const [editNameOpen, setEditNameOpen] = useState(false);
  const [editName, setEditName] = useState('');
  const [editNameError, setEditNameError] = useState('');
  const [isSavingName, setIsSavingName] = useState(false);

  // Status toggle state
  const [isTogglingStatus, setIsTogglingStatus] = useState(false);

  // Delete state
  const [isDeleting, setIsDeleting] = useState(false);

  // Change owner state
  const [selectedNewOwner, setSelectedNewOwner] = useState('');
  const [isChangingOwner, setIsChangingOwner] = useState(false);
  const [ownerChangeMsg, setOwnerChangeMsg] = useState('');
  const [ownerChangeError, setOwnerChangeError] = useState('');

  // Add member state
  const [addMemberForm, setAddMemberForm] = useState({
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    role: 'member' as 'member' | 'owner',
  });
  const [addMemberError, setAddMemberError] = useState('');
  const [addMemberMsg, setAddMemberMsg] = useState('');
  const [isAddingMember, setIsAddingMember] = useState(false);

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ['admin', 'families', id] });
  };

  const handleEditName = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editName.trim()) return;
    setEditNameError('');
    setIsSavingName(true);
    try {
      await apiClient.put(`/families/${id}`, { name: editName.trim() });
      setEditNameOpen(false);
      refresh();
    } catch (err: any) {
      setEditNameError(err.response?.data?.detail || 'Failed to update name');
    } finally {
      setIsSavingName(false);
    }
  };

  const handleToggleStatus = async () => {
    if (!family) return;
    const action = family.is_active ? 'disable' : 'enable';
    if (!window.confirm(`${action === 'disable' ? 'Disable' : 'Enable'} family "${family.name}"?`)) return;
    setIsTogglingStatus(true);
    try {
      await apiClient.patch(`/admin/families/${id}/status`, { is_active: !family.is_active });
      refresh();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update family status');
    } finally {
      setIsTogglingStatus(false);
    }
  };

  const handleDelete = async () => {
    if (!family) return;
    if (!window.confirm(`Delete "${family.name}"? This cannot be undone.`)) return;
    setIsDeleting(true);
    try {
      await apiClient.delete(`/admin/families/${id}`);
      router.push('/admin');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete family');
      setIsDeleting(false);
    }
  };

  const handleChangeOwner = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedNewOwner) return;
    setOwnerChangeError('');
    setOwnerChangeMsg('');
    setIsChangingOwner(true);
    try {
      await apiClient.put(`/admin/families/${id}/owner`, { new_owner_user_id: selectedNewOwner });
      setOwnerChangeMsg('Owner changed successfully.');
      setSelectedNewOwner('');
      refresh();
    } catch (err: any) {
      setOwnerChangeError(err.response?.data?.detail || 'Failed to change owner');
    } finally {
      setIsChangingOwner(false);
    }
  };

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddMemberError('');
    setAddMemberMsg('');
    setIsAddingMember(true);
    try {
      await apiClient.post(`/admin/families/${id}/members`, addMemberForm);
      setAddMemberMsg('Member added successfully.');
      setAddMemberForm({ email: '', first_name: '', last_name: '', password: '', role: 'member' });
      refresh();
    } catch (err: any) {
      setAddMemberError(err.response?.data?.detail || 'Failed to add member');
    } finally {
      setIsAddingMember(false);
    }
  };

  if (isLoading) {
    return (
      <div>
        <Link href="/admin" className="text-sm text-indigo-600 hover:underline mb-4 inline-block">
          &larr; Back to Admin
        </Link>
        <p className="text-gray-500 text-sm mt-4">Loading family details...</p>
      </div>
    );
  }

  if (isError || !family) {
    return (
      <div>
        <Link href="/admin" className="text-sm text-indigo-600 hover:underline mb-4 inline-block">
          &larr; Back to Admin
        </Link>
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded text-yellow-700 text-sm">
          Could not load family details.
          <br />
          <span className="text-xs text-yellow-600">
            {(error as any)?.response?.data?.detail || (error as Error)?.message}
          </span>
        </div>
      </div>
    );
  }

  const activeNonOwnerMembers = family.members.filter(
    (m) => m.status !== 'disabled' && m.user_id !== family.owner_id,
  );
  const canChangeOwner = activeNonOwnerMembers.length > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Link href="/admin" className="text-sm text-indigo-600 hover:underline mb-3 inline-block">
          &larr; Back to Admin
        </Link>

        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div>
            {editNameOpen ? (
              <form onSubmit={handleEditName} className="flex gap-2 items-center mb-1">
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="px-2 py-1.5 border border-gray-300 rounded text-sm bg-white text-gray-900 w-48"
                  required
                  autoFocus
                />
                <button
                  type="submit"
                  disabled={isSavingName || !editName.trim()}
                  className="px-3 py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:opacity-50 font-medium"
                >
                  {isSavingName ? 'Saving...' : 'Save'}
                </button>
                <button
                  type="button"
                  onClick={() => setEditNameOpen(false)}
                  className="px-2 py-1.5 text-xs text-gray-600 hover:text-gray-900"
                >
                  Cancel
                </button>
                {editNameError && (
                  <p className="text-xs text-red-600">{editNameError}</p>
                )}
              </form>
            ) : (
              <div className="flex items-center gap-2 mb-1">
                <h1 className="text-2xl font-bold text-gray-900">{family.name}</h1>
                <StatusBadge active={family.is_active} />
              </div>
            )}
            <div className="text-sm text-gray-500">
              Owner: <span className="font-medium text-gray-700">{family.owner_name}</span>
              {' '}
              <span className="text-gray-400">({family.owner_email})</span>
            </div>
            <div className="text-sm text-gray-500 mt-0.5">
              {family.member_count} member{family.member_count !== 1 ? 's' : ''}
            </div>
          </div>

          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => { setEditName(family.name); setEditNameOpen(true); setEditNameError(''); }}
              className="px-3 py-1.5 text-xs bg-gray-50 text-gray-700 border border-gray-200 rounded hover:bg-gray-100 font-medium"
            >
              Edit Name
            </button>
            <button
              onClick={handleToggleStatus}
              disabled={isTogglingStatus}
              className={`px-3 py-1.5 text-xs border rounded font-medium disabled:opacity-50 ${
                family.is_active
                  ? 'bg-yellow-50 text-yellow-700 border-yellow-200 hover:bg-yellow-100'
                  : 'bg-green-50 text-green-700 border-green-200 hover:bg-green-100'
              }`}
            >
              {isTogglingStatus ? '...' : family.is_active ? 'Disable Family' : 'Enable Family'}
            </button>
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="px-3 py-1.5 text-xs bg-red-50 text-red-700 border border-red-200 rounded hover:bg-red-100 font-medium disabled:opacity-50"
            >
              {isDeleting ? 'Deleting...' : 'Delete Family'}
            </button>
          </div>
        </div>
      </div>

      {/* Change Owner */}
      {canChangeOwner && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <h2 className="text-sm font-semibold text-amber-800 mb-2">Change Owner</h2>
          <p className="text-xs text-amber-700 mb-3">
            This will demote the current owner to member.
          </p>
          {ownerChangeMsg ? (
            <p className="text-sm text-green-700 font-medium">{ownerChangeMsg}</p>
          ) : (
            <form onSubmit={handleChangeOwner} className="flex gap-2 flex-wrap items-center">
              <select
                value={selectedNewOwner}
                onChange={(e) => setSelectedNewOwner(e.target.value)}
                className="px-2 py-1.5 border border-amber-300 rounded text-sm bg-white text-gray-900"
                required
              >
                <option value="">Select new owner...</option>
                {activeNonOwnerMembers.map((m) => (
                  <option key={m.user_id} value={m.user_id}>
                    {m.first_name} {m.last_name} ({m.email})
                  </option>
                ))}
              </select>
              <button
                type="submit"
                disabled={isChangingOwner || !selectedNewOwner}
                className="px-3 py-1.5 bg-amber-600 text-white text-xs rounded hover:bg-amber-700 disabled:opacity-50 font-medium"
              >
                {isChangingOwner ? 'Setting...' : 'Set as Owner'}
              </button>
              {ownerChangeError && (
                <p className="text-xs text-red-600">{ownerChangeError}</p>
              )}
            </form>
          )}
        </div>
      )}

      {/* Add Member */}
      <div className="p-4 bg-white border border-gray-200 rounded-lg">
        <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">Add Member</h2>
        {addMemberMsg && (
          <p className="text-sm text-green-700 font-medium mb-2">{addMemberMsg}</p>
        )}
        <form onSubmit={handleAddMember} className="space-y-2">
          <div className="grid grid-cols-2 gap-2">
            <input
              type="text"
              placeholder="First Name"
              value={addMemberForm.first_name}
              onChange={(e) => setAddMemberForm((f) => ({ ...f, first_name: e.target.value }))}
              className="px-2 py-1.5 border border-gray-300 rounded text-sm bg-white text-gray-900 placeholder-gray-400"
              required
            />
            <input
              type="text"
              placeholder="Last Name"
              value={addMemberForm.last_name}
              onChange={(e) => setAddMemberForm((f) => ({ ...f, last_name: e.target.value }))}
              className="px-2 py-1.5 border border-gray-300 rounded text-sm bg-white text-gray-900 placeholder-gray-400"
              required
            />
          </div>
          <input
            type="email"
            placeholder="Email"
            value={addMemberForm.email}
            onChange={(e) => setAddMemberForm((f) => ({ ...f, email: e.target.value }))}
            className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm bg-white text-gray-900 placeholder-gray-400"
            required
          />
          <div className="grid grid-cols-2 gap-2">
            <input
              type="password"
              placeholder="Password"
              value={addMemberForm.password}
              onChange={(e) => setAddMemberForm((f) => ({ ...f, password: e.target.value }))}
              className="px-2 py-1.5 border border-gray-300 rounded text-sm bg-white text-gray-900 placeholder-gray-400"
              required
            />
            <select
              value={addMemberForm.role}
              onChange={(e) => setAddMemberForm((f) => ({ ...f, role: e.target.value as 'member' | 'owner' }))}
              className="px-2 py-1.5 border border-gray-300 rounded text-sm bg-white text-gray-900"
            >
              <option value="member">Member</option>
              <option value="owner">Owner</option>
            </select>
          </div>
          {addMemberError && (
            <p className="text-xs text-red-600">{addMemberError}</p>
          )}
          <button
            type="submit"
            disabled={isAddingMember}
            className="px-3 py-1.5 bg-indigo-600 text-white text-xs rounded hover:bg-indigo-700 disabled:opacity-50 font-medium"
          >
            {isAddingMember ? 'Adding...' : 'Add Member'}
          </button>
        </form>
      </div>

      {/* Members Table */}
      <div>
        <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">Members</h2>
        {family.members.length === 0 ? (
          <p className="text-sm text-gray-500">No members yet.</p>
        ) : (
          <div className="overflow-x-auto border border-gray-200 rounded-lg">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="py-2.5 px-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Name / Email</th>
                  <th className="py-2.5 px-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Role</th>
                  <th className="py-2.5 px-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Status</th>
                  <th className="py-2.5 px-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Joined</th>
                  <th className="py-2.5 px-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Actions</th>
                </tr>
              </thead>
              <tbody>
                {family.members.map((member) => (
                  <MemberRow
                    key={member.user_id}
                    member={member}
                    isOwner={member.user_id === family.owner_id}
                    familyId={id}
                    onRefresh={refresh}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
