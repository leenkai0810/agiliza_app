# Social Authentication Setup Guide

This guide explains how to set up Google and Apple Sign-In for your Agiliza application using django-allauth and dj-rest-auth.

## Table of Contents
1. [Google OAuth2 Setup](#google-oauth2-setup)
2. [Apple OAuth2 Setup](#apple-oauth2-setup)
3. [API Endpoints](#api-endpoints)
4. [Testing Social Authentication](#testing-social-authentication)
5. [Environment Variables](#environment-variables)

---

## Google OAuth2 Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown and select "New Project"
3. Enter a project name (e.g., "Agiliza")
4. Click "Create"

### Step 2: Enable Google+ API

1. In the Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Google+ API"
3. Click on it and press **Enable**

### Step 3: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth Client ID**
3. Choose **Web Application** as the Application type
4. Fill in the details:
   - **Name**: Agiliza Backend
   - **Authorized JavaScript origins**:
     ```
     http://localhost:8000
     http://localhost:3000
     http://127.0.0.1:8000
     http://127.0.0.1:3000
     ```
   - **Authorized redirect URIs**:
     ```
     http://localhost:8000/api/auth/google/callback/
     http://localhost:3000/auth/google/callback/
     http://127.0.0.1:8000/api/auth/google/callback/
     http://127.0.0.1:3000/auth/google/callback/
     ```
5. Click **Create**
6. Copy the **Client ID** and **Client Secret**

### Step 4: Add Credentials to Django Settings

Update your `config/settings.py`:

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': 'YOUR_GOOGLE_CLIENT_ID',
            'secret': 'YOUR_GOOGLE_CLIENT_SECRET',
            'key': ''
        },
        'VERIFIED_EMAIL': False,
        'VERSION': 'v2',
    },
}
```

Or use environment variables:

```python
import os

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'key': ''
        },
        # ... other settings
    },
}
```

### Step 5: Register in Django Admin

1. Create a superuser if you haven't:
   ```bash
   python manage.py createsuperuser
   ```

2. Go to Django Admin: `http://localhost:8000/admin/`

3. Navigate to **Social Applications**

4. Click **Add Social Application**

5. Fill in the details:
   - **Provider**: Google
   - **Name**: Google
   - **Client id**: Your Google Client ID
   - **Secret key**: Your Google Client Secret
   - **Sites**: Select your site
   - **Key**: Leave empty

6. Click **Save**

---

## Apple OAuth2 Setup

### Step 1: Join Apple Developer Program

1. Go to [Apple Developer Program](https://developer.apple.com/)
2. Sign in with your Apple ID or create a new one
3. Enroll in the Developer Program

### Step 2: Create App ID

1. Go to [Certificates, Identifiers & Profiles](https://developer.apple.com/account/resources/)
2. Click **Identifiers**
3. Click **+** to create a new identifier
4. Select **App IDs** and click **Continue**
5. Choose **App**
6. Fill in:
   - **Description**: Agiliza App
   - **Bundle ID**: com.agiliza.app
   - **Capabilities**: Check "Sign in with Apple"
7. Click **Continue** and **Register**

### Step 3: Create Service ID

1. Go to **Identifiers** again
2. Click **+** to create a new identifier
3. Select **Services IDs** and click **Continue**
4. Fill in:
   - **Description**: Agiliza Service
   - **Identifier**: com.agiliza.service
5. Check **Sign in with Apple**
6. Click **Configure** and add:
   - **Primary Domain**: localhost
   - **Return URLs**:
     ```
     http://localhost:8000/api/auth/apple/callback/
     http://localhost:3000/auth/apple/callback/
     ```
7. Click **Save** and **Continue**
8. Click **Register**

### Step 4: Create Private Key

1. Go to **Keys**
2. Click **+** to create a new key
3. Give it a name: "Agiliza Sign in with Apple"
4. Check **Sign in with Apple**
5. Click **Configure**
6. Select your **Primary App ID** (created in Step 2)
7. Click **Save**
8. Click **Continue** and **Register**
9. **Download the key** (you can only download it once)
10. Note the **Key ID** (shown on the page)

### Step 5: Get Team ID

1. Go to **Membership**
2. Find your **Team ID** under "Membership Information"

### Step 6: Add Credentials to Django Settings

Update your `config/settings.py`:

```python
SOCIALACCOUNT_PROVIDERS = {
    'apple': {
        'SCOPE': [
            'name',
            'email',
        ],
        'APP': {
            'client_id': 'com.agiliza.service',  # Service ID
            'secret': '',  # Will be generated from private key
            'key': ''
        },
    },
}
```

Or use environment variables with Team ID and Key ID:

```python
import os

# Apple OAuth configuration
APPLE_TEAM_ID = os.getenv('APPLE_TEAM_ID')
APPLE_KEY_ID = os.getenv('APPLE_KEY_ID')
APPLE_PRIVATE_KEY = os.getenv('APPLE_PRIVATE_KEY')  # Full path to downloaded .p8 file
APPLE_SERVICE_ID = os.getenv('APPLE_SERVICE_ID', 'com.agiliza.service')

SOCIALACCOUNT_PROVIDERS = {
    'apple': {
        'APP': {
            'client_id': APPLE_SERVICE_ID,
            'secret': '',
            'key': ''
        },
    },
}
```

### Step 7: Register in Django Admin

1. Go to Django Admin: `http://localhost:8000/admin/`
2. Navigate to **Social Applications**
3. Click **Add Social Application**
4. Fill in:
   - **Provider**: Apple
   - **Name**: Apple
   - **Client id**: Your Service ID (com.agiliza.service)
   - **Secret key**: Leave empty or use your Team ID
   - **Sites**: Select your site
   - **Key**: Your Key ID
5. Click **Save**

---

## API Endpoints

### Google Sign-In

**Endpoint:** `POST /api/auth/google/login/`

**Authentication:** ❌ Not required

**Request Body:**

Option 1: Using ID Token (from frontend OAuth)
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ..."
}
```

Option 2: Using Access Token
```json
{
  "access_token": "ya29.a0AfH6SMBx..."
}
```

Option 3: Using Authorization Code
```json
{
  "code": "4/0AY0e-g7VJ8f..."
}
```

**Success Response (200 OK):**
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

---

### Apple Sign-In

**Endpoint:** `POST /api/auth/apple/login/`

**Authentication:** ❌ Not required

**Request Body:**

Option 1: Using ID Token
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ..."
}
```

Option 2: Using Access Token
```json
{
  "access_token": "ca7ee7d3e5f94d36bb5d91b26f0d0e01e.0.123.456"
}
```

Option 3: Using Authorization Code with User Info
```json
{
  "code": "ca3ee7d3e5f94d36bb5d91b26f0d0e01e.0.123.456",
  "user": {
    "name": {
      "firstName": "John",
      "lastName": "Doe"
    },
    "email": "user@privaterelay.appleid.com"
  }
}
```

**Success Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "email": "user@privaterelay.appleid.com",
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

---

### Connect Google Account (Link to Existing User)

**Endpoint:** `POST /api/auth/google/connect/`

**Authentication:** ✅ Required (Bearer token)

**Request Body:**
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ..."
}
```

**Success Response (200 OK):**
```json
{
  "detail": "Google account connected successfully."
}
```

---

### Connect Apple Account (Link to Existing User)

**Endpoint:** `POST /api/auth/apple/connect/`

**Authentication:** ✅ Required (Bearer token)

**Request Body:**
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ..."
}
```

**Success Response (200 OK):**
```json
{
  "detail": "Apple account connected successfully."
}
```

---

### List Connected Social Accounts

**Endpoint:** `GET /api/auth/social/accounts/`

**Authentication:** ✅ Required (Bearer token)

**Success Response (200 OK):**
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

### Disconnect Social Account

**Endpoint:** `POST /api/auth/social/disconnect/`

**Authentication:** ✅ Required (Bearer token)

**Request Body:**
```json
{
  "provider": "google"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Google account disconnected successfully."
}
```

---

## Testing Social Authentication

### Using cURL

#### Test Google Login:
```bash
curl -X POST http://localhost:8000/api/auth/google/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "YOUR_GOOGLE_ID_TOKEN"
  }'
```

#### Test Apple Login:
```bash
curl -X POST http://localhost:8000/api/auth/apple/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "YOUR_APPLE_ID_TOKEN"
  }'
```

#### List Connected Accounts:
```bash
curl -X GET http://localhost:8000/api/auth/social/accounts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Disconnect Social Account:
```bash
curl -X POST http://localhost:8000/api/auth/social/disconnect/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "google"
  }'
```

---

## Environment Variables

Create a `.env` file in your project root:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Apple OAuth
APPLE_TEAM_ID=your_apple_team_id
APPLE_KEY_ID=your_apple_key_id
APPLE_SERVICE_ID=com.agiliza.service
APPLE_PRIVATE_KEY=/path/to/downloaded/key.p8

# Django Settings
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

Then in your `config/settings.py`:

```python
import os
from decouple import config

# Google
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')

# Apple
APPLE_TEAM_ID = config('APPLE_TEAM_ID', default='')
APPLE_KEY_ID = config('APPLE_KEY_ID', default='')
APPLE_SERVICE_ID = config('APPLE_SERVICE_ID', default='com.agiliza.service')
APPLE_PRIVATE_KEY = config('APPLE_PRIVATE_KEY', default='')
```

---

## Frontend Integration Example (React)

### Google Sign-In Integration:

```javascript
import { GoogleLogin } from '@react-oauth/google';

function GoogleSignIn() {
  const handleSuccess = (credentialResponse) => {
    fetch('http://localhost:8000/api/auth/google/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id_token: credentialResponse.credential,
      }),
    })
    .then(response => response.json())
    .then(data => {
      // Store tokens and redirect
      localStorage.setItem('access_token', data.tokens.access);
      localStorage.setItem('refresh_token', data.tokens.refresh);
      window.location.href = '/dashboard';
    });
  };

  return (
    <GoogleLogin
      onSuccess={handleSuccess}
      onError={() => console.log('Login Failed')}
    />
  );
}
```

### Apple Sign-In Integration:

```javascript
import AppleSignin from 'react-apple-signin-auth';

function AppleSignIn() {
  const handleSuccess = (response) => {
    fetch('http://localhost:8000/api/auth/apple/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id_token: response.id_token,
        code: response.code,
        user: response.user,
      }),
    })
    .then(response => response.json())
    .then(data => {
      // Store tokens and redirect
      localStorage.setItem('access_token', data.tokens.access);
      localStorage.setItem('refresh_token', data.tokens.refresh);
      window.location.href = '/dashboard';
    });
  };

  return (
    <AppleSignin
      authOptions={{
        clientId: 'com.agiliza.service',
        teamId: 'YOUR_TEAM_ID',
        keyId: 'YOUR_KEY_ID',
        redirectUri: 'http://localhost:3000/auth/apple/callback',
        scope: 'name email',
        responseType: 'code',
      }}
      onSuccess={handleSuccess}
    />
  );
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Invalid client_id` | Verify your Google/Apple credentials in settings |
| `Redirect URI mismatch` | Ensure redirect URIs match exactly in Google/Apple console |
| `Token expired` | Refresh token using `/api/auth/token/refresh/` endpoint |
| `Provider not configured` | Register the social app in Django admin |
| `CORS error` | Add origin to `CORS_ALLOWED_ORIGINS` in settings |
| `SocialAccount already exists` | User already has this provider connected |

---

## Additional Resources

- [Django AllAuth Documentation](https://django-allauth.readthedocs.io/)
- [dj-rest-auth Documentation](https://dj-rest-auth.readthedocs.io/)
- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Apple Sign In Documentation](https://developer.apple.com/sign-in-with-apple/)
