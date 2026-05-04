# fin-tracker

Hệ thống quản lý báo cáo tài chính doanh nghiệp.

## Phase 1 Scope

- CRUD doanh nghiệp niêm yết
- Tìm kiếm và lọc theo sàn/ngành
- Kiến trúc tách lớp rõ ràng cho frontend/backend
- Chạy đồng bộ bằng Docker Compose (frontend + backend + postgres)

## Tech Stack

- Frontend: React 18 + TailwindCSS + Vite
- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL 15
- Deploy local: Docker Compose

## Cấu trúc thư mục

```text
fin-tracker/
├── docker-compose.yml
├── .env.example
├── src/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── db/
│   │   │   ├── models/
│   │   │   ├── repositories/
│   │   │   ├── schemas/
│   │   │   └── services/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── frontend/
│       ├── src/
│       │   ├── api/
│       │   ├── components/
│       │   ├── constants/
│       │   ├── layouts/
│       │   └── pages/
│       ├── Dockerfile
│       └── package.json
└── README.md
```

## API Phase 1

- `GET /api/companies` - danh sách doanh nghiệp, có `search`, `exchange`, `industry`
- `POST /api/companies` - thêm doanh nghiệp mới
- `GET /api/companies/{id}` - chi tiết doanh nghiệp
- `PUT /api/companies/{id}` - cập nhật doanh nghiệp
- `DELETE /api/companies/{id}` - xoá doanh nghiệp

## Chạy project

```bash
cp .env.example .env
docker compose up --build
```

Sau khi chạy:

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)