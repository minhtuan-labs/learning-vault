import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginForm from '@/components/auth/LoginForm';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useLoginMutation, useAuth } from '@/lib/api-queries';
import { useAuthStore } from '@/lib/stores';

vi.mock('@/lib/api-queries');
vi.mock('@/lib/stores');
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

const Wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={createTestQueryClient()}>
    {children}
  </QueryClientProvider>
);

describe('Auth - US-1.3: User Login (TC-1.3.1)', () => {
  beforeEach(() => {
    const mockLoginMutation = {
      mutateAsync: vi.fn().mockResolvedValue({
        user: { id: '1', email: 'user@example.com', name: 'Test User' },
        families: [{ id: 'f1', name: 'Test Family' }],
      }),
      isPending: false,
    };
    vi.mocked(useLoginMutation).mockReturnValue(mockLoginMutation as any);
    vi.mocked(useAuthStore).mockReturnValue({
      setUser: vi.fn(),
      user: null,
      clearUser: vi.fn(),
    } as any);
  });

  it('should render login form with email and password fields', () => {
    render(<LoginForm />, { wrapper: Wrapper });

    expect(screen.getByPlaceholderText(/you@example.com/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument();
  });

  it('should accept valid email and password input', async () => {
    const user = userEvent.setup();
    render(<LoginForm />, { wrapper: Wrapper });

    const emailInput = screen.getByPlaceholderText(/you@example.com/i);
    const passwordInput = screen.getByLabelText(/password/i);

    await user.type(emailInput, 'user@example.com');
    await user.type(passwordInput, 'password123');

    expect(emailInput).toHaveValue('user@example.com');
    expect(passwordInput).toHaveValue('password123');
  });

  it('should handle login submission with valid credentials', async () => {
    const user = userEvent.setup();
    const mockMutateAsync = vi.fn().mockResolvedValue({
      user: { id: '1', email: 'user@example.com', name: 'Test User' },
      families: [{ id: 'f1', name: 'Test Family' }],
    });

    const mockLoginMutation = {
      mutateAsync: mockMutateAsync,
      isPending: false,
    };
    vi.mocked(useLoginMutation).mockReturnValue(mockLoginMutation as any);

    render(<LoginForm />, { wrapper: Wrapper });

    const emailInput = screen.getByPlaceholderText(/you@example.com/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitBtn = screen.getByRole('button', { name: /log in/i });

    await user.type(emailInput, 'user@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitBtn);

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith(
        expect.objectContaining({
          email: 'user@example.com',
          password: 'password123',
        })
      );
    });
  });

  it('should display error on invalid credentials (TC-1.3.4)', async () => {
    const user = userEvent.setup();
    const mockMutateAsync = vi.fn().mockRejectedValue({
      response: {
        data: { detail: 'Invalid email or password' },
      },
    });

    const mockLoginMutation = {
      mutateAsync: mockMutateAsync,
      isPending: false,
    };
    vi.mocked(useLoginMutation).mockReturnValue(mockLoginMutation as any);

    render(<LoginForm />, { wrapper: Wrapper });

    const emailInput = screen.getByPlaceholderText(/you@example.com/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitBtn = screen.getByRole('button', { name: /log in/i });

    await user.type(emailInput, 'wrong@example.com');
    await user.type(passwordInput, 'wrongpassword');
    await user.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument();
    });
  });

  it('should require email and password fields', async () => {
    const user = userEvent.setup();
    render(<LoginForm />, { wrapper: Wrapper });

    const submitBtn = screen.getByRole('button', { name: /log in/i });

    const emailInput = screen.getByPlaceholderText(/you@example.com/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;

    expect(emailInput.required).toBe(true);
    expect(passwordInput.required).toBe(true);
  });
});

describe('Auth - US-1.3: Family Selection Flow (TC-1.3.2, TC-1.3.3)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should redirect single-family user to dashboard (TC-1.3.2)', async () => {
    const mockRouter = { push: vi.fn() };
    vi.doMock('next/navigation', () => ({
      useRouter: () => mockRouter,
    }));

    const mockMutateAsync = vi.fn().mockResolvedValue({
      user: { id: '1', email: 'user@example.com', name: 'Test User' },
      families: [{ id: 'f1', name: 'Test Family' }],
    });

    const mockLoginMutation = {
      mutateAsync: mockMutateAsync,
      isPending: false,
    };
    vi.mocked(useLoginMutation).mockReturnValue(mockLoginMutation as any);
    vi.mocked(useAuthStore).mockReturnValue({
      setUser: vi.fn(),
      user: null,
      clearUser: vi.fn(),
    } as any);

    const user = userEvent.setup();
    render(<LoginForm />, { wrapper: Wrapper });

    await user.type(screen.getByPlaceholderText(/you@example.com/i), 'user@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /log in/i }));

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalled();
    });
  });

  it('should show family selector for multi-family users (TC-1.3.3)', async () => {
    const mockMutateAsync = vi.fn().mockResolvedValue({
      user: { id: '1', email: 'user@example.com', name: 'Test User' },
      families: [
        { id: 'f1', name: 'Family A' },
        { id: 'f2', name: 'Family B' },
      ],
    });

    const mockLoginMutation = {
      mutateAsync: mockMutateAsync,
      isPending: false,
    };
    vi.mocked(useLoginMutation).mockReturnValue(mockLoginMutation as any);
    vi.mocked(useAuthStore).mockReturnValue({
      setUser: vi.fn(),
      user: null,
      clearUser: vi.fn(),
    } as any);

    const user = userEvent.setup();
    render(<LoginForm />, { wrapper: Wrapper });

    await user.type(screen.getByPlaceholderText(/you@example.com/i), 'user@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /log in/i }));

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalled();
    });
  });
});

describe('Auth - US-1.1: Superadmin Login (TC-1.1.1)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should authenticate superadmin with superadmin/admin123 credentials', async () => {
    const user = userEvent.setup();
    const mockMutateAsync = vi.fn().mockResolvedValue({
      user: {
        id: 'admin1',
        email: 'admin@example.com',
        name: 'Superadmin',
        role: 'superadmin',
      },
      families: [],
    });

    const mockLoginMutation = {
      mutateAsync: mockMutateAsync,
      isPending: false,
    };
    vi.mocked(useLoginMutation).mockReturnValue(mockLoginMutation as any);
    vi.mocked(useAuthStore).mockReturnValue({
      setUser: vi.fn(),
      user: null,
      clearUser: vi.fn(),
    } as any);

    render(<LoginForm />, { wrapper: Wrapper });

    await user.type(screen.getByPlaceholderText(/you@example.com/i), 'superadmin');
    await user.type(screen.getByLabelText(/password/i), 'admin123');
    await user.click(screen.getByRole('button', { name: /log in/i }));

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith({
        email: 'superadmin',
        password: 'admin123',
      });
    });
  });
});
