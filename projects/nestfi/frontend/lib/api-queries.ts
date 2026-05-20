import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api-client';
import type {
  User,
  Family,
  FamilyMember,
  Account,
  Category,
  Transaction,
  DashboardData,
  AuthResponse,
  LoginRequest,
  RegisterRequest,
} from './types';

export const queryKeys = {
  auth: {
    me: () => ['auth', 'me'],
  },
  families: {
    all: () => ['families'],
    detail: (id: string) => ['families', id],
    members: (id: string) => ['families', id, 'members'],
    accounts: (id: string) => ['families', id, 'accounts'],
    categories: (id: string) => ['families', id, 'categories'],
    dashboard: (id: string, period: string) => ['families', id, 'dashboard', period],
  },
  transactions: {
    byAccount: (familyId: string, accountId: string) => [
      'families',
      familyId,
      'accounts',
      accountId,
      'transactions',
    ],
    detail: (familyId: string, accountId: string, txId: string) => [
      'families',
      familyId,
      'accounts',
      accountId,
      'transactions',
      txId,
    ],
  },
};

// Auth queries
export const useAuth = () =>
  useQuery({
    queryKey: queryKeys.auth.me(),
    queryFn: async () => {
      const res = await apiClient.get<User>('/auth/me');
      return res.data;
    },
    retry: 1,
  });

export const useLoginMutation = () => {
  return useMutation({
    mutationFn: async (data: LoginRequest) => {
      const res = await apiClient.post<AuthResponse>('/auth/login', data);
      return res.data;
    },
  });
};

export const useRegisterMutation = () => {
  return useMutation({
    mutationFn: async (data: RegisterRequest) => {
      const res = await apiClient.post<User>('/auth/register', data);
      return res.data;
    },
  });
};

export const useLogoutMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      localStorage.removeItem('auth_token');
      document.cookie = 'auth_token=; path=/; max-age=0; SameSite=Lax';
      queryClient.clear();
    },
  });
};

// Family queries
export const useFamilies = () =>
  useQuery({
    queryKey: queryKeys.families.all(),
    queryFn: async () => {
      const res = await apiClient.get<{ families: Family[] }>('/families');
      return res.data.families || res.data;
    },
  });

export const useFamily = (id: string) =>
  useQuery({
    queryKey: queryKeys.families.detail(id),
    queryFn: async () => {
      const res = await apiClient.get<Family>(`/families/${id}`);
      return res.data;
    },
    enabled: !!id,
  });

export const useFamilyMembers = (familyId: string) =>
  useQuery({
    queryKey: queryKeys.families.members(familyId),
    queryFn: async () => {
      const res = await apiClient.get<{ members: FamilyMember[] }>(
        `/families/${familyId}/members`
      );
      return res.data.members ?? [];
    },
    enabled: !!familyId,
  });

// Dashboard query
export const useDashboard = (familyId: string, period = 'month') =>
  useQuery({
    queryKey: queryKeys.families.dashboard(familyId, period),
    queryFn: async () => {
      const res = await apiClient.get<DashboardData>(
        `/families/${familyId}/dashboard?period=${period}`
      );
      return res.data;
    },
    enabled: !!familyId,
  });

// Account queries
export const useAccounts = (familyId: string) =>
  useQuery({
    queryKey: queryKeys.families.accounts(familyId),
    queryFn: async () => {
      const res = await apiClient.get<{ accounts: Account[] }>(
        `/families/${familyId}/accounts`
      );
      return res.data.accounts ?? [];
    },
    enabled: !!familyId,
  });

export const useCreateAccountMutation = (familyId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: {
      name: string;
      type: string;
      initial_balance_cents: number;
      currency: string;
    }) => {
      const res = await apiClient.post<Account>(
        `/families/${familyId}/accounts`,
        data
      );
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.families.accounts(familyId),
      });
    },
  });
};

export const useUpdateAccountMutation = (familyId: string, accountId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: { name?: string; type?: string }) => {
      const res = await apiClient.put<Account>(
        `/families/${familyId}/accounts/${accountId}`,
        data
      );
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.families.accounts(familyId),
      });
    },
  });
};

// Category queries
export const useCategories = (familyId: string) =>
  useQuery({
    queryKey: queryKeys.families.categories(familyId),
    queryFn: async () => {
      const res = await apiClient.get<{ categories: Category[] }>(
        `/families/${familyId}/categories`
      );
      return res.data.categories ?? [];
    },
    enabled: !!familyId,
  });

// Transaction queries
export const useTransactions = (familyId: string, accountId: string) =>
  useQuery({
    queryKey: queryKeys.transactions.byAccount(familyId, accountId),
    queryFn: async () => {
      const res = await apiClient.get<{ transactions: Transaction[]; total_count: number; has_more: boolean }>(
        `/families/${familyId}/accounts/${accountId}/transactions`
      );
      return res.data.transactions ?? [];
    },
    enabled: !!familyId && !!accountId,
  });

export const useCreateTransactionMutation = (
  familyId: string,
  accountId: string
) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<Transaction>) => {
      const res = await apiClient.post<Transaction>(
        `/families/${familyId}/accounts/${accountId}/transactions`,
        data
      );
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.transactions.byAccount(familyId, accountId),
      });
    },
  });
};

export const useUpdateTransactionMutation = (
  familyId: string,
  accountId: string,
  txId: string
) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<Transaction>) => {
      const res = await apiClient.put<Transaction>(
        `/families/${familyId}/accounts/${accountId}/transactions/${txId}`,
        data
      );
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.transactions.byAccount(familyId, accountId),
      });
    },
  });
};

export const useToggleTransactionMutation = (familyId: string, accountId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ txId, is_enabled }: { txId: string; is_enabled: boolean }) => {
      const res = await apiClient.patch<{ id: string; is_enabled: boolean }>(
        `/families/${familyId}/accounts/${accountId}/transactions/${txId}`,
        { is_enabled }
      );
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.transactions.byAccount(familyId, accountId),
      });
    },
  });
};

export const useDeleteTransactionMutation = (familyId: string, accountId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (txId: string) => {
      await apiClient.delete(
        `/families/${familyId}/accounts/${accountId}/transactions/${txId}`
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.transactions.byAccount(familyId, accountId),
      });
    },
  });
};

export const useCreateMemberMutation = (familyId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: {
      email: string;
      first_name: string;
      last_name: string;
      password: string;
    }) => {
      const res = await apiClient.post<FamilyMember>(
        `/families/${familyId}/members`,
        data
      );
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.families.members(familyId),
      });
    },
  });
};

export const useToggleMemberMutation = (familyId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ userId, status }: { userId: string; status: 'active' | 'disabled' }) => {
      const res = await apiClient.patch<{ user_id: string; status: string }>(
        `/families/${familyId}/members/${userId}`,
        { status }
      );
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.families.members(familyId),
      });
    },
  });
};

export const useCreateCategoryMutation = (familyId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: {
      name: string;
      type: 'income' | 'expense' | 'investment';
    }) => {
      const res = await apiClient.post<Category>(
        `/families/${familyId}/categories`,
        data
      );
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.families.categories(familyId),
      });
    },
  });
};
