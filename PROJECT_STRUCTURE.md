# Email Marketing Project - Updated Structure

Complete project structure after implementing authentication and email systems.

```
email_marketing/
├── app/
│   ├── __pycache__/
│   ├── api/
│   │   ├── __pycache__/
│   │   ├── auth.py              ✨ NEW - Authentication endpoints
│   │   ├── email.py             - Email endpoints
│   │   └── scrape.py            - Scraping endpoints
│   │
│   ├── core/
│   │   ├── __pycache__/
│   │   └── settings.py          ✏️ UPDATED - Added JWT config
│   │
│   ├── db/
│   │   ├── __pycache__/
│   │   └── session.py           - Database session
│   │
│   ├── dependencies/
│   │   ├── __pycache__/
│   │   ├── current_user.py      ✨ NEW - Current user dependency
│   │   ├── email.py             - Email dependencies
│   │   ├── jwt_handler.py       ✨ NEW - JWT token handling
│   │   ├── password_utils.py    ✨ NEW - Password hashing
│   │   ├── scrape.py            - Scraping dependencies
│   │   └── smtp_email.py        - SMTP email service
│   │
│   ├── middleware/
│   │   └── (empty)
│   │
│   ├── model/
│   │   ├── __pycache__/
│   │   ├── emails.py            - Email model
│   │   └── user.py              ✨ NEW - User & Profile models
│   │
│   ├── repo/
│   │   ├── __pycache__/
│   │   ├── email.py             - Email repository
│   │   ├── profile.py           ✨ NEW - Profile repository
│   │   └── user.py              ✨ NEW - User repository
│   │
│   ├── schema/
│   │   ├── __pycache__/
│   │   ├── auth.py              ✨ NEW - Auth schemas
│   │   ├── email.py             - Email schemas
│   │   └── scrape.py            - Scrape schemas
│   │
│   ├── service/
│   │   ├── __pycache__/
│   │   ├── auth_service.py      ✨ NEW - Auth business logic
│   │   ├── cdx_resume_state.txt - Service file
│   │   ├── email_service.py     - Email service
│   │   ├── known_domains.txt    - Service file
│   │   ├── my_uk_list.csv       - Service file
│   │   ├── scrape_email.py      - Email scraper
│   │   └── uk_*_service.py      - UK email services
│   │
│   └── main.py                  ✏️ UPDATED - Added auth router
│
├── .env.example                 ✏️ UPDATED - Added JWT config
├── .env                         - Local env vars (not in git)
├── requirements.txt             - Python dependencies
│
├── AUTH_SYSTEM_README.md        ✨ NEW - Auth documentation
├── AUTH_QUICKSTART.md           ✨ NEW - Quick start guide
├── EMAIL_SYSTEM_README.md       - Email system docs
├── IMPLEMENTATION_SUMMARY.md    ✨ NEW - Implementation summary
└── README.md                    - Project readme (if exists)

KEY:
✨ NEW - New file created
✏️ UPDATED - Modified existing file
- Unchanged existing file
```

## New User Models & Tables

### User Table (SQLModel: app/model/user.py)
```python
User(SQLModel, table=True):
    id: str (UUID, PK)
    email: str (unique, indexed)
    name: str
    password_hash: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
```

### Profile Table (SQLModel: app/model/user.py)
```python
Profile(SQLModel, table=True):
    id: str (UUID, PK)
    user_id: str (FK to users.id, unique)
    business_name: str
    company_id: str (unique, indexed)
    phone: Optional[str]
    website: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    industry: Optional[str]
    company_size: Optional[str]
    description: Optional[str]
    logo_url: Optional[str]
    created_at: datetime
    updated_at: datetime
```

## New API Endpoints

### Authentication Routes (/auth)

**Public Endpoints:**
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Authenticate user
- `POST /auth/forgot-password` - Request password reset

**Protected Endpoints (Bearer Token):**
- `GET /auth/me` - Get current user
- `POST /auth/reset-password` - Change password
- `POST /auth/profile` - Create/update profile
- `GET /auth/profile` - Get user profile
- `GET /auth/profile/full` - Get user with profile

## New Dependencies

Add to `requirements.txt`:
```
python-jose[cryptography]>=0.3.3
passlib[bcrypt]>=1.7.4
```

## Configuration

Add to `.env`:
```env
SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Key Features

### Authentication ✅
- User signup with validation
- User login with password verification
- JWT token generation & validation
- Password hashing (bcrypt)
- Protected endpoints with token auth

### User Profile ✅
- Create/update user profile
- Store business information
- Company ID uniqueness
- Additional contact & company details

### Password Management ✅
- Secure password reset for logged-in users
- Forgot password with email reset link
- Password strength validation (min 8 chars)
- Bcrypt hashing with auto salting

### Security ✅
- Bcrypt password hashing
- JWT with expiration
- Token validation on protected endpoints
- User active status verification
- Secure password verification

### Email Integration ✅
- Welcome email on signup
- Password reset email
- Integration with SMTP system

## Development Workflow

1. **Setup**
   ```bash
   pip install python-jose[cryptography] passlib[bcrypt]
   ```

2. **Configure**
   ```bash
   # Generate secret key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   # Add to .env
   ```

3. **Run**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Test**
   ```bash
   # Visit http://localhost:8000/docs for Swagger UI
   ```

## File Relationships

```
API Endpoints (app/api/auth.py)
    ↓ uses
Auth Service (app/service/auth_service.py)
    ↓ uses
User Repo (app/repo/user.py) + Profile Repo (app/repo/profile.py)
    ↓ use
Models (app/model/user.py)
    ↓ uses
Password Utils (app/dependencies/password_utils.py)
JWT Handler (app/dependencies/jwt_handler.py)
SMTP Email (app/dependencies/smtp_email.py)
    ↓ for
Current User Dependency (app/dependencies/current_user.py)
    ↓ for
Protected Endpoints
```

## Integration Points

### With Email System
- Signup sends welcome email
- Forgot password sends reset email
- Can associate scraped emails with user

### With Scraper
- Authenticate user before scraping
- Save scraped emails under user account
- Track scraping history per user

### With Existing Models
- Database uses same SQLModel/AsyncSession
- Same error handling patterns
- Consistent API response formats

## Production Checklist

- [ ] Change SECRET_KEY to strong value
- [ ] Enable HTTPS
- [ ] Configure CORS if needed
- [ ] Add rate limiting on auth endpoints
- [ ] Implement refresh tokens
- [ ] Add email verification
- [ ] Setup monitoring/logging
- [ ] Regular database backups
- [ ] Security audit
- [ ] Load testing

## Quick Commands

```bash
# Install dependencies
pip install python-jose[cryptography] passlib[bcrypt]

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Start dev server
python -m uvicorn app.main:app --reload

# View API docs
open http://localhost:8000/docs

# Test signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"TestPass123"}'

# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```

## Documentation

- **AUTH_SYSTEM_README.md** - Complete auth system documentation with all endpoints
- **AUTH_QUICKSTART.md** - Quick start guide with curl examples
- **EMAIL_SYSTEM_README.md** - Email system documentation
- **IMPLEMENTATION_SUMMARY.md** - Full implementation summary
- **This file** - Project structure overview

---

**Status:** ✅ Complete and Ready for Use

All authentication and user management features have been fully implemented following FastAPI best practices with proper error handling, validation, and security measures.
