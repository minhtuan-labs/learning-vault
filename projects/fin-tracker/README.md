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
- `GET /api/periods/{id}/files` - danh sách file PDF của kỳ
- `POST /api/periods/{id}/upload` - upload PDF BCTC
- `GET /api/periods/{id}/files/{file_id}` - xem PDF gốc (inline)
- `DELETE /api/periods/{id}/files/{file_id}` - xoá file PDF
- `POST /api/periods/{id}/extract` - trích xuất số liệu (Claude); chạy alert + AI analysis ở background
- `GET /api/periods/{id}/data` - xem số liệu đã trích xuất
- `PUT /api/periods/{id}/data/{metric_id}` - chỉnh sửa số liệu
- `POST /api/periods/{id}/verify` - đánh dấu toàn bộ số liệu trong kỳ là đã kiểm tra

### Dashboard & Analytics
- `GET /api/dashboard/overview` - dữ liệu dashboard tổng quan
- `GET /api/analytics/companies/{id}` - chuỗi chỉ số theo kỳ cho 1 DN
- `GET /api/analytics/compare?ids=1,2,3&year=YYYY[&quarter=Q]` - so sánh chỉ số giữa các DN

### AI Analysis
- `GET /api/analysis/companies/{id}/analysis` - xem tóm tắt AI hiện tại của DN
- `POST /api/analysis/companies/{id}/analyze` - chạy lại tóm tắt AI (background)

### Alerts
- `GET /api/alerts` - danh sách cảnh báo (lọc theo `company_id`, `is_read`)
- `PUT /api/alerts/{id}/read` - đánh dấu đã đọc
- `PUT /api/alerts/read-all` - đánh dấu đã đọc toàn bộ
- `DELETE /api/alerts/{id}` - xoá cảnh báo

## Chạy project

```bash
cp .env.example .env
docker compose up --build
```

Sau khi chạy:

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)