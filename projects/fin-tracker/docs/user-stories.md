# User Stories — fin-tracker

> **Version:** 1.0 | **Ngày tạo:** 2026-05-02

---

## MODULE 1 — Quản lý Doanh Nghiệp

### US-01: Thêm doanh nghiệp mới

**Là** PM, **tôi muốn** thêm doanh nghiệp mới vào hệ thống  
**để** bắt đầu theo dõi BCTC của doanh nghiệp đó

**Acceptance Criteria:**

- [x] Form nhập: Mã CK (_), Tên DN (_), Sàn, Ngành, Mô tả, Website
- [x] Mã CK không được trùng với DN đã có
- [x] Sau khi thêm, chuyển tới trang chi tiết DN
- [x] Hiển thị thông báo thành công

---

### US-02: Xem danh sách doanh nghiệp

**Là** PM, **tôi muốn** xem danh sách tất cả DN đang theo dõi  
**để** có cái nhìn tổng quan

**Acceptance Criteria:**

- [x] Hiển thị dạng bảng: Mã CK, Tên, Sàn, Ngành, Số kỳ báo cáo
- [x] Tìm kiếm theo tên hoặc mã CK
- [x] Lọc theo sàn (HOSE/HNX/UPCOM) và ngành
- [x] Phân trang khi có > 20 DN

---

### US-03: Sửa / Xoá doanh nghiệp

**Là** PM, **tôi muốn** cập nhật hoặc xoá DN  
**để** giữ dữ liệu chính xác

**Acceptance Criteria:**

- [x] Sửa được tất cả thông tin trừ Mã CK
- [x] Xoá DN yêu cầu xác nhận trước khi thực hiện
- [x] Khi xoá DN, toàn bộ BCTC liên quan cũng bị xoá

---

## MODULE 2 — Quản lý BCTC

### US-04: Upload PDF BCTC

**Là** PM, **tôi muốn** upload file PDF BCTC cho DN theo từng kỳ  
**để** lưu trữ tập trung

**Acceptance Criteria:**

- [ ] Chọn DN, năm, quý (hoặc cả năm), loại báo cáo
- [ ] Chấp nhận file PDF, tối đa 50MB
- [ ] Hiển thị progress bar khi upload
- [ ] Có thể upload nhiều loại báo cáo cho cùng 1 kỳ
- [ ] Xem lại file PDF gốc sau khi upload

---

### US-05: AI trích xuất số liệu tự động

**Là** PM, **tôi muốn** hệ thống tự động đọc và trích xuất số liệu từ PDF  
**để** không phải nhập tay

**Acceptance Criteria:**

- [ ] Sau upload, AI tự động trích xuất trong vòng 30 giây
- [ ] Hiển thị số liệu đã trích xuất để review
- [ ] Cho phép chỉnh sửa thủ công nếu AI sai
- [ ] Đánh dấu "đã xác nhận" sau khi review xong
- [ ] Trích xuất được các chỉ số chính: Doanh thu, Lợi nhuận, Tổng tài sản, Nợ, Dòng tiền

---

### US-06: Xem lịch sử BCTC theo DN

**Là** PM, **tôi muốn** xem toàn bộ lịch sử BCTC của 1 DN  
**để** theo dõi tiến trình theo thời gian

**Acceptance Criteria:**

- [ ] Danh sách kỳ báo cáo sắp xếp theo thời gian mới nhất
- [ ] Hiển thị trạng thái: Đã upload / Đã trích xuất / Đã xác nhận
- [ ] Click vào kỳ để xem chi tiết số liệu

---

## MODULE 3 — Phân tích & Báo cáo AI

### US-07: AI tóm tắt tình hình kinh doanh

**Là** PM, **tôi muốn** AI tóm tắt tình hình kinh doanh của DN sau mỗi kỳ  
**để** nhanh chóng nắm bắt tình hình mà không đọc toàn bộ BCTC

**Acceptance Criteria:**

- [ ] Tóm tắt bằng Tiếng Việt, dễ hiểu
- [ ] Đề cập các điểm nổi bật: doanh thu, lợi nhuận, dòng tiền
- [ ] So sánh với kỳ trước nếu có dữ liệu
- [ ] Độ dài khoảng 200-300 từ

---

### US-08: Biểu đồ xu hướng tài chính

**Là** PM, **tôi muốn** xem biểu đồ doanh thu/lợi nhuận qua các kỳ  
**để** nhìn thấy xu hướng phát triển

**Acceptance Criteria:**

- [ ] Line chart doanh thu thuần qua các kỳ
- [ ] Bar chart lợi nhuận sau thuế
- [ ] Chart dòng tiền từ hoạt động kinh doanh
- [ ] Có thể lọc theo khoảng thời gian (1 năm / 3 năm / toàn bộ)

---

### US-09: So sánh giữa các doanh nghiệp

**Là** PM, **tôi muốn** so sánh chỉ số tài chính của 2-3 DN cùng ngành  
**để** đánh giá tương quan

**Acceptance Criteria:**

- [ ] Chọn 2-3 DN để so sánh
- [ ] Chọn kỳ so sánh (cùng kỳ)
- [ ] Hiển thị bảng so sánh các chỉ số chính
- [ ] Biểu đồ radar so sánh đa chiều

---

### US-10: Cảnh báo chỉ số bất thường

**Là** PM, **tôi muốn** nhận cảnh báo khi có chỉ số tài chính bất thường  
**để** phát hiện sớm rủi ro

**Acceptance Criteria:**

- [ ] Cảnh báo khi doanh thu giảm > 20% so với kỳ trước
- [ ] Cảnh báo khi lợi nhuận âm
- [ ] Cảnh báo khi nợ/tài sản tăng đột biến > 30%
- [ ] Hiển thị danh sách cảnh báo trên dashboard
- [ ] Đánh dấu "đã đọc" cho từng cảnh báo