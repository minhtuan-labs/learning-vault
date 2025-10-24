# 🧪 Hướng dẫn Test Session Management

## ✅ Các cải tiến đã thực hiện:

### 1. **Tăng Session Timeout**
- JWT token timeout: **24 giờ** (thay vì 30 phút)
- Cookie expiration: **30 ngày**

### 2. **Cải thiện Session Persistence**
- Đồng bộ giữa session state và cookie
- Tự động khôi phục session từ cookie khi refresh
- Xử lý trường hợp cookie và session state khác nhau

### 3. **Sửa Cookie Manager Issues**
- Sử dụng session state để cache cookie manager
- Tránh duplicate key error với fixed key "pam_cookie_manager"
- Tự động clear cookie manager khi logout

### 4. **Debug Tools**
- Thêm debug function để kiểm tra trạng thái session
- Hiển thị thông tin chi tiết về token và cookie
- Button reset cookie manager nếu cần

## 🧪 Cách Test:

### Test 1: Login và Refresh
1. Truy cập `http://localhost:6868`
2. Login với tài khoản của bạn
3. **Bấm F5 hoặc Refresh** - Session phải được giữ nguyên
4. Kiểm tra debug info (tick vào checkbox "🔍 Debug Session State")

### Test 2: Session Persistence
1. Login thành công
2. Đóng tab browser
3. Mở tab mới, truy cập lại `http://localhost:6868`
4. Phải vẫn đăng nhập (không cần login lại)

### Test 3: Token Expiration
1. Login thành công
2. Đợi 24 giờ (hoặc thay đổi JWT_SECRET_KEY để invalidate token)
3. Phải tự động logout

## 🔍 Debug Information:

Khi tick vào "🔍 Debug Session State", bạn sẽ thấy:
- **Session State**: Trạng thái token trong session
- **Cookie Manager State**: Trạng thái cookie manager trong session
- **Cookie State**: Trạng thái token trong cookie
- **Token Validation**: Token có hợp lệ không
- **🔄 Reset Cookie Manager**: Button để reset cookie manager nếu cần

## 🚨 Nếu vẫn có vấn đề:

1. **Clear browser cache và cookies**
2. **Kiểm tra console logs** trong browser
3. **Kiểm tra Docker logs**: `docker-compose logs pam-frontend-service`
4. **Restart containers**: `docker-compose restart`

## 📝 Expected Behavior:

- ✅ Login → Refresh → Vẫn đăng nhập
- ✅ Login → Đóng tab → Mở tab mới → Vẫn đăng nhập  
- ✅ Token hết hạn → Tự động logout
- ✅ Logout → Clear session và cookie
