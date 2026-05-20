export type UserRole = 'superadmin' | 'owner' | 'member' | 'viewer';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  created_at: string;
  is_superadmin?: boolean;
}

export interface Family {
  id: string;
  name: string;
  owner_id: string;
  created_at: string;
  member_count?: number;
  is_active?: boolean;
}

export interface AdminFamilyDetail {
  id: string;
  name: string;
  owner_id: string;
  owner_email: string;
  owner_name: string;
  is_active: boolean;
  created_at: string;
  member_count: number;
  members: FamilyMember[];
}

export interface FamilyMember {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  status?: 'active' | 'disabled';
  joined_at: string;
}

export type AccountType = 'bank' | 'savings' | 'investment' | 'cash';

export interface Account {
  id: string;
  family_id?: string;
  name: string;
  type: AccountType;
  balance_cents: number;
  currency: string;
  is_active?: boolean;
  created_at: string;
}

export interface DashboardRecentTransaction {
  date: string;
  description: string;
  amount_cents: number;
  direction: 'in' | 'out';
}

export interface DashboardData {
  period: string;
  total_income_cents: number;
  total_expense_cents: number;
  net_savings_cents: number;
  accounts: Array<{ id: string; name: string; balance_cents: number }>;
  recent_transactions: DashboardRecentTransaction[];
}

export interface Category {
  id: string;
  family_id: string;
  name: string;
  type: 'income' | 'expense' | 'investment';
  is_custom: boolean;
  created_at: string;
}

export interface Transaction {
  id: string;
  account_id: string;
  category_id: string;
  category_name?: string;
  account_name?: string;
  amount_cents: number;
  direction: 'in' | 'out';
  description?: string;
  date: string;
  creator_id: string;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name?: string;
    role?: UserRole;
    created_at?: string;
    is_superadmin: boolean;
  };
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}
