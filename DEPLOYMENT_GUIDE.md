# Production Deployment Guide: Email Marketing & Scraper

This guide outlines step-by-step instructions for deploying both the FastAPI Backend (`email_marketin_backend`) and Next.js Frontend (`email_scraper_frontend`).

---

## Architecture Overview

- **Backend:** FastAPI (Python 3.11), SQLModel/SQLAlchemy, Uvicorn / Phusion Passenger WSGI
- **Frontend:** Next.js 16 (React 19), Tailwind CSS, Zustand, Axios
- **Database:** SQLite (default / persistent disk) or PostgreSQL (Recommended for cloud scale)
- **Email Service:** Resend API, SMTP, or Mailjet

---

## Option 1: Vercel (Frontend) + Render / Railway (Backend) [Recommended]

### 1. Backend Deployment (Render or Railway)

1. **Connect Repository:** Push `email_marketin_backend` to GitHub/GitLab.
2. **Create New Web Service:**
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Set Environment Variables:**
   - `DATABASE_URL`: `postgresql+asyncpg://user:pass@host:5432/dbname` or `sqlite+aiosqlite:///email.db`
   - `EMAIL_PROVIDER`: `resend` (or `smtp` / `mailjet`)
   - `RESEND_API_KEY`: `re_...`
   - `SECRET_KEY`: `<generate-random-secret-key>`
   - `CORS_ORIGINS`: `https://your-frontend.vercel.app`
   - `FRONTEND_URL`: `https://your-frontend.vercel.app`

### 2. Frontend Deployment (Vercel)

1. **Import Repository:** Connect `email_scraper_frontend` in Vercel.
2. **Framework Preset:** Next.js
3. **Environment Variables:**
   - `NEXT_PUBLIC_API_URL`: `https://your-backend.onrender.com`
4. **Deploy:** Vercel automatically builds and provides SSL/HTTPS.

---

## Option 2: Docker Compose (Single Server / VPS Deployment)

To deploy both services on a VPS (DigitalOcean, AWS EC2, Linode, Hetzner):

1. **Clone the code to your server:**
   ```bash
   git clone <repo-url>
   cd email_marketin_backend
   ```
2. **Create a `.env` file for production secrets:**
   ```env
   RESEND_API_KEY=re_your_api_key
   SECRET_KEY=your_secure_random_jwt_secret
   ```
3. **Run Docker Compose:**
   ```bash
   docker-compose up --build -d
   ```
4. **Access Applications:**
   - Frontend: `http://<your-server-ip>:3000`
   - Backend API: `http://<your-server-ip>:8000`
   - API Docs: `http://<your-server-ip>:8000/docs`

---

## Option 3: cPanel / WSGI Deployment (Phusion Passenger)

The backend includes a pre-configured `passenger_wsgi.py` for cPanel / Shared Hosting environments.

1. Upload backend files to `public_html/api` (or dedicated directory).
2. Create Python App in cPanel (Select Python 3.10+).
3. Set WSGI entry point to `passenger_wsgi.py`.
4. Install dependencies: `pip install -r requirements.txt`.
5. Restart Python App.

---

## Pre-Deployment Verification Checklist

- [x] Backend syntax & compilation verified (`python3 -m py_compile app/main.py`)
- [x] Dependencies locked in `requirements.txt`
- [x] Dynamic CORS origins configured via `CORS_ORIGINS`
- [x] Frontend Next.js build tested with `npm run build`
- [x] Dockerfile & `.dockerignore` created for both services
