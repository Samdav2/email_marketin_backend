# Quick Reference & Testing Guide

---

## Quick API Reference

### Authentication
- `POST /auth/signup` - Create account
- `POST /auth/login` - Login
- `POST /auth/reset-password` - Change password
- `POST /auth/forgot-password` - Reset password
- `GET /auth/me` - Get current user
- `POST /auth/profile` - Create/update profile
- `GET /auth/profile` - Get user profile
- `GET /auth/profile/full` - Get user with profile

### Email Management
- `GET /emails/all` - List all scraped emails
- `GET /emails/templates` - List email templates
- `GET /emails/templates/{id}` - Get template
- `POST /emails/templates` - Create template
- `PATCH /emails/templates/{id}` - Update template
- `DELETE /emails/templates/{id}` - Delete template
- `POST /emails/send` - Send single email
- `POST /emails/send-bulk` - Send bulk emails

### Scraping
- `POST /scrape/scrape-to-db` - Scrape and save emails

---

## Default Email Templates

The system includes 10 pre-built professional templates:

### 1. NEWSLETTER Template
**Subject:** "Your Weekly Newsletter"
- Weekly updates for subscribers
- Includes header, content sections, and footer
- Professional styling with company branding

### 2. PROMOTIONAL Template
**Subject:** "Limited Time Offer"
- Marketing promotions and discounts
- Call-to-action buttons
- Urgency elements (time limits)

### 3. ANNOUNCEMENT Template
**Subject:** "Important Announcement"
- Company announcements
- Product launches
- Major updates

### 4. PRODUCT Template
**Subject:** "Check Out Our New Product"
- Product showcases
- Features and benefits
- Pricing information

### 5. EVENT Template
**Subject:** "You're Invited to Our Event"
- Event invitations
- Date/time details
- Registration link

### 6. WEBINAR Template
**Subject:** "Join Us for an Educational Webinar"
- Webinar promotions
- Topic highlights
- Registration information

### 7. ONBOARDING Template
**Subject:** "Welcome to Our Platform"
- New user welcome
- Getting started guide
- Useful resources

### 8. FEEDBACK Template
**Subject:** "We'd Love Your Feedback"
- Customer surveys
- Review requests
- Feedback incentives

### 9. RETENTION Template
**Subject:** "We Miss You! Special Offer Inside"
- Re-engagement campaigns
- Win-back offers
- Personalized content

### 10. SALES Template
**Subject:** "Exclusive Opportunity for You"
- Sales outreach
- Lead follow-up
- Proposal templates

---

## Testing with cURL

### Test Signup
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### Test Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### Test Get All Emails
```bash
curl -X GET http://localhost:8000/emails/all \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Test Get Templates
```bash
curl -X GET http://localhost:8000/emails/templates \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Test Send Single Email
```bash
curl -X POST http://localhost:8000/emails/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "recipient_email": "customer@example.com",
    "template_id": "TEMPLATE_UUID",
    "variables": {
      "recipient_name": "John",
      "company_name": "Acme"
    }
  }'
```

### Test Scrape to DB
```bash
curl -X POST http://localhost:8000/scrape/scrape-to-db \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "email_limit": 500,
    "domain_limit": 50,
    "category": "WEB"
  }'
```

### Test Create Profile
```bash
curl -X POST http://localhost:8000/auth/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "business_name": "Acme Corporation",
    "company_id": "ACME001",
    "phone": "+1-555-0100",
    "website": "https://example.com",
    "industry": "Technology"
  }'
```

---

## Testing with Postman

### Import API Collection

1. Open Postman
2. Click "Import"
3. Paste this JSON structure:

```json
{
  "info": {
    "name": "Email Marketing API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Signup",
          "request": {
            "method": "POST",
            "url": "http://localhost:8000/auth/signup",
            "body": {
              "mode": "raw",
              "raw": "{\"name\": \"John Doe\", \"email\": \"john@example.com\", \"password\": \"SecurePass123\"}"
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "http://localhost:8000/auth/login",
            "body": {
              "mode": "raw",
              "raw": "{\"email\": \"john@example.com\", \"password\": \"SecurePass123\"}"
            }
          }
        }
      ]
    }
  ]
}
```

---

## Testing in JavaScript

### Setup Test Environment

```javascript
const API_URL = 'http://localhost:8000';
let token = '';

// Helper function for API calls
async function apiCall(method, endpoint, data = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    }
  };

  if (data) options.body = JSON.stringify(data);

  const response = await fetch(`${API_URL}${endpoint}`, options);
  const result = await response.json();

  if (!response.ok) throw result;
  return result;
}

// Test signup
async function testSignup() {
  try {
    const result = await apiCall('POST', '/auth/signup', {
      name: 'John Doe',
      email: `john${Date.now()}@example.com`,
      password: 'SecurePass123'
    });
    token = result.access_token;
    console.log('✓ Signup successful:', result.user);
    return result;
  } catch (error) {
    console.error('✗ Signup failed:', error);
  }
}

// Test get emails
async function testGetEmails() {
  try {
    const result = await apiCall('GET', '/emails/all');
    console.log('✓ Got emails:', result.total);
    return result;
  } catch (error) {
    console.error('✗ Get emails failed:', error);
  }
}

// Test get templates
async function testGetTemplates() {
  try {
    const result = await apiCall('GET', '/emails/templates');
    console.log('✓ Got templates:', result.length);
    return result;
  } catch (error) {
    console.error('✗ Get templates failed:', error);
  }
}

// Test send email
async function testSendEmail(templateId) {
  try {
    const result = await apiCall('POST', '/emails/send', {
      recipient_email: 'test@example.com',
      template_id: templateId,
      variables: { name: 'Test User' }
    });
    console.log('✓ Email sent:', result);
    return result;
  } catch (error) {
    console.error('✗ Send email failed:', error);
  }
}

// Run all tests
async function runAllTests() {
  console.log('Starting API tests...\n');

  await testSignup();
  console.log();

  const emails = await testGetEmails();
  console.log();

  const templates = await testGetTemplates();
  console.log();

  if (templates && templates.length > 0) {
    await testSendEmail(templates[0].id);
  }

  console.log('\nTests completed!');
}

// Execute tests
runAllTests();
```

---

## Frontend Testing Scenarios

### User Journey 1: First-Time User

```
1. Visit website
2. Click "Sign Up"
3. Enter name, email, password
4. Click "Create Account"
5. Receive welcome email (background)
6. Auto-redirect to setup profile
7. Fill business information
8. Create profile
9. Redirect to dashboard
```

### User Journey 2: Email Campaign

```
1. Login to dashboard
2. Navigate to "Email Management"
3. Click "View All Emails"
4. See 0 emails (first time)
5. Navigate to "Scrape"
6. Set email limit: 1000
7. Set domain limit: 100
8. Click "Start Scraping"
9. Wait for completion (5-10 minutes)
10. See results: "1000 emails collected"
11. Navigate back to "Email Management"
12. See all scraped emails
13. Click "Send Campaign"
14. Select template
15. Click "Send"
16. See confirmation: "Sent to X recipients"
```

### User Journey 3: Custom Template

```
1. Navigate to "Email Templates"
2. Click "Create New Template"
3. Enter template name
4. Select template type: "PROMOTIONAL"
5. Enter subject line
6. Enter HTML body
7. Click "Create"
8. See new template in list
9. Click "Send With This"
10. Select recipients
11. Click "Send"
```

---

## Performance Testing

### Bulk Email Load Test

```javascript
// Send to 10,000 emails (in chunks)
async function loadTestBulkEmail() {
  const emails = Array.from({ length: 10000 }, (_, i) => `test${i}@example.com`);

  const startTime = performance.now();

  try {
    const result = await apiCall('POST', '/emails/send-bulk', {
      recipient_emails: emails,
      template_id: 'TEMPLATE_ID',
      variables: { company: 'Test' }
    });

    const endTime = performance.now();
    console.log(`Bulk email sent in ${(endTime - startTime) / 1000}s`);
    console.log(`Success: ${result.successful}, Failed: ${result.failed}`);
  } catch (error) {
    console.error('Load test failed:', error);
  }
}
```

### Scraping Performance Test

```javascript
// Test scraping with different domain limits
async function performanceTest() {
  const limits = [10, 50, 100, 500, 1000];

  for (const limit of limits) {
    const startTime = performance.now();

    try {
      await apiCall('POST', '/scrape/scrape-to-db', {
        email_limit: 5000,
        domain_limit: limit,
        category: 'WEB'
      });

      const endTime = performance.now();
      console.log(`Domain limit ${limit}: ${(endTime - startTime) / 1000}s`);
    } catch (error) {
      console.error(`Failed for limit ${limit}:`, error);
    }
  }
}
```

---

## Debugging Tips

### Enable API Logging

Add to backend startup:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Monitor Database

```bash
# Connect to PostgreSQL
psql -U postgres -d email_marketing_db

# List tables
\dt

# Check user count
SELECT COUNT(*) FROM user;

# Check email count
SELECT COUNT(*) FROM email;
```

### Check Email Queue

```python
# In backend terminal
python -c "from app.db.session import engine; print(engine.url)"
```

### Frontend Console Tips

```javascript
// Log all API calls
window.addEventListener('fetch', (e) => {
  console.log('Fetch:', e.request.url);
});

// Check localStorage
console.log('Token:', localStorage.getItem('access_token'));

// Decode JWT (for debugging)
function decodeToken(token) {
  const parts = token.split('.');
  const payload = JSON.parse(atob(parts[1]));
  return payload;
}
```

---

## Common Issues & Solutions

### Issue: "Not authenticated" error

**Solution:** Check if token is being sent in Authorization header
```javascript
// Make sure you're using the token
headers: {
  'Authorization': `Bearer ${token}`  // Not 'token' or 'Token'
}
```

### Issue: CORS errors in frontend

**Solution:** Backend needs CORS middleware configured
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Email not sending

**Solution:** Check email configuration
1. Verify Mailjet credentials in `.env`
2. Check email address format
3. Review Mailjet account status

### Issue: Emails not saving during scrape

**Solution:** Ensure database is running
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -U postgres -d email_marketing_db -c "SELECT 1"
```

### Issue: Token expiration

**Solution:** Implement auto-refresh or re-login
```javascript
// Add to API interceptor
if (error.response.status === 401) {
  // Clear token and redirect to login
  localStorage.removeItem('access_token');
  window.location.href = '/login';
}
```

---

## API Response Examples

### Successful Email Send

**Request:**
```bash
POST /emails/send
Authorization: Bearer token
Content-Type: application/json

{
  "recipient_email": "john@example.com",
  "template_id": "uuid-123",
  "variables": {"name": "John"}
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Email sent to john@example.com",
  "recipient": "john@example.com"
}
```

### Bulk Email Statistics

**Request:**
```bash
POST /emails/send-bulk
Authorization: Bearer token

{
  "recipient_emails": ["a@example.com", "b@example.com"],
  "template_id": "uuid-123",
  "variables": {}
}
```

**Response (200 OK):**
```json
{
  "total_recipients": 2,
  "successful": 2,
  "failed": 0,
  "errors": []
}
```

### Scraping Results

**Request:**
```bash
POST /scrape/scrape-to-db
{
  "email_limit": 1000,
  "domain_limit": 100,
  "category": "WEB"
}
```

**Response (200 OK):**
```json
{
  "total_processed": 100,
  "successful_leads": 95,
  "total_emails_found": 450,
  "total_emails_saved": 380,
  "duplicates_skipped": 70,
  "errors": 5,
  "results": [
    {
      "domain": "example.com",
      "emails": ["contact@example.com"],
      "status": "success"
    }
  ]
}
```

---

## Deployment Checklist

### Backend Deployment

- [ ] Set `DEBUG=False` in settings
- [ ] Generate secure `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up email credentials (Mailjet)
- [ ] Configure CORS for production domain
- [ ] Enable HTTPS/SSL
- [ ] Set up logging and monitoring
- [ ] Create database backups
- [ ] Set up error tracking (Sentry)

### Frontend Deployment

- [ ] Update `REACT_APP_API_URL` to production
- [ ] Build production bundle: `npm run build`
- [ ] Set up CDN for static files
- [ ] Enable gzip compression
- [ ] Set up monitoring and analytics
- [ ] Configure domain and DNS
- [ ] Enable HTTPS/SSL

---

## Support Resources

- API Docs: `/docs` (Swagger UI)
- ReDoc: `/redoc` (Alternative docs)
- Backend Logs: `docker logs backend` (if containerized)
- Frontend Logs: Browser DevTools → Console
- Database: PostgreSQL connection for direct queries

---

**Last Updated:** March 28, 2026
**Version:** 1.1
