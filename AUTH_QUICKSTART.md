# Authentication System Quick Start Guide

## Files Created

### Models
- `app/model/user.py` - User and Profile models

### Schemas
- `app/schema/auth.py` - Authentication and profile request/response schemas

### Repositories
- `app/repo/user.py` - User database operations
- `app/repo/profile.py` - Profile database operations

### Services
- `app/service/auth_service.py` - Authentication business logic
- `app/dependencies/jwt_handler.py` - JWT token management
- `app/dependencies/password_utils.py` - Password hashing utilities
- `app/dependencies/current_user.py` - User extraction from token

### API
- `app/api/auth.py` - Authentication endpoints

### Updated Files
- `app/main.py` - Added auth router
- `app/core/settings.py` - Added JWT configuration
- `.env.example` - Added JWT settings

## Installation

### 1. Install Required Packages
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

### 2. Configure Environment
Create `.env` in project root:
```env
# ... existing config ...

# JWT Configuration
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Quick Test

### 1. Start Server
```bash
python -m uvicorn app.main:app --reload
```

### 2. Sign Up
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid...",
    "name": "Test User",
    "email": "test@example.com",
    "is_active": true,
    "created_at": "2026-03-27T..."
  }
}
```

### 3. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

### 4. Create Profile (Replace TOKEN with access_token from signup)
```bash
curl -X POST http://localhost:8000/auth/profile \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "My Company",
    "company_id": "COMP-001",
    "phone": "+1-555-0123",
    "website": "https://mycompany.com",
    "city": "New York",
    "country": "USA",
    "industry": "Technology"
  }'
```

### 5. Get User With Profile
```bash
curl -X GET http://localhost:8000/auth/profile/full \
  -H "Authorization: Bearer TOKEN"
```

### 6. Reset Password
```bash
curl -X POST http://localhost:8000/auth/reset-password \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "TestPass123",
    "new_password": "NewTestPass456"
  }'
```

## Integration with Existing Features

### Using Current User in Other Endpoints

Example in another API endpoint:
```python
from fastapi import APIRouter, Depends
from app.dependencies.current_user import get_current_active_user

router = APIRouter()

@router.get("/protected")
async def protected_endpoint(current_user = Depends(get_current_active_user)):
    return {
        "message": f"Hello {current_user.name}",
        "user_id": current_user.id
    }
```

### Save Emails for Authenticated User

Example of integrating with email scraping:
```python
from app.service.email_service import save_extracted_emails
from app.dependencies.current_user import get_current_active_user

@router.post("/scrape-with-auth")
async def scrape_emails(
    request: ScrapeRequest,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session)
):
    # Scrape emails
    emails = await scrape_email(request)

    # Save to database with user association
    results = await save_extracted_emails(
        emails,
        Category.web,
        db
    )

    return {
        "user": current_user.name,
        "scrape_results": results
    }
```

## API Documentation

### Interactive API Docs
Visit `http://localhost:8000/docs` (Swagger UI)

### Endpoints Overview
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Authenticate user
- `GET /auth/me` - Get current user info
- `POST /auth/reset-password` - Change password
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/profile` - Create/update profile
- `GET /auth/profile` - Get user profile
- `GET /auth/profile/full` - Get user with profile

See `AUTH_SYSTEM_README.md` for detailed endpoint documentation.

## Common Issues

### ModuleNotFoundError: No module named 'passlib'
```bash
pip install passlib[bcrypt]
```

### ModuleNotFoundError: No module named 'jose'
```bash
pip install python-jose[cryptography]
```

### "Invalid or expired token"
- Token has expired (30 minutes default)
- Use login to get a new token

### "Email already registered"
- Email already exists
- Use login to authenticate instead

## Database Schema

The system automatically creates:
- `users` table - User accounts
- `profiles` table - User business profiles

Tables are created automatically on first app startup.

## Security Notes

✅ Passwords hashed with bcrypt
✅ JWT tokens with expiration
✅ Protected endpoints with token validation
✅ User activity status checking
✅ Password reset via email
✅ Welcome email on signup

⚠️ Change SECRET_KEY in production
⚠️ Use HTTPS in production
⚠️ Keep JWT_ALGORITHM to HS256 or RS256

## Next Steps

1. ✅ Test signup and login
2. ✅ Create user profile
3. ✅ Integrate with existing endpoints
4. ✅ Add role-based access control (RBAC) if needed
5. ✅ Add email verification
6. ✅ Implement refresh tokens

## Support

For issues or questions, check:
- `AUTH_SYSTEM_README.md` - Full documentation
- Error logs in terminal
- FastAPI docs at `/docs` endpoint
