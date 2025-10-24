# 🔧 Environment Configuration

## 📋 Single Source of Truth

PAM sử dụng **một file `.env` duy nhất** cho tất cả services, tuân theo nguyên tắc "single source of truth".

## 🗂️ File Structure

```
pam-private-asset-management/
├── .env                    # ⚠️  Không commit (chứa secrets)
├── env.example            # ✅ Template cho .env
├── docker-compose.yml     # Sử dụng .env cho tất cả services
└── ...
```

## 🔑 Environment Variables

### Database Configuration
```bash
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=pam-db-service
DB_PORT=5432
DB_NAME=pam_db
```

### JWT Configuration
```bash
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
JWT_HASHING_ALGORITHM=HS256
```

### Password Security
```bash
PASSWORD_HASHING_ALGORITHM=bcrypt
PASSWORD_HASHING_DEPRECATED_SCHEMES=auto
```

### Frontend Configuration
```bash
PAM_BACKEND_API_URL=http://pam-backend-service:8000
```

### CORS Configuration
```bash
BACKEND_CORS_ORIGINS=http://localhost:6868,http://localhost:8501
```

## 🚀 Setup Process

### 1. Copy Template
```bash
cp env.example .env
```

### 2. Generate JWT Secret
```bash
openssl rand -hex 32
# Copy output to JWT_SECRET_KEY in .env
```

### 3. Update Database Credentials
```bash
# Edit .env file
nano .env
```

### 4. Start Services
```bash
docker-compose up --build -d
```

## 🔒 Security Notes

- **`.env` file**: Không bao giờ commit vào Git
- **JWT Secret**: Phải là random string mạnh
- **Database Password**: Sử dụng password mạnh
- **CORS Origins**: Chỉ cho phép domains cần thiết

## 🐛 Troubleshooting

### Missing .env file
```bash
cp env.example .env
# Edit with your values
```

### Invalid JWT Secret
```bash
# Generate new secret
openssl rand -hex 32
# Update JWT_SECRET_KEY in .env
```

### Database Connection Issues
```bash
# Check DB credentials in .env
# Restart database service
docker-compose restart pam-db-service
```

## 📝 Best Practices

1. **Single .env**: Tất cả services sử dụng chung một file
2. **Template**: Luôn có `env.example` làm template
3. **Security**: Không commit secrets vào Git
4. **Documentation**: Ghi rõ mục đích từng biến
5. **Validation**: Kiểm tra tất cả biến bắt buộc khi start
