# 🚀 PAM Setup Guide

## 📋 Quick Start

### 1. **Clone và Setup**
```bash
git clone <your-repo>
cd pam-private-asset-management
```

### 2. **Environment Configuration**
```bash
# Copy environment template
cp env.example .env

# Edit .env file với thông tin của bạn
nano .env
```

### 3. **Generate JWT Secret Key**
```bash
# Tạo JWT secret key mới
openssl rand -hex 32
```

### 4. **Update .env file**
```bash
# Thay đổi các giá trị trong .env:
DB_USER=your_username
DB_PASSWORD=your_password
JWT_SECRET_KEY=<paste_secret_key_here>
```

### 5. **Run Application**
```bash
# Build và start tất cả services
docker-compose up --build -d

# Check status
docker-compose ps
```

### 6. **Access Application**
- **Frontend**: http://localhost:6868
- **Backend API**: http://localhost:8000/docs
- **Database**: localhost:5432

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_USER` | Database username | - |
| `DB_PASSWORD` | Database password | - |
| `DB_HOST` | Database host | pam-db-service |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | pam_db |
| `JWT_SECRET_KEY` | JWT signing key | - |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 1440 (24h) |
| `JWT_HASHING_ALGORITHM` | JWT token signing algorithm | HS256 |
| `PASSWORD_HASHING_ALGORITHM` | Password hashing algorithm | bcrypt |
| `PAM_BACKEND_API_URL` | Backend API URL | http://localhost:8000 |
| `BACKEND_CORS_ORIGINS` | CORS origins | http://localhost:6868,http://localhost:8501 |

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check database logs
docker-compose logs pam-db-service

# Restart database
docker-compose restart pam-db-service
```

### Backend Issues
```bash
# Check backend logs
docker-compose logs pam-backend-service

# Restart backend
docker-compose restart pam-backend-service
```

### Frontend Issues
```bash
# Check frontend logs
docker-compose logs pam-frontend-service

# Restart frontend
docker-compose restart pam-frontend-service
```

## 🔄 Development Mode

```bash
# Stop all services
docker-compose down

# Start with logs
docker-compose up --build

# Rebuild specific service
docker-compose build pam-backend-service
docker-compose up pam-backend-service
```

## 📝 Notes

- **Single .env file**: Tất cả services sử dụng chung một file `.env`
- **Port 6868**: Frontend chạy trên port 6868 (Lộc Phát - may mắn)
- **Health checks**: Tất cả services có health check
- **Auto restart**: Services tự động restart khi crash
