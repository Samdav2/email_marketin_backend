# Authentication System Documentation

## Overview

Complete authentication and user profile system with JWT tokens, password management, and profile management.

## Architecture

### Models

#### User Model (`app/model/user.py`)
- `id` - Unique user identifier (UUID)
- `email` - User email (unique, indexed)
- `name` - User full name
- `password_hash` - Bcrypt hashed password
- `is_active` - Account status
- `created_at` - Account creation timestamp
- `updated_at` - Last update timestamp

#### Profile Model (`app/model/user.py`)
- `id` - Profile ID (UUID)
- `user_id` - Foreign key to User (unique, one-to-one)
- `business_name` - Business name
- `company_id` - Unique company identifier
- `phone` - Phone number
- `website` - Company website
- `address` - Street address
- `city` - City
- `state` - State/Province
- `postal_code` - Postal code
- `country` - Country
- `industry` - Industry sector
- `company_size` - Company size (e.g., "1-10", "11-50", etc.)
- `description` - Company description
- `logo_url` - Company logo URL
- `created_at` - Profile creation timestamp
- `updated_at` - Last update timestamp

### Core Components

1. **Password Utils** (`app/dependencies/password_utils.py`)
   - `hash_password()` - Hash password with bcrypt
   - `verify_password()` - Verify password against hash

2. **JWT Handler** (`app/dependencies/jwt_handler.py`)
   - `create_access_token()` - Generate JWT token
   - `verify_token()` - Verify and decode JWT token
   - `get_user_id_from_token()` - Extract user ID from token

3. **Current User Dependency** (`app/dependencies/current_user.py`)
   - `get_current_user()` - Get authenticated user from token
   - `get_current_active_user()` - Ensure user is active

4. **Repositories**
   - `app/repo/user.py` - User CRUD operations
   - `app/repo/profile.py` - Profile CRUD operations

5. **Auth Service** (`app/service/auth_service.py`)
   - `signup()` - Create new user account
   - `login()` - Authenticate user
   - `reset_password()` - Change password (authenticated)
   - `forgot_password()` - Send password reset email
   - `create_or_update_profile()` - Manage profile

6. **Auth API** (`app/api/auth.py`)
   - REST endpoints for all auth operations

## API Endpoints

### Public Endpoints

#### POST `/auth/signup`
Register new user account.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "is_active": true,
    "created_at": "2026-03-27T..."
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Email already registered or invalid data
- `500` - Server error

#### POST `/auth/login`
Authenticate user and get access token.

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "is_active": true,
    "created_at": "2026-03-27T..."
  }
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid credentials
- `500` - Server error

#### POST `/auth/forgot-password`
Request password reset email.

**Request:**
```json
{
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password reset link has been sent to your email"
}
```

**Status Codes:**
- `200` - Success (always returns success for security)
- `500` - Server error

### Protected Endpoints (Require Authentication)

All protected endpoints require `Authorization: Bearer <token>` header.

#### POST `/auth/reset-password`
Change password for authenticated user.

**Request:**
```json
{
  "old_password": "CurrentPass123",
  "new_password": "NewPass456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password updated successfully"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid password
- `401` - Unauthorized
- `500` - Server error

#### GET `/auth/me`
Get current user information.

**Response:**
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2026-03-27T..."
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized

#### POST `/auth/profile`
Create or update user profile.

**Request:**
```json
{
  "business_name": "Acme Corp",
  "company_id": "ACME-001",
  "phone": "+1-555-123-4567",
  "website": "https://acme.com",
  "address": "123 Main St",
  "city": "Springfield",
  "state": "IL",
  "postal_code": "62701",
  "country": "USA",
  "industry": "Technology",
  "company_size": "11-50",
  "description": "Leading tech solutions provider",
  "logo_url": "https://acme.com/logo.png"
}
```

**Response:**
```json
{
  "id": "profile-uuid",
  "user_id": "user-uuid",
  "business_name": "Acme Corp",
  "company_id": "ACME-001",
  "phone": "+1-555-123-4567",
  "website": "https://acme.com",
  "address": "123 Main St",
  "city": "Springfield",
  "state": "IL",
  "postal_code": "62701",
  "country": "USA",
  "industry": "Technology",
  "company_size": "11-50",
  "description": "Leading tech solutions provider",
  "logo_url": "https://acme.com/logo.png",
  "created_at": "2026-03-27T...",
  "updated_at": "2026-03-27T..."
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid data or duplicate company_id
- `401` - Unauthorized
- `500` - Server error

#### GET `/auth/profile`
Get user's profile.

**Response:**
```json
{
  "id": "profile-uuid",
  "user_id": "user-uuid",
  "business_name": "Acme Corp",
  "company_id": "ACME-001",
  ...
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `404` - Profile not found
- `500` - Server error

#### GET `/auth/profile/full`
Get user with complete profile information.

**Response:**
```json
{
  "id": "user-uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2026-03-27T...",
  "profile": {
    "id": "profile-uuid",
    "user_id": "user-uuid",
    "business_name": "Acme Corp",
    ...
  }
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `500` - Server error

## Setup

### 1. Install Dependencies

Add to `requirements.txt`:
```
python-jose[cryptography]
passlib[bcrypt]
```

Run:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Update `.env`:
```env
# JWT Configuration
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important:** Change `SECRET_KEY` in production to a strong random string:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Database Migrations

Models are automatically created when the app starts due to SQLModel.

## Usage Examples

### 1. User Registration
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### 2. User Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

Save the `access_token` from response for authenticated requests.

### 3. Get Current User (Protected)
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### 4. Create Profile (Protected)
```bash
curl -X POST http://localhost:8000/auth/profile \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Acme Corp",
    "company_id": "ACME-001",
    "phone": "+1-555-123-4567",
    "website": "https://acme.com",
    "industry": "Technology"
  }'
```

### 5. Reset Password (Protected)
```bash
curl -X POST http://localhost:8000/auth/reset-password \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePass123",
    "new_password": "NewSecurePass456"
  }'
```

## Security Features

### Password Security
- Passwords hashed using bcrypt (automatic salting)
- Passwords never stored in plaintext
- Password verification uses constant-time comparison

### Token Security
- JWT tokens with configurable expiration
- Token validation on each protected request
- User active status checked during authentication

### API Security
- Protected endpoints require valid token
- Automatic user extraction from token
- User activity status validated

### Email Notifications
- Welcome email on signup
- Password reset email for forgot password
- Emails sent asynchronously

## Error Handling

All errors return appropriate HTTP status codes:
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid/expired token)
- `403` - Forbidden (user deactivated)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

## Best Practices

### Frontend Integration

1. **Store Token Securely**
   - Use secure HTTP-only cookies or secure local storage
   - Never expose token in URLs

2. **Add Token to Headers**
   ```javascript
   const headers = {
     'Authorization': `Bearer ${token}`,
     'Content-Type': 'application/json'
   };
   ```

3. **Handle Token Expiration**
   - Redirect to login on 401 response
   - Implement token refresh if desired

### Backend Integration

1. **Use Current User Dependency**
   ```python
   @router.get("/some-protected-endpoint")
   async def protected(current_user = Depends(get_current_active_user)):
       return {"user": current_user}
   ```

2. **Access User Information**
   ```python
   user_id = current_user.id
   user_email = current_user.email
   ```

## Troubleshooting

### "Invalid or expired token"
- Token may have expired (default 30 minutes)
- User may have been deactivated
- Secret key changed

### "User not found"
- User was deleted from database
- Token contains invalid user ID

### "User account is deactivated"
- User called deactivation endpoint
- Account was disabled by admin

### "Email already registered"
- Email already exists in database
- Use login instead or forgot password

## Future Enhancements

- [ ] Email verification on signup
- [ ] Multi-factor authentication
- [ ] OAuth2 integration (Google, GitHub)
- [ ] Refresh token implementation
- [ ] Session management
- [ ] Role-based access control (RBAC)
- [ ] API key authentication for apps
- [ ] User deletion/account closure
