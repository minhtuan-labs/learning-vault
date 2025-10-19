# Stage 1: Chọn một image Python gọn nhẹ làm nền tảng
FROM python:3.11-slim

# Tạo và chuyển tới thư mục làm việc trong container
WORKDIR /app

# Stage 2: Cài đặt các thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Copy source code và chạy ứng dụng
COPY . .

# Mở port 8501 để container có thể nhận request từ bên ngoài
EXPOSE 8001

# Lệnh để khởi chạy ứng dụng Streamlit khi container bắt đầu
CMD ["streamlit", "run", "Home.py", "--server.port=8001", "--server.address=0.0.0.0"]

