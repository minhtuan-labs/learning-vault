'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/stores';

export default function Home() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    const hasAuthCookie = document.cookie.split(';').some((c) => c.trim().startsWith('auth_token='));
    if (user || hasAuthCookie) {
      router.push('/dashboard');
    } else {
      router.push('/login');
    }
  }, [user, router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">NestFi</h1>
        <p className="text-gray-600">Loading...</p>
      </div>
    </div>
  );
}
