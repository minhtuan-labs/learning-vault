import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from './types';

interface AuthStore {
  user: Partial<User> | null;
  selectedFamilyId: string | null;
  setUser: (user: Partial<User> | null) => void;
  setSelectedFamily: (familyId: string | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      selectedFamilyId: null,
      setUser: (user) => set({ user }),
      setSelectedFamily: (familyId) => set({ selectedFamilyId: familyId }),
      logout: () => set({ user: null, selectedFamilyId: null }),
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        user: state.user,
        selectedFamilyId: state.selectedFamilyId,
      }),
    }
  )
);

interface UIStore {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
}));
