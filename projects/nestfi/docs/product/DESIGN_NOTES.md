# NestFi — Design System & Notes

## Brand & Visual Identity

### Logo & Naming
- **Product Name**: NestFi
- **Brand Concept**: "Nest" (family home, safety, stability) + "Fi" (finance)
- **Logo Style**: Modern, approachable; suitable for both light and dark modes
- **Logo Placement**: Top-left corner (desktop); centered on login/auth pages

### Design Philosophy
- **Principle 1**: Clarity first — financial data must be unambiguous
- **Principle 2**: Reduce friction — transaction entry should be < 30 seconds
- **Principle 3**: Inclusive — accessible to non-technical family members
- **Principle 4**: Responsive — works equally well on desktop, tablet, mobile
- **Principle 5**: Trust — professional, polished appearance; no amateur design

---

## Color Palette

### Primary Colors
- **Primary Blue**: `#0066CC` (trust, financial, professional)
  - Light variant: `#E3F2FD`
  - Dark variant: `#003D99`
- **Accent Green**: `#22C55E` (positive, income, growth)
- **Accent Red**: `#EF4444` (negative, expenses, alerts)

### Secondary/Neutral Colors
- **Background**: `#FFFFFF` (primary)
- **Surface**: `#F9FAFB` (secondary surfaces, sections)
- **Border**: `#E5E7EB` (dividers, low-contrast lines)
- **Text Primary**: `#111827` (main text)
- **Text Secondary**: `#6B7280` (helper text, labels)
- **Text Tertiary**: `#9CA3AF` (disabled, muted)
- **Hover**: `#F3F4F6` (subtle hover state)

### Semantic Colors
| Element | Light Theme | Usage |
|---------|-------------|-------|
| Income | `#22C55E` | Transaction type, positive balance |
| Expense | `#EF4444` | Transaction type, negative balance |
| Investment | `#8B5CF6` | Investment transactions, purple |
| Cash Withdrawal | `#F59E0B` | Cash out, amber |
| Neutral | `#6B7280` | Neutral categories |
| Success | `#10B981` | Confirmation, alerts |
| Warning | `#F59E0B` | Warnings |
| Error | `#EF4444` | Errors, destructive actions |

### Dark Mode (Future)
- Invert neutral scale: backgrounds dark, text light
- Primary colors remain same; tints adjusted for contrast

---

## Typography

### Font Family
- **Primary Font**: System font stack (SF Pro Display on iOS/macOS, Segoe UI on Windows, Roboto on Android fallback)
  ```css
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  ```
- **Monospace**: `SF Mono`, `Fira Code`, or system monospace (for amounts, codes)

### Type Scale

| Role | Size | Weight | Line Height | Usage |
|------|------|--------|------------|-------|
| **Hero** | 40px | 700 | 1.2 | Page titles (Dashboard heading) |
| **H1** | 32px | 700 | 1.3 | Modal titles, section headers |
| **H2** | 24px | 600 | 1.35 | Subsection headers |
| **H3** | 20px | 600 | 1.4 | Card titles, category names |
| **Subtitle** | 16px | 600 | 1.5 | Labels, form headers |
| **Body Large** | 16px | 400 | 1.5 | Primary body text, descriptions |
| **Body** | 14px | 400 | 1.5 | Standard text, list items |
| **Caption** | 12px | 400 | 1.4 | Metadata, timestamps, hints |
| **Overline** | 12px | 600 | 1.6 | Labels, badges |
| **Button** | 14px | 600 | 1 | CTA buttons, nav items |

### Text Treatments
- **Primary Text**: Color `#111827`, weight 400-600
- **Secondary Text**: Color `#6B7280`, weight 400
- **Disabled Text**: Color `#D1D5DB`, weight 400
- **Links**: Color `#0066CC`, underline on hover, weight 500
- **Amount Fields**: Use monospace, weight 600, increase size slightly (1.1em)

---

## Spacing System (8px base unit)

```
8px   (1 unit)   — padding in buttons, tight spacing
12px  (1.5 unit) — input padding, small gaps
16px  (2 units)  — standard padding, card margins
24px  (3 units)  — section padding, card spacing
32px  (4 units)  — large section gaps
48px  (6 units)  — page margins (desktop)
```

---

## Role-Based UI Patterns

### Owner-Only Actions
- Delete permanently (transaction hard-delete) — red destructive button, owner-only
- Manage members (invite, disable, enable, change roles) — settings tab
- Manage categories (create, edit, delete custom categories) — settings tab
- UI Strategy: Hide buttons from non-owners; show tooltip "Owner only" if hovering where button would be

### Member Actions (vs Viewer)
- Create transactions — visible [+ Add Transaction] button
- Edit transactions — visible [Edit] button on transaction rows
- Disable/enable transactions — visible [Disable] / [Enable] button
- UI Strategy: Hide all transaction-creation UX from Viewers; show read-only views only

### Viewer Actions
- View all data (accounts, transactions, analytics)
- No action buttons for creating/editing
- UI Strategy: Simplified UI with read-only tables and charts; no modals or forms

### Disabled Members
- Show as "Disabled" in members list with status badge
- Cannot log in (session immediately terminated)
- Their past transactions remain visible to other members
- Can be re-enabled by owner

---

### Common Patterns
- **Button**: 12px vertical, 20px horizontal padding
- **Input**: 12px padding (top/bottom), 16px (left/right)
- **Card**: 24px padding, 8px border-radius
- **Modal**: 16px padding inside modal (content area 40px padding)
- **Section gaps**: 24px (stacked cards/sections), 16px (sub-sections)

---

## Components & States

### Buttons

#### Primary Button
```
Background: #0066CC
Text: White, weight 600, size 14px
Padding: 12px 20px
Border-radius: 6px
Transition: background 200ms ease

States:
  Default:  bg-#0066CC
  Hover:    bg-#003D99
  Active:   bg-#002657
  Disabled: bg-#D1D5DB, text-#9CA3AF, cursor-not-allowed
  Loading:  spinner icon, disabled state
```

#### Secondary Button
```
Background: #F3F4F6
Text: #111827, weight 600, size 14px
Border: 1px solid #E5E7EB
Padding: 12px 20px
Border-radius: 6px

States:
  Default:  bg-#F3F4F6
  Hover:    bg-#E5E7EB
  Active:   bg-#D1D5DB
  Disabled: bg-#F9FAFB, text-#9CA3AF
```

#### Destructive Button (Delete)
```
Background: #EF4444
Text: White, weight 600
All properties same as Primary, but red-themed

States:
  Default:  bg-#EF4444
  Hover:    bg-#DC2626
  Active:   bg-#991B1B
  Disabled: bg-#FCA5A5, cursor-not-allowed
```

#### Ghost/Link Button
```
Background: transparent
Text: #0066CC, weight 500
Underline on hover
No padding; text-only

States:
  Default:  color-#0066CC, no underline
  Hover:    color-#003D99, underline
  Active:   color-#002657
  Disabled: color-#D1D5DB
```

### Form Inputs

```
Border: 1px solid #E5E7EB
Border-radius: 6px
Padding: 12px 16px
Font: 14px, #111827
Background: White

States:
  Default:    border-#E5E7EB, bg-White
  Hover:      border-#D1D5DB
  Focus:      border-#0066CC (2px), shadow-none (or soft glow: 0 0 0 3px rgba(0,102,204,0.1))
  Disabled:   bg-#F9FAFB, border-#D1D5DB, color-#9CA3AF, cursor-not-allowed
  Error:      border-#EF4444 (2px), error text below field in red
  Filled:     background-#E3F2FD (light blue tint, optional)
```

**Label**:
- Font: 14px, weight 600, color #111827
- Margin-bottom: 8px
- Required indicator: red asterisk (*) or "Required" text

**Helper Text**:
- Font: 12px, color #6B7280, weight 400
- Margin-top: 4px (optional, below input)

**Error Text**:
- Font: 12px, color #EF4444, weight 500
- Margin-top: 4px
- Example: "Email is not valid" or "Password too short (min 8 characters)"

### Checkboxes & Radio Buttons

```
Size: 18px × 18px
Border-radius: 4px (checkbox), 50% (radio)
Border: 2px solid #D1D5DB
Accent color: #0066CC when checked

States:
  Unchecked:  border-#D1D5DB, bg-White
  Hover:      border-#0066CC
  Checked:    bg-#0066CC, border-#0066CC
  Disabled:   border-#D1D5DB, bg-#F9FAFB, cursor-not-allowed
```

### Badges / Tags

```
Background: One of the semantic colors (income green, expense red, etc.)
Text: White, weight 600, size 12px
Padding: 4px 12px
Border-radius: 12px (pill-shaped)
```

**Examples**:
- Income: green badge
- Expense: red badge
- Investment: purple badge
- Member role: gray badge

### Cards & Containers

```
Background: White
Border: 1px solid #E5E7EB
Border-radius: 8px
Padding: 24px
Box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) (subtle)

Hover (if clickable):
  Box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1)
  Cursor: pointer
```

### Tables

```
Border-collapse: collapse
Row height: 44px (content height) + spacing
Border-bottom: 1px solid #E5E7EB (between rows)
Header:
  Background: #F9FAFB
  Font: weight 600, size 14px, color #6B7280
  Padding: 12px 16px
  Border-bottom: 2px solid #E5E7EB

Row hover:
  Background: #F9FAFB
```

### Modals / Dialogs

```
Overlay: rgba(0, 0, 0, 0.5) (50% opacity)
Modal container:
  Background: White
  Border-radius: 12px
  Box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15)
  Max-width: 90% (desktop: 500px typical)
  Max-height: 90vh
  Padding: 32px (title area), 24px (content)

Close button (✕):
  Top-right corner, 8px from edge
  Color: #6B7280
  Hover: #111827
```

### Alerts / Toast Messages

```
Success:
  Background: #ECFDF5 (light green)
  Border-left: 4px solid #10B981
  Text: #047857

Error:
  Background: #FEF2F2 (light red)
  Border-left: 4px solid #EF4444
  Text: #B91C1C

Warning:
  Background: #FFFBEB (light amber)
  Border-left: 4px solid #F59E0B
  Text: #92400E

Padding: 16px
Border-radius: 6px
Font-size: 14px
Auto-dismiss: 4-5 seconds (except errors)
```

### Dropdown Select

```
Border: 1px solid #E5E7EB
Border-radius: 6px
Padding: 12px 16px
Font: 14px, #111827
Background: White with dropdown arrow (right side)

Open state:
  Border: 2px solid #0066CC
  Dropdown menu appears below with z-index 1000
  Max-height: 300px (with scroll if > items)
  Menu items:
    Padding: 12px 16px
    Hover: background #F3F4F6
    Selected: background #E3F2FD, text-#0066CC
```

### Pagination

```
Centered alignment, margin-top: 24px
Buttons:
  Size: 36px × 36px (circles)
  Font: 14px, weight 500
  Border: 1px solid #E5E7EB
  Background: White

States:
  Default:    color-#111827, bg-White, cursor-pointer
  Hover:      bg-#F3F4F6, border-#D1D5DB
  Active:     bg-#0066CC, color-White, border-#0066CC
  Disabled:   color-#D1D5DB, bg-#F9FAFB, cursor-not-allowed

Example: [< Prev] [1] [2] [3] [4] [Next >]
Only show adjacent pages: [< Prev] [2] [3] [4] [5] [Next >]
```

---

## Icons & Graphics

### Icon Library
- Use a consistent icon set (e.g., Feather Icons, Heroicons, or Material Icons)
- Size: 16px (inline), 20px (UI), 24px (headers)
- Color: Inherit from text/element color
- Stroke width: 2px (for outlined icons)

### Common Icons
| Icon | Usage |
|------|-------|
| Home / Dashboard | Dashboard/home link |
| Send / Arrow Right | CTA, next action |
| Settings / Gear | Settings |
| Plus | Add item |
| Trash / X | Delete item |
| Edit / Pencil | Edit item |
| ChevronDown | Dropdown trigger |
| ChevronRight | Navigation forward |
| Eye / EyeOff | Password visibility |
| Check / Checkmark | Confirmation, done |
| X / Close | Close modal, cancel |
| Calendar | Date picker |
| Clock | Time/recent |
| Wallet / DollarSign | Finance, transactions |
| TrendingUp / Chart | Analytics, growth |
| Users | Family/members |
| Lock | Security/login |

### Charts & Visualizations
- **Pie Charts**: Use semantic colors (green for income, red for expense)
- **Bar Charts**: Use primary blue for primary metric; light blue for secondary
- **Line Charts**: Primary blue for main trend; gray for secondary
- **Legend**: Positioned below chart (mobile) or right (desktop)
- **Tooltip**: Dark background (#111827), white text, appear on hover, 200ms delay

---

## Responsiveness Breakpoints

```
Mobile:      < 768px
Tablet:      768px - 1199px
Desktop:     1200px+
Large:       1600px+
```

### Adjustments per Breakpoint

| Element | Mobile | Tablet | Desktop |
|---------|--------|--------|---------|
| Page padding | 16px | 24px | 48px |
| Sidebar | Hidden (hamburger) | Visible | Fixed 250px |
| Card width | Full | ~90% | 300-400px |
| Table | Card view or scroll | Scroll X | Full view |
| Modal | Full-screen | 90% | 500px |
| Font sizes | -2px (body) | standard | standard |
| Button padding | 10px 16px | 12px 20px | 12px 20px |

---

## Animations & Transitions

### Duration & Easing
```
Fast:      200ms, ease-out (interactions, hover states)
Normal:    300ms, ease-in-out (modal open/close, page transitions)
Slow:      500ms, ease-in-out (enter animations)
Easing:    cubic-bezier(0.4, 0, 0.2, 1) (material standard)
```

### Transition Examples
- **Button hover**: background 200ms ease-out
- **Input focus**: border 200ms ease-out, box-shadow 200ms ease-out
- **Modal enter**: opacity 300ms + scale (from 0.95) 300ms
- **Toast enter**: slideIn 300ms ease-out
- **Page transition**: opacity 200ms (if SPA)

---

## UI Visibility & Conditional Components

### Role-Based Feature Visibility

Each component/feature should be conditionally visible based on user role:

| Feature | Superadmin | Owner | Member | Viewer |
|---------|-----------|-------|--------|--------|
| Create Family | ✓ | - | - | - |
| Invite Members | - | ✓ | - | - |
| Disable/Enable Members | - | ✓ | - | - |
| Change Member Role | - | ✓ | - | - |
| Create Transactions | - | ✓ | ✓ | - |
| Edit Transactions | - | ✓ | ✓ | - |
| Disable/Enable Transactions | - | ✓ | ✓ | - |
| Hard-Delete Transactions | - | ✓ | - | - |
| Manage Categories | - | ✓ | - | - |
| View All Data | - | ✓ | ✓ | ✓ |
| View Edit History | - | ✓ | ✓ | ✓ |

### Implementation Strategy

For each role-restricted feature:

1. **Default**: Hide the component/button
2. **On Load**: Check user role from auth context/API response
3. **Conditional Render**: Only show if user has permission
4. **Hover/Tooltip** (Optional): Show "Owner only" tooltip where button would be
5. **API Protection**: Backend enforces authorization (don't rely on frontend hiding)

### Examples

```jsx
// Owner-only delete button
{user.role === 'owner' && (
  <Button variant="destructive" onClick={handleDelete}>
    Delete Permanently
  </Button>
)}

// Member & Owner can create transactions
{['owner', 'member'].includes(user.role) && (
  <Button onClick={handleAddTransaction}>
    + Add Transaction
  </Button>
)}

// All roles can view
<TransactionList transactions={transactions} />
```

---

## Accessibility Checklist

### Visual
- [ ] Color contrast: WCAG AA minimum (4.5:1 for text, 3:1 for graphics)
- [ ] Non-reliant on color alone: icons, borders, patterns also indicate state
- [ ] Focus visible: 2-3px border or glow around interactive elements
- [ ] Font size: minimum 14px for body text (12px acceptable for captions)
- [ ] Line height: minimum 1.4

### Interactive
- [ ] Keyboard navigation: Tab, Shift+Tab, Enter, Escape functional
- [ ] Tab order: logical flow (left→right, top→bottom)
- [ ] Focus trap: modals trap focus until closed
- [ ] Link underlines: visible or sufficient color contrast to distinguish

### Semantic
- [ ] Form labels: `<label>` associated with `<input>` via `for` attribute
- [ ] Buttons: semantic `<button>` tag, not styled divs
- [ ] Headings: proper hierarchy (H1→H2→H3, no skipping)
- [ ] Lists: use `<ul>`, `<ol>`, `<li>` for lists
- [ ] ARIA: use aria-labels where visual context insufficient
  - Example: `aria-label="Close modal"` for icon-only button

### Content
- [ ] Alt text: all images have descriptive alt text
- [ ] Form errors: visible and descriptive ("Email invalid" not just red border)
- [ ] Validation: inline feedback as user types, not just on submit
- [ ] Error recovery: users can easily correct and resubmit

### Screen Reader
- [ ] Form fields: labels are announced
- [ ] Icons: meaningful icons have aria-labels
- [ ] Tables: headers associated with cells (`<th scope="col">`)
- [ ] Modals: announced with `role="dialog"` + `aria-labelledby`
- [ ] Alerts: announced immediately with `role="alert"` + `aria-live="polite"`

---

## Localization Notes (Future)

While MVP is English, consider:
- **Text expansion**: Vietnamese can be 30-40% longer; leave margin in UI
- **Directionality**: English (LTR); future Vietnamese also LTR
- **Date format**: Align with locale (e.g., DD/MM/YYYY for Vietnam)
- **Currency**: Vietnamese Dong (VND) display format; future multi-currency
- **Numbers**: Decimal separator varies by locale (. vs ,)

---

## File & Code Conventions

### CSS Variables (Recommended)
```css
:root {
  /* Colors */
  --color-primary: #0066CC;
  --color-primary-light: #E3F2FD;
  --color-primary-dark: #003D99;
  --color-success: #22C55E;
  --color-error: #EF4444;
  --color-warning: #F59E0B;
  
  /* Spacing */
  --spacing-xs: 8px;
  --spacing-sm: 12px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Typography */
  --font-primary: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: "SF Mono", "Fira Code", monospace;
  --font-size-body: 14px;
  --font-size-h1: 32px;
  
  /* Transitions */
  --transition-fast: 200ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 300ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Component Naming
- Use BEM or similar: `.button`, `.button--primary`, `.button--disabled`
- Or Tailwind/utility classes if using that approach
- Keep class names semantic (`.card`, not `.blue-box`)

### File Organization
```
frontend/
├── public/
├── src/
│  ├── assets/
│  │  ├── logos/
│  │  ├── icons/
│  │  └── images/
│  ├── components/
│  │  ├── Button.tsx
│  │  ├── Input.tsx
│  │  ├── Card.tsx
│  │  └── ...
│  ├── pages/
│  │  ├── Login.tsx
│  │  ├── Dashboard.tsx
│  │  └── ...
│  ├── styles/
│  │  ├── variables.css
│  │  ├── globals.css
│  │  └── ...
│  └── utils/
└── ...
```

---

## Testing & QA Checklist

- [ ] Responsive design tested on Chrome, Firefox, Safari, Edge
- [ ] Mobile tested on actual devices (not just browser DevTools)
- [ ] Accessibility tested with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Keyboard navigation: all interactive elements accessible
- [ ] Forms: validation messages clear and helpful
- [ ] Error states: visually distinct from success/neutral
- [ ] Loading states: spinners/indicators show progress
- [ ] Performance: images optimized; CSS/JS minified
- [ ] Copy: proofread for typos, consistent tone

---

## Notes for Frontend Developer

1. **Build System**: Consider Vite for fast development; Next.js if SSR needed.
2. **State Management**: React Context + custom hooks sufficient for MVP; Redux optional.
3. **Form Handling**: React Hook Form + Zod for schema validation.
4. **Styling**: Tailwind CSS recommended for rapid prototyping; pure CSS also acceptable.
5. **Charts**: Use Recharts or Chart.js for analytics views.
6. **Icons**: Heroicons or Feather Icons recommended.
7. **Responsive**: Mobile-first CSS strategy; use rem/em units for scalability.
8. **Testing**: Jest + React Testing Library for component tests; Cypress for E2E.
9. **Accessibility**: Axe DevTools browser extension during development.
10. **Performance**: Lighthouse audit target: 80+ score on Performance, Accessibility.

---

## Design Debt & Future Improvements

- [ ] Dark mode support (design in progress)
- [ ] High-contrast mode (WCAG AAA compliance)
- [ ] Print-friendly styles for reports/statements
- [ ] Improved mobile-first optimizations (currently desktop-first)
- [ ] Animation preferences (reduce motion support)
- [ ] Custom branding per deployment (white-labeling)
- [ ] Advanced data visualization (d3.js custom charts)
