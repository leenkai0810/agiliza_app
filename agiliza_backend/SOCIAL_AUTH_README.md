# Social Authentication Integration Guide

Complete guide for setting up Google and Apple Sign-In with Agiliza backend.

## 📋 Quick Overview

This setup includes:
- ✅ Google OAuth2 Sign-In
- ✅ Apple OAuth2 Sign-In  
- ✅ Social account connection/disconnection
- ✅ JWT token management
- ✅ User profile management
- ✅ Multiple provider support

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env with your credentials
nano .env
```

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Register Providers in Django Admin
```bash
python manage.py runserver
# Navigate to http://localhost:8000/admin/
# Add Social Applications for Google and Apple
```

### 6. Test Endpoints
```bash
# Test social auth endpoints
python test_social_auth.py

# Test with actual tokens (see SOCIAL_AUTH_SETUP.md)
curl -X POST http://localhost:8000/api/auth/google/login/ \
  -H "Content-Type: application/json" \
  -d '{"id_token": "YOUR_TOKEN"}'
```

---

## 📚 File Structure

```
agiliza_backend/
├── accounts/
│   ├── models.py              # CustomUser model
│   ├── views.py               # All authentication views (JWT + Social)
│   ├── serializers.py         # Serializers for auth endpoints
│   ├── adapters.py            # Custom allauth adapters
│   ├── urls.py                # API routes
│   └── admin.py               # Admin configuration
├── config/
│   ├── settings.py            # Django settings (with social auth config)
│   ├── urls.py                # Main URL router
│   └── wsgi.py                # WSGI application
├── SOCIAL_AUTH_SETUP.md       # Detailed setup guide (Google + Apple)
├── test_social_auth.py        # Social auth endpoint tests
├── Agiliza_Social_Auth.postman_collection.json  # Postman requests
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
└── manage.py                  # Django CLI
```

---

## 🔐 Environment Variables

Required variables in `.env`:

```env
# Google OAuth2
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx

# Apple OAuth2
APPLE_TEAM_ID=xxx
APPLE_KEY_ID=xxx
APPLE_SERVICE_ID=com.agiliza.service
APPLE_PRIVATE_KEY=/path/to/key.p8

# Django
DEBUG=True
SECRET_KEY=your-secret-key

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

See `.env.example` for all available options.

---

## 🔗 API Endpoints

### Traditional Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login with email/password
- `POST /api/auth/logout/` - Logout user
- `GET /api/auth/profile/` - Get user profile
- `PUT/PATCH /api/auth/profile/` - Update profile
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Social Authentication
- `POST /api/auth/google/login/` - Login with Google
- `POST /api/auth/google/connect/` - Link Google to existing account
- `POST /api/auth/apple/login/` - Login with Apple
- `POST /api/auth/apple/connect/` - Link Apple to existing account
- `GET /api/auth/social/accounts/` - List connected social accounts
- `POST /api/auth/social/disconnect/` - Disconnect social account

---

## 📖 Setup Instructions

### Google OAuth2

**See detailed instructions in [SOCIAL_AUTH_SETUP.md](SOCIAL_AUTH_SETUP.md#google-oauth2-setup)**

Quick summary:
1. Create Google Cloud Project
2. Enable Google+ API
3. Create OAuth2 credentials (Web Application)
4. Add authorized redirect URIs
5. Copy Client ID & Secret to `.env`
6. Register in Django Admin as Social Application

### Apple OAuth2

**See detailed instructions in [SOCIAL_AUTH_SETUP.md](SOCIAL_AUTH_SETUP.md#apple-oauth2-setup)**

Quick summary:
1. Enroll in Apple Developer Program
2. Create App ID with Sign in with Apple
3. Create Service ID for web
4. Create private key (download .p8 file)
5. Get Team ID and Key ID
6. Add credentials to `.env`
7. Register in Django Admin as Social Application

---

## 🧪 Testing

### Test All Social Auth Endpoints
```bash
python test_social_auth.py
```

### Test with Real Tokens

#### Google Sign-In
```bash
# Get ID token from Google OAuth client
curl -X POST http://localhost:8000/api/auth/google/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "YOUR_GOOGLE_ID_TOKEN"
  }'
```

#### Apple Sign-In
```bash
# Get ID token from Apple OAuth client
curl -X POST http://localhost:8000/api/auth/apple/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "YOUR_APPLE_ID_TOKEN"
  }'
```

#### List Connected Accounts
```bash
curl -X GET http://localhost:8000/api/auth/social/accounts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Disconnect Account
```bash
curl -X POST http://localhost:8000/api/auth/social/disconnect/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"provider": "google"}'
```

### Using Postman

1. Import `Agiliza_Social_Auth.postman_collection.json` into Postman
2. Set variables:
   - `base_url`: http://localhost:8000/api/auth
   - `access_token`: Your JWT access token
3. Use collections to test each endpoint

---

## 🔄 Authentication Flow

### Social Login Flow

```
1. User clicks "Sign in with Google/Apple"
   ↓
2. Frontend handles OAuth flow with provider
   ↓
3. Frontend receives ID token/authorization code
   ↓
4. Frontend sends token to: POST /api/auth/{google|apple}/login/
   ↓
5. Backend validates token with provider
   ↓
6. If new user: Create account automatically
   ↓
7. If existing user: Link social account
   ↓
8. Return JWT tokens + user data
   ↓
9. Frontend stores tokens and authenticates subsequent requests
```

### Connect Social Account Flow

```
1. User logged in to Agiliza (has JWT token)
   ↓
2. User clicks "Connect Google/Apple"
   ↓
3. Frontend handles OAuth flow with provider
   ↓
4. Frontend receives ID token
   ↓
5. Frontend sends token to: POST /api/auth/{google|apple}/connect/
      with Authorization: Bearer JWT_TOKEN
   ↓
6. Backend validates token with provider
   ↓
7. Backend links social account to existing user
   ↓
8. Return success response
   ↓
9. Frontend shows confirmation
```

---

## 🛠️ Custom Adapters

The system includes custom adapters (`accounts/adapters.py`) that:

1. **CustomAccountAdapter**: Handles user creation from social accounts
   - Extracts full name from provider data
   - Marks email as verified if provider confirms it
   - Sets default role as CLIENT

2. **CustomSocialAccountAdapter**: Handles social login
   - Connects social account to existing user if email matches
   - Populates user fields from provider data
   - Manages account linking

---

## 🔒 Security Considerations

1. **Token Validation**: All tokens are validated with the provider's servers
2. **CORS**: Restricted to specified origins in `CORS_ALLOWED_ORIGINS`
3. **JWT**: Tokens expire after 5 minutes (access) or 1 day (refresh)
4. **Email Verification**: Optional verification for email addresses
5. **HTTPS**: Use HTTPS in production (set `JWT_AUTH_SECURE=True`)

---

## 📝 Response Examples

### Successful Google Login
```json
{
  "user": {
    "id": 1,
    "email": "user@gmail.com",
    "full_name": "John Doe",
    "phone": null,
    "profile_image": null,
    "role": "CLIENT",
    "is_verified": true,
    "is_active": true,
    "date_joined": "2026-05-16T10:30:00Z"
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### List Social Accounts
```json
{
  "social_accounts": [
    {
      "provider": "google",
      "display_name": "Google",
      "connected_at": "2026-05-16T10:30:00Z",
      "is_primary": true
    },
    {
      "provider": "apple",
      "display_name": "Apple",
      "connected_at": "2026-05-16T10:35:00Z",
      "is_primary": false
    }
  ],
  "total": 2
}
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `SocialAccount is not configured` | Register provider in Django Admin |
| `Invalid credentials` | Verify Google/Apple credentials in `.env` |
| `Redirect URI mismatch` | Check OAuth redirect URIs in provider console |
| `Email already exists` | User already has account with different provider |
| `CORS error` | Add frontend URL to `CORS_ALLOWED_ORIGINS` |
| `Token expired` | Use refresh token endpoint to get new token |
| `Provider not found` | Ensure provider is in INSTALLED_APPS |

---

## 📚 Additional Resources

- [SOCIAL_AUTH_SETUP.md](SOCIAL_AUTH_SETUP.md) - Detailed setup for Google & Apple
- [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md) - Traditional auth endpoints
- [Django AllAuth Docs](https://django-allauth.readthedocs.io/)
- [dj-rest-auth Docs](https://dj-rest-auth.readthedocs.io/)
- [Google OAuth Docs](https://developers.google.com/identity/protocols/oauth2)
- [Apple Sign In Docs](https://developer.apple.com/sign-in-with-apple/)

---

## 🎯 Next Steps

1. ✅ Configure `.env` with Google/Apple credentials
2. ✅ Run migrations
3. ✅ Register providers in Django Admin
4. ✅ Test endpoints with `python test_social_auth.py`
5. ✅ Integrate with frontend
6. ✅ Deploy to production (update CORS, use HTTPS)

---

## 💬 Support

For issues or questions:
1. Check [SOCIAL_AUTH_SETUP.md](SOCIAL_AUTH_SETUP.md) for detailed setup
2. Check [Troubleshooting](#-troubleshooting) section
3. Review Django AllAuth & dj-rest-auth documentation
4. Check Django logs: `python manage.py runserver 2>&1 | grep -i error`

---

**Happy authenticating! 🚀**
