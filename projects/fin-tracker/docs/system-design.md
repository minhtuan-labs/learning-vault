# System Design — fin-tracker

> **Version:** 1.0  
> **Ngày tạo:** 2026-05-02

---

## 1. KIẾN TRÚC TỔNG THỂ

```
┌─────────────────────────────────────────────────┐
│                  User (Browser)                  │
└─────────────────┬───────────────────────────────┘
                  │ HTTP/HTTPS
┌─────────────────▼───────────────────────────────┐
│            React Frontend (Port 3000)            │
│         TailwindCSS + Recharts + Axios           │
└─────────────────┬───────────────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────────────┐
│           FastAPI Backend (Port 8000)            │
│        Python + PyMuPDF + Claude API             │
└──────┬──────────────────────────┬───────────────┘
       │                          │
┌──────▼──────┐          ┌────────▼────────┐
│ PostgreSQL  │          │   Claude API    │
│  (Port 5432)│          │  (Anthropic)    │
└─────────────┘          └─────────────────┘
```

---

## 2. TECH STACK

|Layer|Công nghệ|Version|Lý do chọn|
|---|---|---|---|
|**Frontend**|React|18.x|Component-based, ecosystem lớn|
|**UI**|TailwindCSS|3.x|Utility-first, nhanh|
|**Charts**|Recharts|2.x|Tích hợp tốt với React|
|**Backend**|FastAPI|0.110+|Async, tự gen API docs|
|**Language**|Python|3.12+|Ecosystem AI/ML tốt nhất|
|**Database**|PostgreSQL|15+|Dữ liệu có cấu trúc, query mạnh|
|**ORM**|SQLAlchemy|2.x|Pythonic, migration dễ|
|**PDF**|PyMuPDF|Latest|Đọc PDF nhanh, hỗ trợ scan|
|**AI**|Claude API|claude-3-5-sonnet|Phân tích tài chính, tiếng Việt|
|**Deploy**|Docker Compose|Latest|Đóng gói toàn bộ stack|
|**File Storage**|Local Volume|—|Đơn giản cho v1.0|

---

## 3. DATABASE SCHEMA

### Bảng: `companies` — Doanh nghiệp

```sql
CREATE TABLE companies (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(10) UNIQUE NOT NULL,  -- Mã CK: VNM, FPT...
    name        VARCHAR(255) NOT NULL,         -- Tên DN
    exchange    VARCHAR(10),                   -- HOSE / HNX / UPCOM
    industry    VARCHAR(100),                  -- Ngành
    description TEXT,                          -- Mô tả
    website     VARCHAR(255),
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);
```

### Bảng: `financial_periods` — Kỳ báo cáo

```sql
CREATE TABLE financial_periods (
    id          SERIAL PRIMARY KEY,
    company_id  INTEGER REFERENCES companies(id),
    year        INTEGER NOT NULL,              -- 2024
    quarter     INTEGER,                       -- 1/2/3/4 hoặc NULL = cả năm
    period_type VARCHAR(10) NOT NULL,          -- 'Q' hoặc 'Y'
    created_at  TIMESTAMP DEFAULT NOW()
);
```

### Bảng: `report_files` — File PDF gốc

```sql
CREATE TABLE report_files (
    id           SERIAL PRIMARY KEY,
    period_id    INTEGER REFERENCES financial_periods(id),
    report_type  VARCHAR(20) NOT NULL,         -- KQKD/CDKT/LCTT/TM/CBTT
    file_name    VARCHAR(255),
    file_path    VARCHAR(500),
    file_size    INTEGER,
    uploaded_at  TIMESTAMP DEFAULT NOW()
);
```

### Bảng: `financial_data` — Số liệu trích xuất

```sql
CREATE TABLE financial_data (
    id           SERIAL PRIMARY KEY,
    period_id    INTEGER REFERENCES financial_periods(id),
    report_type  VARCHAR(20) NOT NULL,
    metric_name  VARCHAR(255) NOT NULL,        -- "Doanh thu thuần"
    metric_value DECIMAL(20, 2),               -- 1234567890.00
    unit         VARCHAR(20) DEFAULT 'VND',    -- VND / tỷ VND
    is_verified  BOOLEAN DEFAULT FALSE,        -- Đã kiểm tra thủ công chưa
    created_at   TIMESTAMP DEFAULT NOW()
);
```

### Bảng: `company_summaries` — Tóm tắt AI

```sql
CREATE TABLE company_summaries (
    id            SERIAL PRIMARY KEY,
    company_id    INTEGER REFERENCES companies(id) ON DELETE CASCADE UNIQUE,
    summary_text  TEXT NOT NULL,
    generated_at  TIMESTAMP DEFAULT NOW()
);
```

### Bảng: `ai_analysis` — Phân tích AI (đã loại bỏ, thay bằng `company_summaries`)

### Bảng: `alerts` — Cảnh báo

```sql
CREATE TABLE alerts (
    id           SERIAL PRIMARY KEY,
    company_id   INTEGER REFERENCES companies(id),
    period_id    INTEGER REFERENCES financial_periods(id),
    metric_name  VARCHAR(255),
    alert_type   VARCHAR(50),                  -- 'decrease'/'anomaly'
    description  TEXT,
    is_read      BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMP DEFAULT NOW()
);
```

---

## 4. API ENDPOINTS

### Companies

```
GET    /api/companies          → Danh sách DN (có filter, search)
POST   /api/companies          → Thêm DN mới
GET    /api/companies/{id}     → Chi tiết DN
PUT    /api/companies/{id}     → Cập nhật DN
DELETE /api/companies/{id}     → Xoá DN
```

### Financial Reports

```
GET    /api/companies/{id}/periods          → Danh sách kỳ báo cáo
POST   /api/companies/{id}/periods          → Tạo kỳ mới
POST   /api/periods/{id}/upload             → Upload PDF
GET    /api/periods/{id}/data               → Xem số liệu đã trích xuất
PUT    /api/periods/{id}/data/{metric_id}   → Chỉnh sửa số liệu
```

### AI Summary & Analytics

```
GET    /api/companies/{id}/summary         → Xem tóm tắt AI
POST   /api/companies/{id}/summary         → Tạo tóm tắt mới bằng AI
GET    /api/analytics/dashboard            → Dữ liệu dashboard tổng quan
GET    /api/analytics/compare              → So sánh chỉ số giữa các DN
```

---

## 5. CẤU TRÚC THƯ MỤC

```
fin-tracker/
├── docs/
│   ├── PRD.md
│   ├── system-design.md        ← File này
│   ├── user-stories.md
│   └── test-cases.md
├── src/
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── api/            → API clients (axios)
│   │   │   ├── components/     → UI components
│   │   │   ├── pages/          → Trang chính
│   │   │   └── utils/
│   │   ├── Dockerfile
│   │   └── package.json
│   └── backend/
│       ├── app/
│       │   ├── api/            → Route handlers
│       │   ├── models/         → SQLAlchemy models
│       │   ├── schemas/        → Pydantic schemas
│       │   ├── services/       → Business logic
│       │   │   ├── pdf_extractor.py
│       │   │   ├── summary_service.py
│       │   │   ├── analytics_service.py
│       │   │   └── dashboard_service.py
│       │   └── main.py
│       ├── Dockerfile
│       └── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## 6. DOCKER COMPOSE

```yaml
services:
  db:
    image: postgres:15-alpine
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

  backend:
    build: ./src/backend
    environment:
      UPLOAD_DIR: /app/uploads
    ports:
      - "${BACKEND_PORT}:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./src/backend:/app
      - fin_tracker_uploads:/app/uploads

  frontend:
    build: ./src/frontend
    environment:
      VITE_API_BASE_URL: ${VITE_API_BASE_URL}
    ports:
      - "${FRONTEND_PORT}:5173"
    depends_on:
      - backend
    volumes:
      - ./src/frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
  fin_tracker_uploads:
```