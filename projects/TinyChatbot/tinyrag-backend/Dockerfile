# Sử dụng một base image Python chính thức
FROM python:3.13

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Sao chép file requirements.txt vào container
COPY requirements.txt requirements.txt

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn của dự án vào container
COPY . .

# Mở port 8000 để bên ngoài có thể truy cập vào API
EXPOSE 8000

# Lệnh để chạy ứng dụng khi container khởi động
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
