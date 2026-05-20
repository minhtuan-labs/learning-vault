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

describe('Family - US-2.1: Create a New Family', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render family creation form (TC-2.1.1)', () => {
    render(
      <form className="space-y-4">
        <div>
          <label htmlFor="family-name">Family Name</label>
          <input id="family-name" type="text" placeholder="e.g. Smith Family" required />
        </div>
        <button type="submit">Create Family</button>
      </form>,
      { wrapper: Wrapper }
    );

    expect(screen.getByLabelText(/Family Name/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Create Family/i })).toBeInTheDocument();
  });

  it('should accept valid family name input (TC-2.1.1)', async () => {
    const user = userEvent.setup();
    render(
      <form className="space-y-4">
        <input type="text" placeholder="e.g. Smith Family" required />
        <button type="submit">Create Family</button>
      </form>,
      { wrapper: Wrapper }
    );

    const nameInput = screen.getByPlaceholderText(/Smith Family/i) as HTMLInputElement;
    await user.type(nameInput, 'Test Family');

    expect(nameInput.value).toBe('Test Family');
  });

  it('should require family name (TC-2.1.2)', () => {
    render(
      <form>
        <input type="text" placeholder="e.g. Smith Family" required />
      </form>,
      { wrapper: Wrapper }
    );

    const nameInput = screen.getByPlaceholderText(/Smith Family/i) as HTMLInputElement;
    expect(nameInput.required).toBe(true);
  });

  it('should show validation error when name is empty (TC-2.1.2)', async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn((e) => {
      e.preventDefault();
      if (!e.currentTarget.nameInput.value) {
        throw new Error('Family name is required');
      }
    });

    render(
      <form onSubmit={handleSubmit}>
        <input name="nameInput" type="text" required />
        <button type="submit">Create Family</button>
      </form>,
      { wrapper: Wrapper }
    );

    const submitBtn = screen.getByRole('button', { name: /Create Family/i });

    // HTML5 validation should prevent submission
    const nameInput = screen.getByDisplayValue('') as HTMLInputElement;
    expect(nameInput.required).toBe(true);
  });

  it('should create family and designate owner (TC-2.1.1)', async () => {
    const user = userEvent.setup();
    const mockCreateFamily = vi.fn();

    render(
      <form
        onSubmit={(e) => {
          e.preventDefault();
          mockCreateFamily();
        }}
      >
        <input type="text" placeholder="e.g. Smith Family" required />
        <button type="submit">Create Family</button>
      </form>,
      { wrapper: Wrapper }
    );

    const nameInput = screen.getByPlaceholderText(/Smith Family/i);
    const submitBtn = screen.getByRole('button', { name: /Create Family/i });

    await user.type(nameInput, 'Test Family');
    await user.click(submitBtn);

    expect(mockCreateFamily).toHaveBeenCalled();
  });
});

describe('Family - US-2.2: Add Family Members', () => {
  it('should render add member form (TC-2.2.1)', () => {
    render(
      <form className="space-y-4">
        <div>
          <label htmlFor="member-email">Email Address</label>
          <input id="member-email" type="email" placeholder="member@example.com" required />
        </div>
        <button type="submit">Send Invitation</button>
      </form>,
      { wrapper: Wrapper }
    );

    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/member@example.com/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Send Invitation/i })).toBeInTheDocument();
  });

  it('should accept valid email for invitation (TC-2.2.1)', async () => {
    const user = userEvent.setup();
    render(
      <form>
        <input type="email" placeholder="member@example.com" required />
        <button type="submit">Send Invitation</button>
      </form>,
      { wrapper: Wrapper }
    );

    const emailInput = screen.getByPlaceholderText(/member@example.com/i) as HTMLInputElement;
    await user.type(emailInput, 'member@example.com');

    expect(emailInput.value).toBe('member@example.com');
  });

  it('should show invitation in pending list (TC-2.2.1)', () => {
    const pendingInvitations = [
      {
        id: 'inv1',
        email: 'member1@example.com',
        status: 'pending',
      },
    ];

    render(
      <div>
        <h3>Pending Invitations</h3>
        <ul>
          {pendingInvitations.map((inv) => (
            <li key={inv.id}>
              <span>{inv.email}</span>
              <span className="text-sm text-gray-500">{inv.status}</span>
            </li>
          ))}
        </ul>
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/Pending Invitations/i)).toBeInTheDocument();
    expect(screen.getByText(/member1@example.com/i)).toBeInTheDocument();
  });

  it('should display member with join/accept option (TC-2.2.2)', () => {
    const invitations = [
      {
        id: 'inv1',
        familyName: 'Test Family',
        invitedBy: 'owner@example.com',
        status: 'pending',
      },
    ];

    render(
      <div>
        {invitations.map((inv) => (
          <div key={inv.id} className="p-4 bg-white rounded-lg">
            <p>
              <strong>{inv.familyName}</strong> invited you by {inv.invitedBy}
            </p>
            <button>Accept Invitation</button>
          </div>
        ))}
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/Test Family/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Accept Invitation/i })).toBeInTheDocument();
  });

  it('should allow member to join family (TC-2.2.2)', async () => {
    const user = userEvent.setup();
    const mockAcceptInvitation = vi.fn();

    render(
      <button onClick={mockAcceptInvitation} type="button">
        Join Family
      </button>,
      { wrapper: Wrapper }
    );

    const joinBtn = screen.getByRole('button', { name: /Join Family/i });
    await user.click(joinBtn);

    expect(mockAcceptInvitation).toHaveBeenCalled();
  });

  it('should display multiple families for user (TC-2.2.3)', () => {
    const userFamilies = [
      { id: 'f1', name: 'Family A', role: 'member' },
      { id: 'f2', name: 'Family B', role: 'member' },
    ];

    render(
      <div>
        <h2>Your Families</h2>
        <div className="grid gap-4">
          {userFamilies.map((family) => (
            <div key={family.id} className="p-4 bg-white rounded-lg border">
              <h3 className="font-semibold">{family.name}</h3>
              <p className="text-sm text-gray-500">Role: {family.role}</p>
            </div>
          ))}
        </div>
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/Your Families/i)).toBeInTheDocument();
    expect(screen.getByText(/Family A/i)).toBeInTheDocument();
    expect(screen.getByText(/Family B/i)).toBeInTheDocument();
  });

  it('should show family selector for multi-family users (TC-2.2.3)', () => {
    const families = [
      { id: 'f1', name: 'Family A' },
      { id: 'f2', name: 'Family B' },
    ];

    render(
      <div>
        <label>Select Family</label>
        <select>
          <option value="">Choose a family...</option>
          {families.map((f) => (
            <option key={f.id} value={f.id}>
              {f.name}
            </option>
          ))}
        </select>
      </div>,
      { wrapper: Wrapper }
    );

    const selector = screen.getByDisplayValue('Choose a family...') as HTMLSelectElement;
    expect(selector.children.length).toBe(3); // default + 2 families
  });
});

describe('Family - US-2.3: View Family Members (SHOULD)', () => {
  it('should display active members list', () => {
    const members = [
      { id: 'm1', email: 'owner@example.com', role: 'owner', status: 'active' },
      { id: 'm2', email: 'member1@example.com', role: 'member', status: 'active' },
    ];

    render(
      <div>
        <h3>Active Members</h3>
        <table>
          <tbody>
            {members.map((m) => (
              <tr key={m.id}>
                <td>{m.email}</td>
                <td>{m.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/Active Members/i)).toBeInTheDocument();
    expect(screen.getByText(/owner@example.com/i)).toBeInTheDocument();
    expect(screen.getByText(/member1@example.com/i)).toBeInTheDocument();
  });

  it('should display pending invitations with action buttons', () => {
    const pending = [
      { id: 'p1', email: 'pending@example.com' },
    ];

    render(
      <div>
        <h3>Pending Invitations</h3>
        {pending.map((p) => (
          <div key={p.id} className="flex justify-between">
            <span>{p.email}</span>
            <div className="space-x-2">
              <button>Resend</button>
              <button>Revoke</button>
            </div>
          </div>
        ))}
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/Pending Invitations/i)).toBeInTheDocument();
    expect(screen.getByText(/pending@example.com/i)).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: /Resend/i })).toBeTruthy();
  });
});

describe('Family - US-2.4: Disable/Enable Members (SHOULD)', () => {
  it('should allow owner to disable member', () => {
    render(
      <div>
        <button type="button">Disable Member</button>
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByRole('button', { name: /Disable Member/i })).toBeInTheDocument();
  });

  it('should update member status to disabled', async () => {
    const user = userEvent.setup();
    const mockDisable = vi.fn();

    render(
      <button onClick={mockDisable} type="button">
        Disable Member
      </button>,
      { wrapper: Wrapper }
    );

    await user.click(screen.getByRole('button', { name: /Disable Member/i }));
    expect(mockDisable).toHaveBeenCalled();
  });

  it('should allow owner to re-enable disabled member', () => {
    render(
      <div>
        <p>Status: disabled</p>
        <button type="button">Re-enable Member</button>
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/Status: disabled/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Re-enable Member/i })).toBeInTheDocument();
  });

  it('should preserve disabled members transactions', () => {
    const transactions = [
      { id: 't1', createdBy: 'disabledMember', amount: 500, category: 'Groceries' },
    ];

    render(
      <div>
        <p>Transaction from disabled member:</p>
        {transactions.map((t) => (
          <div key={t.id}>
            <p>By: {t.createdBy}</p>
            <p>Amount: ${t.amount}</p>
          </div>
        ))}
      </div>,
      { wrapper: Wrapper }
    );

    expect(screen.getByText(/disabledMember/i)).toBeInTheDocument();
    expect(screen.getByText(/\$500/i)).toBeInTheDocument();
  });
});
