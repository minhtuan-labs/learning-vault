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
|**Language**|Python|3.11+|Ecosystem AI/ML tốt nhất|
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

### Bảng: `ai_analysis` — Phân tích AI

```sql
CREATE TABLE ai_analysis (
    id           SERIAL PRIMARY KEY,
    period_id    INTEGER REFERENCES financial_periods(id),
    company_id   INTEGER REFERENCES companies(id),
    analysis_type VARCHAR(50),                 -- 'summary'/'comparison'/'alert'
    content      TEXT,                         -- Nội dung phân tích tiếng Việt
    created_at   TIMESTAMP DEFAULT NOW()
);
```

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

### AI Analysis

```
POST   /api/periods/{id}/analyze            → Trigger AI phân tích
GET    /api/companies/{id}/analysis         → Xem lịch sử phân tích
POST   /api/compare                         → So sánh 2-3 DN
GET    /api/alerts                          → Danh sách cảnh báo
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
│   │   ├── public/
│   │   ├── src/
│   │   │   ├── components/     → UI components
│   │   │   ├── pages/          → Trang chính
│   │   │   ├── services/       → Gọi API
│   │   │   └── utils/
│   │   ├── package.json
│   │   └── tailwind.config.js
│   └── backend/
│       ├── app/
│       │   ├── api/            → Route handlers
│       │   ├── models/         → SQLAlchemy models
│       │   ├── services/       → Business logic
│       │   │   ├── pdf_extractor.py
│       │   │   └── ai_analyzer.py
│       │   └── database.py
│       ├── requirements.txt
│       └── main.py
├── docker/
│   ├── Dockerfile.frontend
│   ├── Dockerfile.backend
│   └── docker-compose.yml
└── README.md
```

---

## 6. DOCKER COMPOSE

```yaml
version: '3.8'
services:
  frontend:
    build:
      context: ../src/frontend
      dockerfile: ../../docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  backend:
    build:
      context: ../src/backend
      dockerfile: ../../docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/fintracker
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - db
    volumes:
      - pdf_storage:/app/uploads

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=fintracker
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
  pdf_storage:
```