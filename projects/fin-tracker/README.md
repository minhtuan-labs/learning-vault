# fin-tracker

Hệ thống quản lý báo cáo tài chính doanh nghiệp.

## Current Scope

- CRUD doanh nghiệp niêm yết
- Tìm kiếm và lọc theo sàn/ngành
- Upload và trích xuất PDF BCTC bằng AI
- Dashboard phân tích tài chính và so sánh DN
- AI tóm tắt tình hình kinh doanh (Claude API)
- Kiến trúc tách lớp rõ ràng cho frontend/backend
- Chạy đồng bộ bằng Docker Compose (frontend + backend + postgres)

## Tech Stack

- Frontend: React 18 + TailwindCSS + Vite + Recharts
- Backend: FastAPI + SQLAlchemy
- AI: Claude API (Anthropic)
- Database: PostgreSQL 15
- Deploy local: Docker Compose

## Cấu trúc thư mục

```text
fin-tracker/
├── docker-compose.yml
├── .env.example
├── docs/
│   ├── PRD.md
│   ├── system-design.md
│   └── user-stories.md
├── src/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── db/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   └── services/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── frontend/
│       ├── src/
│       │   ├── api/
│       │   ├── components/
│       │   ├── pages/
│       │   └── utils/
│       ├── Dockerfile
│       └── package.json
└── README.md
```

## API Endpoints

### Companies
- `GET /api/companies` - danh sách doanh nghiệp, có `search`, `exchange`, `industry`
- `POST /api/companies` - thêm doanh nghiệp mới
- `GET /api/companies/{id}` - chi tiết doanh nghiệp
- `PUT /api/companies/{id}` - cập nhật doanh nghiệp
- `DELETE /api/companies/{id}` - xoá doanh nghiệp

### Periods & Reports
- `GET /api/companies/{id}/periods` - danh sách kỳ báo cáo
- `POST /api/companies/{id}/periods` - tạo kỳ báo cáo mới
- `POST /api/periods/{id}/upload` - upload PDF BCTC
- `GET /api/periods/{id}/data` - xem số liệu đã trích xuất

### Analytics & AI
- `GET /api/companies/{id}/summary` - xem tóm tắt AI
- `POST /api/companies/{id}/summary` - tạo tóm tắt mới bằng AI
- `GET /api/analytics/dashboard` - dữ liệu dashboard tổng quan
- `GET /api/analytics/compare` - so sánh chỉ số giữa các DN

## Chạy project

```bash
cp .env.example .env
docker compose up --build
```

Sau khi chạy:

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)