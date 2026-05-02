# 📊 fin-tracker

> Hệ thống Quản lý Báo Cáo Tài Chính Doanh Nghiệp

Ứng dụng web giúp lưu trữ, số hoá và phân tích BCTC của các doanh nghiệp niêm yết trên thị trường chứng khoán Việt Nam.

---

## ✨ Tính năng

- 🏢 Quản lý danh sách doanh nghiệp theo mã chứng khoán
- 📄 Upload và lưu trữ BCTC dạng PDF theo từng kỳ
- 🤖 AI tự động trích xuất số liệu từ PDF (Claude API)
- 📈 Biểu đồ xu hướng doanh thu, lợi nhuận, dòng tiền
- 🔍 So sánh chỉ số tài chính giữa các doanh nghiệp
- 🚨 Cảnh báo tự động khi có chỉ số bất thường
- 📝 AI tóm tắt tình hình kinh doanh bằng Tiếng Việt

---

## 🛠️ Tech Stack

|Layer|Công nghệ|
|---|---|
|Frontend|React 18 + TailwindCSS + Recharts|
|Backend|Python FastAPI|
|Database|PostgreSQL 15|
|AI|Claude API (Anthropic)|
|Deploy|Docker Compose|

---

## 🚀 Chạy project

### Yêu cầu

- Docker & Docker Compose
- Anthropic API Key

### Các bước

```bash
# 1. Clone repo
git clone https://github.com/minhtuan-labs/learning-vault.git
cd learning-vault/projects/fin-tracker

# 2. Tạo file .env
cp .env.example .env
# Điền ANTHROPIC_API_KEY vào file .env

# 3. Chạy Docker
docker-compose -f docker/docker-compose.yml up -d

# 4. Mở trình duyệt
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

---

## 📁 Cấu trúc thư mục

```
fin-tracker/
├── docs/           → Tài liệu BA/SA
├── src/
│   ├── frontend/   → React app
│   └── backend/    → FastAPI
├── docker/         → Docker config
└── README.md
```

---

## 📋 Tài liệu

- [PRD — Product Requirements](https://claude.ai/chat/docs/PRD.md)
- [System Design](https://claude.ai/chat/docs/system-design.md)
- [User Stories](https://claude.ai/chat/docs/user-stories.md)
- [Test Cases](https://claude.ai/chat/docs/test-cases.md)

---

## 🗺️ Lộ trình

- [x] Phase 1 — Setup + CRUD Doanh nghiệp
- [ ] Phase 2 — Upload PDF + AI trích xuất
- [ ] Phase 3 — Dashboard + Charts
- [ ] Phase 4 — AI Analysis + Cảnh báo

---

_Tác giả: Tuan Pham | FPT IS_