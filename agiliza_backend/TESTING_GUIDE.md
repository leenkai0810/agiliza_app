# API Testing - Complete Guide

This directory contains comprehensive tools and documentation for testing the Agiliza authentication APIs.

## 📋 Available Testing Methods

### 1. **Automated Python Script** (Recommended for beginners)
File: `test_apis.py`

**Features:**
- Automatically tests all endpoints
- Colored output for easy reading
- Handles token management automatically
- Tests error scenarios
- Provides test summary

**How to run:**
```bash
python test_apis.py
```

**What it tests:**
- ✅ User registration
- ✅ User login
- ✅ Get user profile
- ✅ Update user profile
- ✅ Token refresh
- ✅ User logout
- ✅ Invalid token handling
- ✅ Duplicate email detection
- ✅ Invalid credentials handling

**Output Example:**
```
============================================================
TEST 1: USER REGISTRATION
============================================================

✓ User registered successfully!
ℹ Email: testuser1715852345@example.com
ℹ Access Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
ℹ Refresh Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 2. **Postman Collection** (Visual & Interactive)
File: `Agiliza_API.postman_collection.json`

**How to import:**
1. Open Postman
2. Click `File` → `Import`
3. Select `Agiliza_API.postman_collection.json`
4. Collection will appear in your sidebar

**Variables to set:**
- `base_url`: http://localhost:8000/api/auth (already set)
- `access_token`: Paste token from login/register response
- `refresh_token`: Paste refresh token from login/register response

**Collections:**
- 6 pre-configured requests
- All headers and body templates included
- Easy to copy and modify

---

### 3. **cURL Commands** (Command Line)
File: `test_api.sh`

**How to use:**

**Option A: Source the script and run individual functions**
```bash
source test_api.sh
register_user
```

**Option B: Run the entire script**
```bash
bash test_api.sh
```

**Available Functions:**
- `register_user` - Register new user
- `login_user` - Login user
- `get_profile` - Get user profile
- `update_profile` - Update profile
- `refresh_token` - Refresh access token
- `logout_user` - Logout user
- `test_invalid_token` - Test invalid token
- `test_invalid_credentials` - Test invalid credentials
- `test_duplicate_email` - Test duplicate email
- `test_password_mismatch` - Test password mismatch

---

### 4. **Manual cURL Commands** (Direct API calls)

#### Register a new user:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "role": "CLIENT"
  }'
```

#### Login user:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

#### Get user profile (requires token):
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Update user profile:
```bash
curl -X PATCH http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "phone": "+9876543210"
  }'
```

#### Refresh access token:
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

#### Logout user:
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

---

## 🚀 Quick Start

### Step 1: Start Django server
```bash
python manage.py runserver
```

### Step 2: Run migrations (first time only)
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Choose your testing method

**For automated testing:**
```bash
python test_apis.py
```

**For Postman:**
1. Import `Agiliza_API.postman_collection.json`
2. Click on each request and hit `Send`

**For cURL:**
```bash
source test_api.sh
register_user
```

---

## 📊 API Endpoints Reference

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/auth/register/` | ❌ | Register new user |
| POST | `/api/auth/login/` | ❌ | Login user |
| POST | `/api/auth/logout/` | ✅ | Logout user |
| GET | `/api/auth/profile/` | ✅ | Get user profile |
| PUT/PATCH | `/api/auth/profile/` | ✅ | Update user profile |
| POST | `/api/auth/token/refresh/` | ❌ | Refresh access token |

---

## 🔐 Token Management

### Access Token
- **Lifetime**: 5 minutes
- **Used for**: API authentication
- **Header format**: `Authorization: Bearer <token>`
- **When expired**: Use refresh token to get new one

### Refresh Token
- **Lifetime**: 1 day
- **Used for**: Getting new access token
- **Rotation**: Automatically rotated when used
- **Blacklist**: Previous token is blacklisted after rotation

### How to refresh token:
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

---

## ✅ Expected Responses

### Success Responses

**201 Created (Register):**
```json
{
  "message": "User registered successfully.",
  "user": {...},
  "tokens": {"access": "...", "refresh": "..."}
}
```

**200 OK (Login):**
```json
{
  "message": "Login successful.",
  "user": {...},
  "tokens": {"access": "...", "refresh": "..."}
}
```

**200 OK (Get Profile):**
```json
{
  "id": 1,
  "email": "john@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "profile_image": null,
  "role": "CLIENT",
  "is_verified": false,
  "is_active": true,
  "date_joined": "2026-05-16T10:30:00Z"
}
```

### Error Responses

**400 Bad Request (Invalid data):**
```json
{
  "email": ["Email already registered."],
  "password": ["Passwords do not match."]
}
```

**401 Unauthorized (Invalid token):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| `Connection refused` | Make sure Django server is running (`python manage.py runserver`) |
| `Authentication credentials were not provided` | Add `Authorization: Bearer <token>` header |
| `Token is invalid or expired` | Refresh token using `/token/refresh/` endpoint |
| `Email already registered` | Use a different email for registration |
| `Passwords do not match` | Ensure password and password_confirm are identical |
| `CORS error` | CORS is configured in settings for all origins |
| `Port 8000 already in use` | Run on different port: `python manage.py runserver 8001` |

---

## 📚 Detailed Documentation

For more detailed information, see:
- `API_TESTING_GUIDE.md` - Comprehensive API documentation
- Individual endpoint specifications with examples
- Request/response schemas

---

## 🛠️ Tools You Can Use

### 1. **Postman**
- Visual API testing
- Easy token management with variables
- Request history
- Download: https://www.postman.com/downloads/

### 2. **Thunder Client** (VS Code)
- Built into VS Code
- Quick and lightweight
- Extension ID: `rangav.vscode-thunder-client`

### 3. **REST Client** (VS Code)
- Create `.http` files with requests
- Execute directly from editor
- Extension ID: `humao.rest-client`

### 4. **cURL** (Command line)
- Built into macOS/Linux
- For Windows, download from: https://curl.se/download.html

### 5. **HTTPie** (Command line)
- User-friendly alternative to cURL
- Install: `pip install httpie`
- Usage: `http POST http://localhost:8000/api/auth/register/ ...`

---

## 📝 Sample Test Workflow

```bash
# 1. Start server
python manage.py runserver

# 2. In another terminal, register user
python test_apis.py

# 3. Copy the access and refresh tokens from output

# 4. Use tokens to test other endpoints
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 5. To refresh token before it expires
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'

# 6. To logout
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

---

## ❓ FAQ

**Q: How often do access tokens expire?**
A: Every 5 minutes. Use the refresh token to get a new one.

**Q: Can I use the same refresh token multiple times?**
A: No. After using it once, it gets rotated and a new one is issued. The old one is blacklisted.

**Q: What happens when I logout?**
A: Your refresh token is blacklisted and cannot be used again.

**Q: Can I register with the same email twice?**
A: No. The API will return a 400 error saying "Email already registered."

**Q: Do I need to send password confirm on login?**
A: No. Password confirm is only needed during registration.

**Q: Can I update my password through the profile endpoint?**
A: No. The profile endpoint only updates full_name, phone, and profile_image. To change password, you would need a separate endpoint.

---

## 📞 Need Help?

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the detailed API documentation in `API_TESTING_GUIDE.md`
3. Check Django server logs for error messages
4. Ensure all required fields are being sent in the request
5. Verify token format and expiration

---

Happy Testing! 🚀
