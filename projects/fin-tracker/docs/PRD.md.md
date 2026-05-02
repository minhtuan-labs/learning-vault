# PRD — Hệ thống Quản lý Báo Cáo Tài Chính Doanh Nghiệp

> **Project:** fin-tracker  
> **Version:** 1.0  
> **Ngày tạo:** 2026-05-02  
> **Tác giả:** Tuan Pham (PM)

---

## 1. TỔNG QUAN SẢN PHẨM

### Vấn đề

PM/Analyst theo dõi trên 100 doanh nghiệp hiện phải:

- Tải thủ công từng file PDF BCTC từ nhiều nguồn khác nhau
- Nhập liệu tay vào Excel để so sánh
- Tốn 2-4 giờ mỗi kỳ chỉ để tổng hợp số liệu
- Khó phát hiện sớm các dấu hiệu bất thường

### Giải pháp

Hệ thống web tập trung giúp:

- Lưu trữ toàn bộ BCTC theo từng DN và từng kỳ
- AI tự động trích xuất số liệu từ PDF
- Phân tích, so sánh và cảnh báo tự động
- Trực quan hoá dữ liệu qua biểu đồ

### Mục tiêu

|Chỉ số|Hiện tại|Mục tiêu|
|---|---|---|
|Thời gian tổng hợp BCTC/kỳ|2-4 giờ|< 15 phút|
|Số DN theo dõi được|~20-30|> 100|
|Phát hiện bất thường|Thủ công|Tự động|

---

## 2. NGƯỜI DÙNG MỤC TIÊU

|Nhóm|Mô tả|Nhu cầu chính|
|---|---|---|
|**PM/Analyst**|Người theo dõi nhiều DN|Upload, xem báo cáo, nhận cảnh báo|
|**Nhà đầu tư cá nhân**|Theo dõi danh mục|So sánh DN, xem xu hướng|

---

## 3. TÍNH NĂNG CHI TIẾT

### Module 1 — Quản lý Doanh Nghiệp

- Thêm / sửa / xoá doanh nghiệp
- Thông tin lưu trữ: Mã CK, Tên DN, Sàn (HOSE/HNX/UPCOM), Ngành, Mô tả, Website
- Tìm kiếm theo tên hoặc mã CK
- Lọc theo ngành / sàn chứng khoán
- Xem tổng quan nhanh từng DN

### Module 2 — Quản lý BCTC

- Upload file PDF BCTC theo kỳ (Q1 / Q2 / Q3 / Q4 / Năm)
- Phân loại báo cáo:
    - Báo cáo Kết quả Kinh doanh (KQKD)
    - Bảng Cân đối Kế toán (CĐKT)
    - Báo cáo Lưu chuyển Tiền tệ (LCTT)
    - Thuyết minh BCTC
    - Công bố thông tin khác
- AI tự động trích xuất số liệu từ PDF
- Cho phép chỉnh sửa số liệu nếu AI trích xuất sai
- Xem lại file PDF gốc bất kỳ lúc nào

### Module 3 — Phân tích & Báo cáo AI

- **Tóm tắt kỳ:** AI tóm tắt tình hình kinh doanh bằng ngôn ngữ tự nhiên (Tiếng Việt)
- **So sánh kỳ:** Biểu đồ tăng trưởng doanh thu, lợi nhuận, dòng tiền qua các kỳ
- **So sánh DN:** Đặt 2-3 DN cạnh nhau để so sánh chỉ số
- **Cảnh báo:** Tự động phát hiện và thông báo khi có chỉ số bất thường
- **Biểu đồ:** Line chart, Bar chart, Radar chart cho các chỉ số tài chính

---

## 4. YÊU CẦU PHI CHỨC NĂNG

|Yêu cầu|Chi tiết|
|---|---|
|**Ngôn ngữ**|Tiếng Việt toàn bộ giao diện và báo cáo|
|**Hiệu năng**|Trích xuất PDF < 30 giây/file|
|**Bảo mật**|Đăng nhập cơ bản, dữ liệu private|
|**Deploy**|Docker Compose, có thể share link|
|**Trình duyệt**|Chrome, Firefox, Edge|

---

## 5. PHẠM VI NGOÀI (Out of Scope — v1.0)

- Tự động crawl BCTC từ internet
- Mobile app
- Đa người dùng / phân quyền phức tạp
- Tích hợp API chứng khoán real-time

---

## 6. LỘ TRÌNH TRIỂN KHAI

### Phase 1 — Nền tảng (MVP)

> Mục tiêu: Chạy được web app, quản lý được danh sách DN

- Setup project React + FastAPI + PostgreSQL + Docker
- CRUD Doanh nghiệp
- Giao diện danh sách DN

### Phase 2 — Upload & Trích xuất

> Mục tiêu: Upload PDF và có dữ liệu thực trong hệ thống

- Upload PDF BCTC
- AI trích xuất số liệu tự động (Claude API)
- Lưu và hiển thị số liệu đã trích xuất

### Phase 3 — Visualize

> Mục tiêu: Nhìn thấy xu hướng qua biểu đồ

- Dashboard tổng quan
- Biểu đồ doanh thu / lợi nhuận / dòng tiền
- So sánh giữa các kỳ

### Phase 4 — AI Analysis

> Mục tiêu: Hệ thống thông minh, tự phân tích

- AI tóm tắt tình hình kinh doanh
- So sánh giữa các DN
- Cảnh báo chỉ số bất thường

---

## 7. TIÊU CHÍ HOÀN THÀNH (Definition of Done)

- [ ] Thêm được DN với đầy đủ thông tin
- [ ] Upload PDF và AI trích xuất đúng số liệu chính
- [ ] Xem biểu đồ tăng trưởng theo kỳ
- [ ] AI tóm tắt được tình hình kinh doanh bằng Tiếng Việt
- [ ] Cảnh báo khi doanh thu/lợi nhuận giảm >20% so với kỳ trước
- [ ] Chạy được trên Docker, có thể share link