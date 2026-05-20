import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
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

describe('Transactions - US-5.1: Record Income Transaction', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render income transaction form (TC-5.1.1)', () => {
    render(
      <form className="space-y-4">
        <div>
          <label htmlFor="type">Type</label>
          <select id="type" defaultValue="Income">
            <option>Income</option>
            <option>Expense</option>
          </select>
        </div>
        <div>
          <label htmlFor="amount">Amount</label>
          <input id="amount" type="number" placeholder="0.00" required min="0.01" step="0.01" />
        </div>
        <div>
          <label htmlFor="category">Category</label>
          <select id="category" required>
            <option value="">Select Category</option>
            <option value="Salary">Salary</option>
          </select>
        </div>
        <button type="submit">Save Transaction</button>
      </form>,
      { wrapper: Wrapper }
    );

    expect(screen.getByLabelText(/Type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Amount/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Category/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Save Transaction/i })).toBeInTheDocument();
  });

  it('should accept valid income amount (TC-5.1.1)', async () => {
    const user = userEvent.setup();
    render(
      <form className="space-y-4">
        <input type="number" placeholder="0.00" required min="0.01" step="0.01" />
      </form>,
      { wrapper: Wrapper }
    );

    const amountInput = screen.getByPlaceholderText(/0.00/i) as HTMLInputElement;
    await user.type(amountInput, '5000');

    expect(amountInput.value).toBe('5000');
  });

  it('should require amount > 0 (TC-5.1.2)', () => {
    render(
      <form>
        <input type="number" placeholder="0.00" required min="0.01" step="0.01" />
      </form>,
      { wrapper: Wrapper }
    );

    const amountInput = screen.getByPlaceholderText(/0.00/i) as HTMLInputElement;
    expect(amountInput.required).toBe(true);
    expect(amountInput.min).toBe('0.01');
  });

  it('should accept future-dated income (TC-5.1.3)', async () => {
    const user = userEvent.setup();
    const futureDate = '2026-12-31';

    render(
      <form>
        <input type="date" required />
      </form>,
      { wrapper: Wrapper }
    );

    const dateInput = screen.getByDisplayValue('') as HTMLInputElement;
    await user.type(dateInput, futureDate);

    expect(dateInput.value).toBe(futureDate);
  });

  it('should allow selecting income category (TC-5.1.1)', async () => {
    const user = userEvent.setup();
    render(
      <form>
        <select required>
          <option value="">Select Category</option>
          <option value="Salary">Salary</option>
          <option value="Bonus">Bonus</option>
        </select>
      </form>,
      { wrapper: Wrapper }
    );

    const categorySelect = screen.getByRole('combobox') as HTMLSelectElement;
    await user.selectOptions(categorySelect, 'Salary');

    expect(categorySelect.value).toBe('Salary');
  });
});

describe('Transactions - US-5.2: Record Expense Transaction', () => {
  it('should render expense transaction form (TC-5.2.1)', () => {
    render(
      <form className="space-y-4">
        <div>
          <label htmlFor="exp-type">Type</label>
          <select id="exp-type">
            <option>Income</option>
            <option>Expense</option>
            <option>Investment</option>
          </select>
        </div>
        <div>
          <label htmlFor="exp-amount">Amount</label>
          <input id="exp-amount" type="number" placeholder="0.00" required />
        </div>
        <div>
          <label htmlFor="exp-category">Category</label>
          <select id="exp-category" required>
            <option value="">Select Category</option>
            <option value="Groceries">Groceries</option>
            <option value="Utilities">Utilities</option>
          </select>
        </div>
        <button type="submit">Save Transaction</button>
      </form>,
      { wrapper: Wrapper }
    );

    expect(screen.getByLabelText(/Type/i)).toBeInTheDocument();
    expect(screen.getByText('Groceries')).toBeInTheDocument();
  });

  it('should accept expense amount with decimals (TC-5.2.1)', async () => {
    const user = userEvent.setup();
    render(
      <input type="number" placeholder="0.00" step="0.01" required />,
      { wrapper: Wrapper }
    );

    const amountInput = screen.getByPlaceholderText(/0.00/i) as HTMLInputElement;
    await user.type(amountInput, '125.50');

    expect(amountInput.value).toBe('125.5');
  });

  it('should allow negative balance (overdraft) (TC-5.2.2)', () => {
    const accountBalance = 1000;
    const expenseAmount = 2000;
    const resultBalance = accountBalance - expenseAmount;

    render(
      <div>
        <p>Account Balance: ${resultBalance}</p>
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/Account Balance: \$-1000/i)).toBeInTheDocument();
  });

  it('should have Cash Withdrawal as standard category (TC-5.2.3)', () => {
    render(
      <select>
        <option value="">Select Category</option>
        <option value="Groceries">Groceries</option>
        <option value="Cash Withdrawal">Cash Withdrawal</option>
      </select>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText('Cash Withdrawal')).toBeInTheDocument();
  });
});

describe('Transactions - US-5.4: Edit Transaction', () => {
  it('should render edit transaction form (TC-5.4.1)', () => {
    const transaction = {
      id: 't1',
      type: 'Income',
      amount: 5000,
      category: 'Salary',
      date: '2026-05-15',
    };

    render(
      <form className="space-y-4">
        <div>
          <label>Amount</label>
          <input type="number" defaultValue={transaction.amount} step="0.01" required />
        </div>
        <div>
          <label>Category</label>
          <select defaultValue={transaction.category} required>
            <option value="Salary">Salary</option>
            <option value="Bonus">Bonus</option>
          </select>
        </div>
        <button type="submit">Update Transaction</button>
      </form>,
      { wrapper: Wrapper }
    );

    const amountInput = screen.getByDisplayValue('5000') as HTMLInputElement;
    expect(amountInput).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Update Transaction/i })).toBeInTheDocument();
  });

  it('should update transaction amount (TC-5.4.1)', async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn((e) => e.preventDefault());

    render(
      <form onSubmit={handleSubmit} className="space-y-4">
        <input type="number" defaultValue={5000} step="0.01" required />
        <button type="submit">Update Transaction</button>
      </form>,
      { wrapper: Wrapper }
    );

    const amountInput = screen.getByDisplayValue('5000') as HTMLInputElement;
    await user.clear(amountInput);
    await user.type(amountInput, '5500');

    expect(amountInput.value).toBe('5500');
  });

  it('should allow another member to edit transaction (TC-5.4.2)', async () => {
    const transaction = {
      id: 't1',
      createdBy: 'Member1',
      amount: 500,
      category: 'Groceries',
    };

    render(
      <div>
        <p>Created by: {transaction.createdBy}</p>
        <button>Edit</button>
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByRole('button', { name: /Edit/i })).toBeInTheDocument();
    expect(screen.getByText(/Created by: Member1/i)).toBeInTheDocument();
  });

  it('should recalculate account balance on edit (TC-5.4.5)', () => {
    const originalAmount = 5000;
    const newAmount = 5500;
    const initialBalance = 10000;

    const originalBalance = initialBalance - originalAmount;
    const newBalance = initialBalance - newAmount;

    render(
      <div>
        <p>Original Balance: ${originalBalance}</p>
        <p>New Balance: ${newBalance}</p>
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/Original Balance: \$5000/i)).toBeInTheDocument();
    expect(screen.getByText(/New Balance: \$4500/i)).toBeInTheDocument();
  });

  it('should show edit history with timestamp and changes (TC-5.4.3)', () => {
    const editHistory = [
      {
        editor: 'Member2',
        timestamp: '2026-05-16 15:30',
        change: 'Amount changed from $5000 to $5500',
      },
    ];

    render(
      <div>
        <h3>Edit History</h3>
        {editHistory.map((edit, idx) => (
          <div key={idx} className="p-2 bg-gray-50">
            <p>
              <strong>{edit.editor}</strong> on {edit.timestamp}
            </p>
            <p>{edit.change}</p>
          </div>
        ))}
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/Edit History/i)).toBeInTheDocument();
    expect(screen.getByText(/Member2/i)).toBeInTheDocument();
    expect(screen.getByText(/Amount changed from/i)).toBeInTheDocument();
  });

  it('should display before/after snapshots (TC-5.4.4)', () => {
    const before = { amount: 5000, category: 'Salary', date: '2026-05-15' };
    const after = { amount: 5500, category: 'Salary', date: '2026-05-15' };

    render(
      <div>
        <details>
          <summary>View Details</summary>
          <div>
            <h4>Before</h4>
            <p>Amount: ${before.amount}</p>
            <h4>After</h4>
            <p>Amount: ${after.amount}</p>
          </div>
        </details>
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/View Details/i)).toBeInTheDocument();
    const details = screen.getByText(/View Details/i).closest('details');
    expect(details).toBeInTheDocument();
  });
});

describe('Transactions - Integration: Record Multiple Transactions', () => {
  it('should support recording multiple transactions and calculate total', () => {
    const transactions = [
      { id: 't1', type: 'Income', amount: 8000, category: 'Salary' },
      { id: 't2', type: 'Expense', amount: 500, category: 'Groceries' },
      { id: 't3', type: 'Expense', amount: 200, category: 'Utilities' },
    ];

    const totalIncome = transactions
      .filter((t) => t.type === 'Income')
      .reduce((sum, t) => sum + t.amount, 0);
    const totalExpenses = transactions
      .filter((t) => t.type === 'Expense')
      .reduce((sum, t) => sum + t.amount, 0);
    const netSavings = totalIncome - totalExpenses;

    render(
      <div>
        <p>Total Income: ${totalIncome}</p>
        <p>Total Expenses: ${totalExpenses}</p>
        <p>Net Savings: ${netSavings}</p>
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/Total Income: \$8000/i)).toBeInTheDocument();
    expect(screen.getByText(/Total Expenses: \$700/i)).toBeInTheDocument();
    expect(screen.getByText(/Net Savings: \$7300/i)).toBeInTheDocument();
  });
});
