# P.A.M - Private Asset Management System

Dự án cá nhân nhằm xây dựng một hệ thống quản lý tài sản toàn diện, được tạo ra với mục tiêu chính là học hỏi và thực hành các công nghệ hiện đại như FastAPI, Streamlit, và Docker.

## 🎯 Mục tiêu dự án

Hệ thống **P.A.M** được thiết kế để cung cấp một cái nhìn tổng quan và chi tiết về tình hình tài sản cá nhân, giúp người dùng theo dõi sự biến động, quản lý dòng tiền và đưa ra các quyết định tài chính tốt hơn.

## ✨ Tính năng chính

### Giai đoạn 1: Chức năng cốt lõi (MVP)
- [ ] **Quản lý đa tài sản:** Theo dõi các loại tài sản khác nhau bao gồm:
    - Tiền mặt (Cash)
    - Cổ phiếu (Stocks)
    - Chứng chỉ quỹ (ETFs/Funds)
    - Tiết kiệm (Savings)
- [ ] **Theo dõi dòng tiền:** Ghi nhận và phân loại các giao dịch (nạp tiền, rút tiền, mua/bán, nhận cổ tức...).
- [ ] **Tích hợp dữ liệu Real-time:** Tự động lấy giá cổ phiếu hiện tại từ các nguồn API công khai để tính toán lãi/lỗ tạm tính.
- [ ] **Dashboard trực quan:** Cung cấp các biểu đồ (biểu đồ tròn, biểu đồ đường) để trực quan hóa tỷ trọng và sự tăng trưởng của tài sản.
- [ ] **Cảnh báo tự động:** Gửi thông báo qua **Telegram** khi giá cổ phiếu chạm đến ngưỡng giá mục tiêu (Target Price) hoặc cắt lỗ (Stop-loss).

### Giai đoạn 2: Nâng cao (Tương lai)
- [ ] **Tích hợp AI/ML:** Xây dựng và tích hợp mô hình dự báo xu hướng giá cổ phiếu.

## 🛠️ Công nghệ sử dụng

| Phần         | Công nghệ                                        |
|--------------|--------------------------------------------------|
| **Backend** | Python, FastAPI                                  |
| **Frontend** | Streamlit                                        |
| **Database** | PostgreSQL                                       |
| **Triển khai**| Docker, Docker Compose                           |
| **Thông báo** | Telegram Bot API                                 |

## 🏛️ Kiến trúc hệ thống

Dự án được xây dựng dựa trên kiến trúc microservice cơ bản, tách biệt hoàn toàn giữa Frontend và Backend:

- **Frontend (Streamlit):** Là giao diện người dùng, chịu trách nhiệm hiển thị dữ liệu và tương tác. Giao tiếp với Backend thông qua các request API.
- **Backend (FastAPI):** Là bộ não của hệ thống, xử lý toàn bộ logic nghiệp vụ, xác thực người dùng, và tương tác với cơ sở dữ liệu.
- **Database (PostgreSQL):** Lưu trữ toàn bộ dữ liệu của người dùng.
- **Telegram Worker:** Một tiến trình độc lập, chạy định kỳ để kiểm tra giá và gửi cảnh báo.

## 📁 Cấu trúc thư mục dự án

```
.
├── pam_backend/        # Source code cho Backend (FastAPI)
├── pam_frontend/       # Source code cho Frontend (Streamlit)
├── telegram_worker/    # Source code cho tiến trình gửi cảnh báo
├── docker-compose.yml  # File điều phối các container
└── README.md
```

## 🚀 Hướng dẫn cài đặt và chạy dự án

1.  **Clone repository `learning-vault`:**
    ```bash
    git clone [https://github.com/minhtuan-labs/learning-vault.git](https://github.com/minhtuan-labs/learning-vault.git)
    ```
2.  **Di chuyển vào thư mục dự án:**
    Dự án này sẽ nằm trong thư mục `projects`. Hãy di chuyển vào thư mục tương ứng:
    ```bash
    cd learning-vault/projects/pam-private-asset-management/
    ```
3.  **Tạo file biến môi trường:**
    Tạo các file `.env` trong từng thư mục service (`pam_backend`, `telegram_worker`) dựa trên các file `.env.example` (sẽ được tạo sau).

4.  **Cấu hình `docker-compose.yml`:**
    Để chạy front-end tại cổng `6868`, file `docker-compose.yml` của bạn sẽ cần cấu hình mapping port cho service `frontend` như sau:
    ```yaml
    services:
      frontend:
        build: ./pam_frontend
        ports:
          - "6868:8501" # Map cổng 6868 của máy host vào cổng 8501 của container
      # ... các services khác
    ```

5.  **Khởi chạy với Docker Compose:**
    Từ thư mục gốc của dự án P.A.M, chạy lệnh:
    ```bash
    docker-compose up --build
    ```
- **Frontend sẽ chạy tại: `http://localhost:6868`** (Lộc Phát Lộc Phát  prosperous_face:)
- Backend API sẽ chạy tại: `http://localhost:8000/docs`

## 📜 License
MIT License — for learning, research, and experimentation.

---

**Author:** *Pham Minh Tuan*  
© 2025 — *TinyChatBot: Build, Learn, Share.*
