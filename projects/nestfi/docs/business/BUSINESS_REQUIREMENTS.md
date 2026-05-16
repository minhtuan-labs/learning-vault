# Business Requirements — NestFi

## 1. Executive Summary

NestFi is a web-based family financial management platform enabling households to collaboratively track, categorize, and analyze their finances in real-time. The platform serves couples, families, and multi-generational households needing unified financial visibility across multiple families and accounts.

## 2. Business Objectives

- Enable families to centralize financial tracking across household income and expenses
- Provide real-time visibility into spending patterns and financial health
- Support multi-family account management for users with multiple households
- Establish secure, scalable family financial management infrastructure

## 3. Functional Requirements

### 3.1 User Management
- **Superadmin Account**: Default credentials provided (superadmin/admin123) with password change capability
- **Family Creation**: Superadmin creates families and invites initial owners via email
- **Email-based Invitation**: Owner accepts invitation to join family; non-acceptance tracked
- **Multi-family Support**: Single user can belong to and manage multiple families
- **Family Switching**: User switches between families after login
- **Member Invitation**: Owners add family members by email invitation after accepting family invitation

### 3.2 Financial Tracking
- **Transaction Logging**: Family members log purchases, income, and cash withdrawals
- **Category Management**: Families manage custom categories for:
  - Income (e.g., salary, bonuses, interest)
  - Expenses (e.g., groceries, utilities, rent)
  - Investments
  - Cash Withdrawal (treated as expense category)
- **Bank Account Management**: Families manage and track multiple bank accounts
- **Transaction Categories**: Each transaction assigned to a category; categories generate statistics

### 3.3 Dashboard & Analytics
- **Financial Overview**: Dashboard displays spending trends, savings rate, investment performance
- **Category Statistics**: Automatic statistics generation per category for analysis
- **Real-time Updates**: All family members see consistent transaction data immediately
- **Multi-family View**: Users can access separate dashboards per family

### 3.4 Financial Management Sections
- Bank Accounts: Create, list, manage family bank accounts
- Income Categories: Configure custom income categories
- Expense Categories: Configure custom expense categories (including "Cash Withdrawal")
- Investment Categories: Configure custom investment categories

## 4. Non-functional Requirements

### 4.1 Security & Compliance
- Email verification required for invitations and account changes
- Secure password handling (e.g., hashing, secure storage)
- Family-level access control (members can only see their family's data)

### 4.2 Performance & Usability
- Family members can log in and view household financial overview within 2 minutes
- All family members see consistent transaction data (no stale reads)
- Dashboard loads within 3 seconds for typical household (100-1000 transactions)

### 4.3 Deployment
- Web-based platform (desktop-first, responsive design for tablets)
- No mobile app in v1

## 5. Data & Integrity

- **Family-scoped Access**: Users can only see/modify data for families they belong to
- **Transactional Consistency**: All family members see the same transaction data at all times
- **Category Ownership**: Categories belong to families, not individuals
- **Multi-currency**: Not in scope for v1 (assumption: single currency per family)

## 6. Business Rules

### 6.1 Account & Family Management
- Superadmin is the only role that creates families
- Each family has at least one owner who accepts the initial invitation
- Owners can invite additional members; invitees can accept/decline
- Users must belong to at least one family; can belong to multiple families
- Deleting a family requires explicit confirmation

### 6.2 Financial Operations
- Cash withdrawals are transactions with category "Cash Withdrawal" (treated as expense)
- All transactions must have a category; categories are family-specific
- Categories can be created/edited/deleted only by family owners (or superadmin)
- Income, expenses, and investments are tracked separately for analysis

### 6.3 Dashboard & Reporting
- Statistics are calculated from transactions tagged with each category
- Empty categories appear on the list but contribute zero to statistics
- Historical data is never deleted (only marked as inactive for categories)

## 7. Out of Scope — v1

- Budget tracking and alerts
- Investment portfolio tracking
- Financial goal setting
- Automated categorization suggestions
- Bill splitting among family members
- Financial reports and exports
- Mobile app
- Multi-currency support
- Tax reporting integration
- Advanced analytics (ML predictions)

## 8. Success Metrics

- Family members can log in and view household financial overview within 2 minutes
- All family members see consistent transaction data
- Categories enable meaningful spending analysis
- User retention: week 1 and month 1

## 9. Dependencies & Assumptions

- **Tech Stack**: To be confirmed by SA (no tech preference specified by user)
- **Budget**: Not specified (assume startup/self-funded)
- **Timeline**: Not specified
- **Users**: Assume target users have joint bank accounts or significant shared financial management needs
- **Email**: Assume reliable email delivery for invitations

## 10. Open Business Questions

1. Multi-currency support needed beyond v1?
2. Bill splitting feature scope for v1 vs v2?
3. Analytics depth: basic charts vs advanced ML predictions?
4. Tax reporting integration needed?
5. Data retention policy: how long to keep transaction history?
6. Minimum family size enforcement: can solo users join?
