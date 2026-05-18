# API Testing Guide

## Base URL
```
http://localhost:8000/api/auth/
```

---

## 1. User Registration
**Endpoint:** `POST /api/auth/register/`  
**Authentication:** ❌ Not Required

### Request
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

### Request Body Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| email | string | ✅ | Must be unique |
| password | string | ✅ | Min 8 characters |
| password_confirm | string | ✅ | Must match password |
| full_name | string | ✅ | User's full name |
| phone | string | ❌ | Phone number |
| role | string | ❌ | CLIENT, PROFESSIONAL, ADMIN (default: CLIENT) |

### Success Response (201 Created)
```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "profile_image": null,
    "role": "CLIENT",
    "is_verified": false,
    "is_active": true,
    "date_joined": "2026-05-16T10:30:00Z"
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### Error Response (400 Bad Request)
```json
{
  "email": ["Email already registered."],
  "password": ["Passwords do not match."]
}
```

---

## 2. User Login
**Endpoint:** `POST /api/auth/login/`  
**Authentication:** ❌ Not Required

### Request
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### Request Body Fields
| Field | Type | Required |
|-------|------|----------|
| email | string | ✅ |
| password | string | ✅ |

### Success Response (200 OK)
```json
{
  "message": "Login successful.",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "profile_image": null,
    "role": "CLIENT",
    "is_verified": false,
    "is_active": true,
    "date_joined": "2026-05-16T10:30:00Z"
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### Error Response (400 Bad Request)
```json
{
  "non_field_errors": ["Invalid credentials. Please check your email and password."]
}
```

---

## 3. Get Current User Profile
**Endpoint:** `GET /api/auth/profile/`  
**Authentication:** ✅ Required (Bearer Token)

### Request
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Success Response (200 OK)
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

### Error Response (401 Unauthorized)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## 4. Update User Profile
**Endpoint:** `PUT/PATCH /api/auth/profile/`  
**Authentication:** ✅ Required (Bearer Token)

### Request (PUT - Complete Update)
```bash
curl -X PUT http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Doe",
    "phone": "+9876543210",
    "profile_image": null
  }'
```

### Request (PATCH - Partial Update)
```bash
curl -X PATCH http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Doe"
  }'
```

### Updateable Fields
| Field | Type | Required |
|-------|------|----------|
| full_name | string | ❌ |
| phone | string | ❌ |
| profile_image | file | ❌ |

### Success Response (200 OK)
```json
{
  "message": "Profile updated successfully.",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "full_name": "Jane Doe",
    "phone": "+9876543210",
    "profile_image": null,
    "role": "CLIENT",
    "is_verified": false,
    "is_active": true,
    "date_joined": "2026-05-16T10:30:00Z"
  }
}
```

---

## 5. Refresh Access Token
**Endpoint:** `POST /api/auth/token/refresh/`  
**Authentication:** ❌ Not Required

### Request
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

### Request Body Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| refresh | string | ✅ | Refresh token from login/register response |

### Success Response (200 OK)
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Error Response (401 Unauthorized)
```json
{
  "detail": "Token is invalid or expired."
}
```

---

## 6. User Logout
**Endpoint:** `POST /api/auth/logout/`  
**Authentication:** ✅ Required (Bearer Token)

### Request
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

### Request Body Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| refresh | string | ❌ | Refresh token to blacklist |

### Success Response (200 OK)
```json
{
  "message": "Logout successful."
}
```

### Error Response (400 Bad Request)
```json
{
  "error": "Token is blacklisted"
}
```

---

## Token Structure

### Access Token
- **Lifetime:** 5 minutes
- **Used for:** Authenticating API requests
- **Header:** `Authorization: Bearer <access_token>`

### Refresh Token
- **Lifetime:** 1 day
- **Used for:** Obtaining new access token
- **Can be:** Rotated and blacklisted after rotation

---

## Testing Workflow Example

```bash
# 1. Register a new user
RESPONSE=$(curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "full_name": "Test User",
    "phone": "+1111111111",
    "role": "CLIENT"
  }')

# Extract tokens (requires jq)
ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.tokens.access')
REFRESH_TOKEN=$(echo $RESPONSE | jq -r '.tokens.refresh')

# 2. Get user profile
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 3. Update profile
curl -X PATCH http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name"
  }'

# 4. Refresh token
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH_TOKEN\"}"

# 5. Logout
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH_TOKEN\"}"
```

---

## Postman Collection

Import this JSON into Postman:

```json
{
  "info": {
    "name": "Agiliza API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Register",
      "request": {
        "method": "POST",
        "header": [
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"email\": \"john@example.com\", \"password\": \"SecurePass123!\", \"password_confirm\": \"SecurePass123!\", \"full_name\": \"John Doe\", \"phone\": \"+1234567890\", \"role\": \"CLIENT\"}"
        },
        "url": {"raw": "http://localhost:8000/api/auth/register/", "protocol": "http", "host": ["localhost"], "port": "8000", "path": ["api", "auth", "register", ""]}
      }
    },
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {"mode": "raw", "raw": "{\"email\": \"john@example.com\", \"password\": \"SecurePass123!\"}"},
        "url": {"raw": "http://localhost:8000/api/auth/login/", "protocol": "http", "host": ["localhost"], "port": "8000", "path": ["api", "auth", "login", ""]}
      }
    },
    {
      "name": "Get Profile",
      "request": {
        "method": "GET",
        "header": [{"key": "Authorization", "value": "Bearer {{ACCESS_TOKEN}}"}],
        "url": {"raw": "http://localhost:8000/api/auth/profile/", "protocol": "http", "host": ["localhost"], "port": "8000", "path": ["api", "auth", "profile", ""]}
      }
    },
    {
      "name": "Update Profile",
      "request": {
        "method": "PATCH",
        "header": [{"key": "Authorization", "value": "Bearer {{ACCESS_TOKEN}}"}, {"key": "Content-Type", "value": "application/json"}],
        "body": {"mode": "raw", "raw": "{\"full_name\": \"Updated Name\"}"},
        "url": {"raw": "http://localhost:8000/api/auth/profile/", "protocol": "http", "host": ["localhost"], "port": "8000", "path": ["api", "auth", "profile", ""]}
      }
    },
    {
      "name": "Refresh Token",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {"mode": "raw", "raw": "{\"refresh\": \"{{REFRESH_TOKEN}}\"}"},
        "url": {"raw": "http://localhost:8000/api/auth/token/refresh/", "protocol": "http", "host": ["localhost"], "port": "8000", "path": ["api", "auth", "token", "refresh", ""]}
      }
    },
    {
      "name": "Logout",
      "request": {
        "method": "POST",
        "header": [{"key": "Authorization", "value": "Bearer {{ACCESS_TOKEN}}"}, {"key": "Content-Type", "value": "application/json"}],
        "body": {"mode": "raw", "raw": "{\"refresh\": \"{{REFRESH_TOKEN}}\"}"},
        "url": {"raw": "http://localhost:8000/api/auth/logout/", "protocol": "http", "host": ["localhost"], "port": "8000", "path": ["api", "auth", "logout", ""]}
      }
    }
  ],
  "variable": [
    {"key": "ACCESS_TOKEN", "value": ""},
    {"key": "REFRESH_TOKEN", "value": ""}
  ]
}
```

---

## Quick Start Steps

1. **Start Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Make sure migrations are applied:**
   ```bash
   python manage.py migrate
   ```

3. **Test Register endpoint** - copy the `access` and `refresh` tokens from response

4. **Set tokens in Postman** or use them in curl commands with `Bearer $ACCESS_TOKEN`

5. **Test other endpoints** using the access token

6. **When access token expires** (after 5 minutes), use refresh token to get new one

---

## Common Issues

| Issue | Solution |
|-------|----------|
| `Authentication credentials were not provided` | Add `Authorization: Bearer <token>` header |
| `Token is invalid or expired` | Refresh token using `/token/refresh/` endpoint |
| `Email already registered` | Use a different email for registration |
| `Passwords do not match` | Ensure password and password_confirm are identical |
| `CORS error` | CORS is configured in settings |

