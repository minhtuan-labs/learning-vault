'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useFamilies } from '@/lib/api-queries';
import { useAuthStore } from '@/lib/stores';

export default function FamilySelectionPage() {
  const router = useRouter();
  const { data: families = [], isLoading } = useFamilies();
  const setSelectedFamily = useAuthStore((state) => state.setSelectedFamily);

  useEffect(() => {
    if (!isLoading && families.length === 1) {
      setSelectedFamily(families[0].id);
      router.push('/dashboard');
    }
  }, [isLoading, families, setSelectedFamily, router]);

  const handleSelectFamily = (familyId: string) => {
    setSelectedFamily(familyId);
    router.push('/dashboard');
  };

  if (isLoading) {
    return <div className="text-center text-gray-600">Loading families...</div>;
  }

  if (families.length === 0) {
    return (
      <div className="text-center text-gray-600 py-4">
        You have not been invited to any family yet. Please contact your administrator.
      </div>
    );
  }

  if (families.length === 1) {
    return <div className="text-center text-gray-600">Redirecting...</div>;
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6 text-center text-gray-900">
        Select Family
      </h2>
      <div className="space-y-3">
        {families.map((family) => (
          <button
            key={family.id}
            onClick={() => handleSelectFamily(family.id)}
            className="w-full p-4 border border-gray-300 rounded-lg hover:bg-blue-50 hover:border-blue-500 text-left transition"
          >
            <div className="font-medium text-gray-900">{family.name}</div>
            <div className="text-sm text-gray-500">
              {family.member_count || 0} members
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
