'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/common/Navbar';
import Sidebar from '@/components/common/Sidebar';
import { useAuthStore, useUIStore } from '@/lib/stores';

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const sidebarOpen = useUIStore((state) => state.sidebarOpen);
  const selectedFamilyId = useAuthStore((s) => s.selectedFamilyId);
  const router = useRouter();

  useEffect(() => {
    if (!selectedFamilyId) {
      router.replace('/family-selection');
    }
  }, [selectedFamilyId, router]);

  if (!selectedFamilyId) {
    return null;
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-0'
        } bg-gray-900 text-white transition-all duration-300 overflow-hidden`}
      >
        <Sidebar />
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-auto">
          <div className="p-8">{children}</div>
        </main>
      </div>
    </div>
  );
}
