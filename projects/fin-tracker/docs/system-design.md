# System Design — fin-tracker

> **Version:** 1.1  
> **Ngày tạo:** 2026-05-02  
> **Cập nhật:** 2026-05-08

---

## 1. KIẾN TRÚC TỔNG THỂ

```
┌─────────────────────────────────────────────────┐
│                  User (Browser)                  │
└─────────────────┬───────────────────────────────┘
                   │ HTTP/HTTPS
┌─────────────────▼───────────────────────────────┐
│            React Frontend (Port 3000)            │
│     TailwindCSS + Recharts + Axios + JWT        │
└─────────────────┬───────────────────────────────┘
                   │ REST API (Bearer Token)
┌─────────────────▼───────────────────────────────┐
│           FastAPI Backend (Port 8000)            │
│     Python + PyMuPDF + Claude API + JWT Auth     │
└──────┬──────────────────────────┬───────────────┘
       │                          │
┌──────▼──────┐          ┌────────▼────────┐
│ PostgreSQL  │          │   Claude API    │
│  (Port 5432)│          │  (Anthropic)    │
└─────────────┘          └─────────────────┘
```

### Quy trình xác thực

1. User gửi `POST /api/auth/login` → nhận JWT access token
2. Frontend lưu token vào `localStorage`, kèm theo mọi request trong header `Authorization: Bearer <token>`
3. Backend xác thực token qua `get_current_user` dependency
4. Token hết hạn → frontend tự redirect về `/login`
5. Endpoint `/auth/register` và `/auth/login` là công khai; tất cả endpoint khác yêu cầu xác thực

---

## 2. TECH STACK

|Layer|Công nghệ|Version|Lý do chọn|
|---|---|---|---|
|**Frontend**|React|18.x|Component-based, ecosystem lớn|
|**UI**|TailwindCSS|3.x|Utility-first, nhanh|
|**Charts**|Recharts|2.x|Tích hợp tốt với React|
|**Routing**|React Router|6.x|SPA routing, protected routes|
|**Auth**|JWT (python-jose + bcrypt)|3.3.0 / 4.2.1| Stateless, đơn giản cho v1.0|
|**Backend**|FastAPI|0.115+|Async, tự gen API docs|
|**Language**|Python|3.12+|Ecosystem AI/ML tốt nhất|
|**Database**|PostgreSQL|15+|Dữ liệu có cấu trúc, query mạnh|
|**ORM**|SQLAlchemy|2.x|Pythonic, migration dễ|
|**PDF**|PyMuPDF|Latest|Đọc PDF nhanh, hỗ trợ scan|
|**AI**|Claude API|claude-sonnet-4-6|Phân tích tài chính, tiếng Việt|
|**Deploy**|Docker Compose|Latest|Đóng gói toàn bộ stack|
|**File Storage**|Local Volume|—|Đơn giản cho v1.0|

---

## 3. DATABASE SCHEMA

### Bảng: `users` — Người dùng

```sql
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    display_name    VARCHAR(100),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### Bảng: `companies` — Doanh nghiệp

```sql
CREATE TABLE companies (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(20) UNIQUE NOT NULL,
    name        VARCHAR(255) NOT NULL,
    exchange    VARCHAR(10) NOT NULL,        -- HOSE / HNX / UPCOM
    industry    VARCHAR(255),
    description TEXT,
    website     VARCHAR(255),
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);
```

### Bảng: `financial_periods` — Kỳ báo cáo

```sql
CREATE TABLE financial_periods (
    id          SERIAL PRIMARY KEY,
    company_id  INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    year        INTEGER NOT NULL,
    quarter     INTEGER,                       -- 1/2/3/4 hoặc NULL = cả năm
    period_type VARCHAR(10) NOT NULL,          -- 'Q' hoặc 'Y'
    created_at  TIMESTAMP DEFAULT NOW()
);
```

### Bảng: `report_files` — File PDF gốc

```sql
CREATE TABLE report_files (
    id           SERIAL PRIMARY KEY,
    period_id    INTEGER REFERENCES financial_periods(id) ON DELETE CASCADE,
    report_type  VARCHAR(20) NOT NULL,         -- KQKD/CDKT/LCTT/TM/CBTT
    file_name    VARCHAR(512) NOT NULL,
    file_path    VARCHAR(1024) NOT NULL,
    file_size    INTEGER NOT NULL,
    uploaded_at  TIMESTAMP DEFAULT NOW()
);
```

### Bảng: `financial_data` — Số liệu trích xuất

```sql
CREATE TABLE financial_data (
    id           SERIAL PRIMARY KEY,
    period_id    INTEGER REFERENCES financial_periods(id) ON DELETE CASCADE,
    report_type  VARCHAR(20) NOT NULL,
    metric_name  VARCHAR(512) NOT NULL,
    metric_value DECIMAL(24, 4) NOT NULL,
    unit         VARCHAR(64) DEFAULT 'triệu VND',
    is_verified  BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMP DEFAULT NOW()
);
```

### Bảng: `company_summaries` — Tóm tắt AI

```sql
CREATE TABLE company_summaries (
    id            SERIAL PRIMARY KEY,
    company_id    INTEGER REFERENCES companies(id) ON DELETE CASCADE UNIQUE,
    summary_text  TEXT NOT NULL,
    summary_html  TEXT NOT NULL DEFAULT '',
    generated_at  TIMESTAMP DEFAULT NOW()
);
```

### Bảng: `ai_analysis` — Phân tích AI (legacy, thay bằng `company_summaries`)

### Bảng: `alerts` — Cảnh báo

```sql
CREATE TABLE alerts (
    id           SERIAL PRIMARY KEY,
    company_id   INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    period_id    INTEGER REFERENCES financial_periods(id) ON DELETE CASCADE,
    alert_type   VARCHAR(50) NOT NULL,
    severity     VARCHAR(20) NOT NULL,
    description  TEXT NOT NULL,
    is_read      BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMP NOT NULL
);
```

### Bảng: `settings` — Cài đặt hệ thống

```sql
CREATE TABLE settings (
    key         VARCHAR(100) PRIMARY KEY,
    value       VARCHAR(500) NOT NULL,
    label       VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    updated_at  TIMESTAMP DEFAULT NOW()
);
```

**Cài đặt mặc định:**

|Key|Default|Label|Mô tả|
|---|---|---|---|
|`ai_analysis_enabled`|`true`|Bật phân tích AI|Gọi Anthropic API để phân tích BCTC, tóm tắt, so sánh|
|`ai_extraction_enabled`|`true`|Bật trích xuất AI|AI tự động trích xuất số liệu từ PDF|
|`ai_summary_enabled`|`true`|Bật tóm tắt AI|AI tạo tóm tắt tình hình kinh doanh|
|`alert_enabled`|`true`|Bật cảnh báo|Tự động kiểm tra chỉ số bất thường|

---

## 4. API ENDPOINTS

### Auth (công khai)

```
POST   /api/auth/register    → Tạo tài khoản mới
POST   /api/auth/login       → Đăng nhập, nhận JWT token
GET    /api/auth/me           → Thông tin user hiện tại (cần token)
```

### Settings (cần xác thực)

```
GET    /api/settings          → Danh sách tất cả cài đặt
PUT    /api/settings/{key}    → Cập nhật cài đặt (value: "true"/"false")
```

### Companies (cần xác thực)

```
GET    /api/companies          → Danh sách DN (có filter, search)
POST   /api/companies          → Thêm DN mới
GET    /api/companies/{id}     → Chi tiết DN
PUT    /api/companies/{id}     → Cập nhật DN
DELETE /api/companies/{id}     → Xoá DN
GET    /api/companies/{id}/summary       → Xem tóm tắt AI
POST   /api/companies/{id}/summary       → Tạo tóm tắt mới (kiểm tra ai_summary_enabled)
```

### Financial Reports (cần xác thực)

```
GET    /api/companies/{id}/periods          → Danh sách kỳ báo cáo
POST   /api/companies/{id}/periods          → Tạo kỳ mới
POST   /api/periods/{id}/upload             → Upload PDF
GET    /api/periods/{id}/files              → Danh sách file PDF
GET    /api/periods/{id}/files/{file_id}    → Xem PDF gốc (trả blob qua API)
DELETE /api/periods/{id}/files/{file_id}    → Xoá file PDF
POST   /api/periods/{id}/extract            → Trích xuất AI (kiểm tra ai_extraction_enabled)
GET    /api/periods/{id}/data                → Xem số liệu đã trích xuất
PUT    /api/periods/{id}/data/{metric_id}    → Chỉnh sửa số liệu
POST   /api/periods/{id}/verify             → Xác nhận số liệu
```

### Dashboard & Analytics (cần xác thực)

```
GET    /api/dashboard/overview               → Dữ liệu dashboard tổng quan
GET    /api/analytics/companies/{id}         → Chuỗi chỉ số theo kỳ cho 1 DN
GET    /api/analytics/compare?ids=1,2,3&year=YYYY[&quarter=Q] → So sánh chỉ số giữa các DN
```

### AI Analysis (cần xác thực)

```
GET    /api/analysis/companies/{id}/analysis  → Xem phân tích AI hiện tại
POST   /api/analysis/companies/{id}/analyze    → Chạy lại phân tích AI (kiểm tra ai_analysis_enabled)
```

### Alerts (cần xác thực)

```
GET    /api/alerts                → Danh sách cảnh báo (lọc theo company_id, is_read)
PUT    /api/alerts/{id}/read     → Đánh dấu đã đọc
PUT    /api/alerts/read-all       → Đánh dấu đã đọc toàn bộ
DELETE /api/alerts/{id}           → Xoá cảnh báo
```

---

## 5. CẤU TRÚC THƯ MỤC

```
fin-tracker/
├── docs/
│   ├── PRD.md
│   ├── system-design.md        ← File này
│   └── user-stories.md
├── src/
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── api/            → API clients (axios + JWT interceptor)
│   │   │   │   ├── client.js   → Shared axios instance with auth
│   │   │   │   ├── authApi.js
│   │   │   │   ├── settingsApi.js
│   │   │   │   ├── companyApi.js
│   │   │   │   ├── periodApi.js
│   │   │   │   ├── dashboardApi.js
│   │   │   │   ├── analyticsApi.js
│   │   │   │   ├── analysisApi.js
│   │   │   │   ├── alertsApi.js
│   │   │   │   └── summaryApi.js
│   │   │   ├── components/     → UI components
│   │   │   ├── contexts/       → React context providers
│   │   │   │   ├── AuthContext.jsx
│   │   │   │   └── AlertContext.jsx
│   │   │   ├── layouts/        → MainLayout with nav + logout
│   │   │   ├── pages/          → Trang chính
│   │   │   ├── constants/      → Static data (exchanges, reportTypes)
│   │   │   ├── App.jsx          → Routes + protected routes
│   │   │   └── main.jsx         → Entry point + AuthProvider
│   │   ├── nginx.conf
│   │   └── package.json
│   └── backend/
│       ├── app/
│       │   ├── api/
│       │   │   ├── deps.py          → Auth dependency (get_current_user)
│       │   │   └── v1/
│       │   │       ├── router.py
│       │   │       └── endpoints/
│       │   │           ├── auth.py
│       │   │           ├── settings.py
│       │   │           ├── companies.py
│       │   │           ├── periods.py
│       │   │           ├── dashboard.py
│       │   │           ├── analytics.py
│       │   │           ├── analysis.py
│       │   │           └── alerts.py
│       │   ├── core/
│       │   │   ├── config.py         → JWT_SECRET_KEY, JWT_EXPIRE_HOURS
│       │   │   └── alert_thresholds.py
│       │   ├── db/
│       │   │   └── session.py
│       │   ├── models/
│       │   │   ├── user.py
│       │   │   ├── company.py
│       │   │   ├── financial.py
│       │   │   ├── summary.py
│       │   │   ├── alert.py
│       │   │   ├── ai_analysis.py
│       │   │   └── setting.py
│       │   ├── schemas/
│       │   │   ├── auth.py
│       │   │   ├── setting.py
│       │   │   ├── company.py
│       │   │   ├── financial.py
│       │   │   ├── dashboard.py
│       │   │   ├── analysis.py
│       │   │   └── alert.py
│       │   ├── services/
│       │   │   ├── auth_service.py        → JWT + bcrypt
│       │   │   ├── settings_service.py    → is_enabled()
│       │   │   ├── company_service.py
│       │   │   ├── period_service.py
│       │   │   ├── pdf_extractor.py
│       │   │   ├── summary_service.py
│       │   │   ├── ai_analyzer.py
│       │   │   ├── analytics_service.py
│       │   │   ├── dashboard_service.py
│       │   │   └── alert_engine.py
│       │   └── main.py
│       ├── Dockerfile
│       └── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 6. BẢO MẬT & XÁC THỰC

### JWT Authentication

- ** Thuật toán:** HS256 (HMAC-SHA256)
- **Token寿命:** 24 giờ (cấu hình qua `JWT_EXPIRE_HOURS`)
- **Password hashing:** bcrypt (4.2.1)
- **Flow:**
  1. `POST /api/auth/register` → tạo user mới (công khai)
  2. `POST /api/auth/login` → trả về JWT access token (công khai)
  3. Mọi request khác → header `Authorization: Bearer <token>`
  4. Token hết hạn / không hợp lệ → HTTP 401 → frontend redirect `/login`

### CORS

- Origins được phép: `http://localhost:3000`, `http://localhost:5173` (frontend dev)
- Credentials: cho phép
- Methods: tất cả
- Headers: tất cả

### Settings Guards

Các endpoint gọi AI/API có thể bị khoá qua bảng `settings`:

|Endpoint|Setting key|Khi tắt|
|---|---|---|
|`POST /periods/{id}/extract`|`ai_extraction_enabled`|Trả về 403|
|`POST /analysis/companies/{id}/analyze`|`ai_analysis_enabled`|Trả về 403|
|`POST /companies/{id}/summary`|`ai_summary_enabled`|Trả về 403|
|Background alert check|`alert_enabled`|Bỏ qua|
|Background AI analysis|`ai_analysis_enabled`|Bỏ qua|

---

## 7. DOCKER COMPOSE

```yaml
services:
  db:
    image: postgres:15-alpine
    container_name: fin-tracker-db
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "${POSTGRES_PORT}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 10

  backend:
    build:
      context: ./src/backend
    container_name: fin-tracker-backend
    env_file:
      - .env
    ports:
      - "${BACKEND_PORT}:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./src/backend:/app
      - ./.env:/app/.env
      - fin_tracker_uploads:/app/uploads

  frontend:
    image: nginx:alpine
    container_name: fin-tracker-frontend
    ports:
      - "${FRONTEND_PORT}:80"
    depends_on:
      - backend
    volumes:
      - ./src/frontend/dist:/usr/share/nginx/html:ro
      - ./src/frontend/nginx.conf:/etc/nginx/conf.d/default.conf:ro

volumes:
  postgres_data:
  fin_tracker_uploads:
```

---

## 8. ENV VARIABLES

```env
# App
APP_NAME=fin-tracker API
ENVIRONMENT=development
API_PREFIX=/api

# Database
POSTGRES_USER=fin_user
POSTGRES_PASSWORD=fin_password
POSTGRES_DB=fin_tracker
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=3000
VITE_API_BASE_URL=http://localhost:8000

# AI — Claude (Anthropic)
CLAUDE_API_KEY=
CLAUDE_MODEL=claude-sonnet-4-6

# Auth
JWT_SECRET_KEY=change-me-in-production
JWT_EXPIRE_HOURS=24

# Upload
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_MB=50
```