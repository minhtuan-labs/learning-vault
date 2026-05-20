# Business Requirements — NestFi

## Overview
NestFi is a web-based family financial management application that enables households to collectively track income, expenses, savings, and investments with categorized analytics and dashboards.

## Core Business Rules

### Multi-Tenancy & Family Hierarchy
- A single user account can belong to **multiple families** simultaneously
- Upon login, the user selects which family they wish to manage in that session
- Each family is an independent financial domain (transactions, accounts, members)
- One user account = many families; one family = many users

### Authentication & Authorization
- **Superadmin account** is pre-created at system initialization
  - Username: `superadmin`
  - Default password: `admin123`
  - Superadmin can change their password after first login
  - Superadmin can create new families and invite owners
- **Family Owner** (invited by Superadmin via email)
  - Must accept invitation via email confirmation
  - Can then add other members to the family
  - Responsible for family financial management
- **Family Member** (added by Owner)
  - Can view and manage transactions within the family
  - Full access to family financial data

### Financial Transactions & Categorization
- All income, expenses, and transfers must be **categorized**
  - Income categories (salary, bonus, investment returns, etc.)
  - Expense categories (groceries, utilities, entertainment, etc.)
  - Investment categories (stocks, bonds, real estate, etc.)
- **Special case: Cash Withdrawals**
  - ATM withdrawal is treated as an **expense transaction** with category "Cash Withdrawal"
  - The withdrawn cash itself is not tracked as an asset (cash in wallet is not in scope)
- Transactions require:
  - Amount
  - Category
  - Date
  - Optional description/notes

### Financial Accounts
- Families can maintain multiple **bank accounts** (checking, savings, investment, etc.)
- Each account tracks balance and transaction history
- Accounts are family-specific (not shared across families)

### Reporting & Analysis
- **Dashboard** provides:
  - Summary of all transactions by category
  - Income vs. Expense analysis
  - Savings tracking
  - Investment portfolio overview
  - Time-based trends and analytics

## Constraints

### Data Ownership
- All family data (transactions, accounts, members) is isolated per family
- No cross-family data sharing or consolidation
- User cannot view another family's data without being explicitly added as a member

### Security Requirements
- Email-based invitation system for family creation
- Password reset capability for all users
- Session isolation per login (one family selected at a time)

## Out of Scope (v1)

These features are deferred to future versions:
- Multi-currency support
- Investment portfolio tracking (detailed)
- Bill splitting beyond expense categorization
- Recurring transaction automation
- Mobile app (web-only for v1)
- Real-time synchronization across devices
