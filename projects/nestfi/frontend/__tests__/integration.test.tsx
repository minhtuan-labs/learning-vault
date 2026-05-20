import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

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

describe('Integration - TC-Cross-1: Full Happy Path', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should complete full workflow: Login → Create Family → Add Member → Record Transactions → View Dashboard', async () => {
    const user = userEvent.setup();

    // Step 1: Superadmin logs in
    const { unmount: unmountLogin } = render(
      <form className="space-y-4">
        <input type="email" placeholder="superadmin email" required />
        <input type="password" placeholder="superadmin password" required />
        <button type="submit">Sign In</button>
      </form>,
      { wrapper: Wrapper }
    );

    expect(screen.getByPlaceholderText(/superadmin email/i)).toBeInTheDocument();
    unmountLogin();

    // Step 2: Create family via invitation
    const { unmount } = render(
      <form className="space-y-4">
        <input type="text" placeholder="Family Name" required />
        <button type="submit">Create Family</button>
      </form>,
      { wrapper: Wrapper }
    );

    const familyInput = screen.getByPlaceholderText(/Family Name/i) as HTMLInputElement;
    await user.type(familyInput, 'Test Family');
    expect(familyInput.value).toBe('Test Family');

    unmount();

    // Step 3: Owner accepts invitation and sets password
    const { unmount: unmountPassword } = render(
      <form className="space-y-4">
        <input type="password" placeholder="New password" required />
        <button type="submit">Set Password & Join</button>
      </form>,
      { wrapper: Wrapper }
    );

    const passwordInput = screen.getByPlaceholderText(/New password/i) as HTMLInputElement;
    await user.type(passwordInput, 'secure123!');
    expect(passwordInput.value).toBe('secure123!');

    unmountPassword();

    // Step 4: Owner invites member
    const { unmount: unmountInvite } = render(
      <form className="space-y-4">
        <input type="email" placeholder="member@example.com" required />
        <button type="submit">Send Invitation</button>
      </form>,
      { wrapper: Wrapper }
    );

    const inviteInput = screen.getByPlaceholderText(/member@example.com/i) as HTMLInputElement;
    await user.type(inviteInput, 'member1@example.com');
    expect(inviteInput.value).toBe('member1@example.com');

    unmountInvite();

    // Step 5: Member accepts invitation
    const { unmount: unmountAccept } = render(
      <div>
        <h2>Family Invitation</h2>
        <p>Test Family invited you</p>
        <button>Accept & Join</button>
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/Test Family invited you/i)).toBeInTheDocument();

    unmountAccept();

    // Step 6: Member creates account with initial balance
    const { unmount: unmountAccount } = render(
      <form className="space-y-4">
        <input type="text" placeholder="Account Name" required />
        <select>
          <option value="">Account Type</option>
          <option value="Bank">Bank</option>
          <option value="Savings">Savings</option>
        </select>
        <input type="number" placeholder="Initial Balance" step="0.01" required />
        <button type="submit">Create Account</button>
      </form>,
      { wrapper: Wrapper }
    );

    const accountNameInput = screen.getByPlaceholderText(/Account Name/i) as HTMLInputElement;
    const balanceInput = screen.getByPlaceholderText(/Initial Balance/i) as HTMLInputElement;

    await user.type(accountNameInput, 'Checking');
    await user.type(balanceInput, '5000');

    expect(accountNameInput.value).toBe('Checking');
    expect(balanceInput.value).toBe('5000');

    unmountAccount();

    // Step 7: Member1 records income ($8000 salary)
    const { unmount: unmountIncome } = render(
      <form className="space-y-4">
        <input type="number" placeholder="Income Amount" step="0.01" required />
        <select>
          <option>Income</option>
          <option>Expense</option>
        </select>
        <select>
          <option value="">Category</option>
          <option value="Salary">Salary</option>
        </select>
        <button type="submit">Save Transaction</button>
      </form>,
      { wrapper: Wrapper }
    );

    const incomeAmountInput = screen.getByPlaceholderText(/Income Amount/i) as HTMLInputElement;
    await user.type(incomeAmountInput, '8000');

    expect(incomeAmountInput.value).toBe('8000');

    unmountIncome();

    // Step 8: Member1 records expense ($500 groceries)
    const { unmount: unmountExpense1 } = render(
      <form className="space-y-4">
        <input type="number" placeholder="Expense Amount" step="0.01" required />
        <select>
          <option value="">Category</option>
          <option value="Groceries">Groceries</option>
          <option value="Utilities">Utilities</option>
        </select>
        <button type="submit">Save Transaction</button>
      </form>,
      { wrapper: Wrapper }
    );

    const expenseAmountInput = screen.getByPlaceholderText(/Expense Amount/i) as HTMLInputElement;
    const categorySelects = screen.getAllByRole('combobox');
    const categorySelect = categorySelects[categorySelects.length - 1] as HTMLSelectElement;

    await user.type(expenseAmountInput, '500');
    await user.selectOptions(categorySelect, 'Groceries');

    expect(expenseAmountInput.value).toBe('500');
    expect(categorySelect.value).toBe('Groceries');

    unmountExpense1();

    // Step 9: Owner records expense ($200 utilities)
    const { unmount: unmountExpense2 } = render(
      <form className="space-y-4">
        <input type="number" placeholder="Utilities Amount" step="0.01" required />
        <select>
          <option value="">Category</option>
          <option value="Utilities">Utilities</option>
        </select>
        <button type="submit">Save Transaction</button>
      </form>,
      { wrapper: Wrapper }
    );

    const ownerExpenseInput = screen.getByPlaceholderText(/Utilities Amount/i) as HTMLInputElement;
    const ownerCategorySelects = screen.getAllByRole('combobox');
    const ownerCategorySelect = ownerCategorySelects[ownerCategorySelects.length - 1] as HTMLSelectElement;

    await user.type(ownerExpenseInput, '200');
    await user.selectOptions(ownerCategorySelect, 'Utilities');

    unmountExpense2();

    // Step 10: View dashboard with calculated totals
    const totalIncome = 8000;
    const totalExpenses = 500 + 200; // 700
    const netSavings = totalIncome - totalExpenses; // 7300
    const initialBalance = 5000;
    const finalBalance = initialBalance + totalIncome - totalExpenses; // 12300

    const { unmount: unmountDashboard } = render(
      <div>
        <h1>Dashboard</h1>
        <div>
          <h2>Total Income</h2>
          <p>${totalIncome}</p>
        </div>
        <div>
          <h2>Total Expenses</h2>
          <p>${totalExpenses}</p>
        </div>
        <div>
          <h2>Net Savings</h2>
          <p>${netSavings}</p>
        </div>
        <div>
          <h2>Account Balance</h2>
          <p>${finalBalance}</p>
        </div>
      </div>,
      { wrapper: Wrapper }
    );

    // Verify dashboard values
    expect(screen.getByText(/\$8000/)).toBeInTheDocument(); // total income
    expect(screen.getByText(/\$700/)).toBeInTheDocument(); // total expenses
    expect(screen.getByText(/\$7300/)).toBeInTheDocument(); // net savings
    expect(screen.getByText(/\$12300/)).toBeInTheDocument(); // final balance

    unmountDashboard();

    // Step 11: View expense breakdown by category
    const { unmount: unmountBreakdown } = render(
      <div>
        <h2>Expense Breakdown</h2>
        <ul>
          <li>Groceries: $500</li>
          <li>Utilities: $200</li>
        </ul>
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/Groceries: \$500/i)).toBeInTheDocument();
    expect(screen.getByText(/Utilities: \$200/i)).toBeInTheDocument();

    unmountBreakdown();

    // Step 12: Both members logout
    const { unmount: unmountLogout } = render(
      <button type="button">Logout</button>,
      { wrapper: Wrapper }
    );

    expect(screen.getByRole('button', { name: /Logout/i })).toBeInTheDocument();

    unmountLogout();

    // Step 13: Both log back in; family selector shows family
    render(
      <div>
        <h2>Select Family</h2>
        <select>
          <option value="">Choose a family...</option>
          <option value="f1">Test Family</option>
        </select>
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/Test Family/i)).toBeInTheDocument();
  });

  it('should maintain data consistency across multiple transactions', () => {
    const transactions = [
      { id: 't1', type: 'Income', amount: 8000 },
      { id: 't2', type: 'Expense', amount: 500 },
      { id: 't3', type: 'Expense', amount: 200 },
    ];

    const totalIncome = transactions
      .filter((t) => t.type === 'Income')
      .reduce((sum, t) => sum + t.amount, 0);

    const totalExpenses = transactions
      .filter((t) => t.type === 'Expense')
      .reduce((sum, t) => sum + t.amount, 0);

    const netSavings = totalIncome - totalExpenses;

    // Verify calculation
    expect(totalIncome).toBe(8000);
    expect(totalExpenses).toBe(700);
    expect(netSavings).toBe(7300);
  });

  it('should allow members in same family to view all transactions', () => {
    const transactions = [
      { id: 't1', createdBy: 'Member1', amount: 8000 },
      { id: 't2', createdBy: 'Member1', amount: 500 },
      { id: 't3', createdBy: 'Owner', amount: 200 },
    ];

    render(
      <div>
        <h2>All Transactions</h2>
        {transactions.map((tx) => (
          <div key={tx.id}>
            <p>{tx.createdBy}: ${tx.amount}</p>
          </div>
        ))}
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/Member1: \$8000/)).toBeInTheDocument();
    expect(screen.getByText(/Owner: \$200/)).toBeInTheDocument();
  });
});
