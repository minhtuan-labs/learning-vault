'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useLogoutMutation, useFamilies } from '@/lib/api-queries';
import { useAuthStore, useUIStore } from '@/lib/stores';
import { getInitials } from '@/lib/utils';

export default function Navbar() {
  const router = useRouter();
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const selectedFamilyId = useAuthStore((s) => s.selectedFamilyId);
  const setSelectedFamily = useAuthStore((s) => s.setSelectedFamily);
  const logoutMutation = useLogoutMutation();
  const { data: families } = useFamilies();

  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const hasSession =
    !!user ||
    (typeof document !== 'undefined' && document.cookie.includes('auth_token'));

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [menuOpen]);

  const handleLogout = async () => {
    setMenuOpen(false);
    await logoutMutation.mutateAsync();
    logout();
    router.push('/login');
  };

  const handleFamilyChange = (familyId: string) => {
    setSelectedFamily(familyId);
    setMenuOpen(false);
    router.push('/dashboard');
  };

  const handleSwitchFamily = () => {
    setMenuOpen(false);
    router.push('/family-selection');
  };

  return (
    <nav className="bg-white border-b border-gray-200 px-8 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={toggleSidebar}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
            title="Toggle sidebar"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 className="text-2xl font-bold text-gray-900">NestFi</h1>
        </div>

        {hasSession && (
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setMenuOpen((v) => !v)}
              className="flex items-center gap-2 px-2 py-1 rounded-lg hover:bg-gray-100 transition"
            >
              <div className="w-9 h-9 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold text-sm select-none">
                {user ? getInitials(user.first_name ?? '', user.last_name ?? '') : '?'}
              </div>
              {user?.first_name && (
                <span className="text-sm font-medium text-gray-700">{user.first_name}</span>
              )}
            </button>

            {menuOpen && (
              <div className="absolute right-0 mt-2 min-w-56 bg-white rounded-lg shadow-lg z-50 py-1 border border-gray-100">
                <div className="px-4 py-3">
                  <div className="text-sm font-semibold text-gray-900">
                    {user?.first_name} {user?.last_name}
                  </div>
                  {user?.email && (
                    <div className="text-xs text-gray-500 mt-0.5">{user.email}</div>
                  )}
                </div>

                <hr className="border-gray-100" />

                {families && families.length > 0 && (
                  <>
                    <div className="px-4 py-2">
                      <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                        Current Family
                      </div>
                      {families.length === 1 ? (
                        <div className="text-sm text-gray-700">{families[0].name}</div>
                      ) : (
                        <select
                          value={selectedFamilyId ?? ''}
                          onChange={(e) => handleFamilyChange(e.target.value)}
                          className="w-full text-sm border border-gray-200 rounded-md px-2 py-1.5 bg-gray-50 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          {families.map((f) => (
                            <option key={f.id} value={f.id}>
                              {f.name}
                            </option>
                          ))}
                        </select>
                      )}
                      <button
                        onClick={handleSwitchFamily}
                        className="mt-2 text-xs text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        Switch Family
                      </button>
                    </div>
                    <hr className="border-gray-100" />
                  </>
                )}

                <div className="px-2 py-1">
                  <button
                    onClick={handleLogout}
                    disabled={logoutMutation.isPending}
                    className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-md transition disabled:opacity-50"
                  >
                    {logoutMutation.isPending ? 'Logging out...' : 'Logout'}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
