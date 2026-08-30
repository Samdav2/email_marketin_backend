# Complete Railway Deployment Guide (Backend & Frontend)

This guide provides step-by-step instructions for deploying the **FastAPI Backend** (`email_marketin_backend`) and **Next.js Frontend** (`email_scraper_frontend`) to [Railway.app](https://railway.app) with a production **PostgreSQL Database**.

---

## Step 1: Create a Railway Project

1. Log in to [Railway.app](https://railway.app).
2. Click **New Project** -> Select **Empty Project**.
3. Name your project (e.g., `Email-Marketing-Production`).

---

## Step 2: Deploy Backend & PostgreSQL Database

### A. Add PostgreSQL Database Plugin
1. Inside your Railway project, click **+ New** -> **Database** -> **Add PostgreSQL**.
2. Railway will provision a managed PostgreSQL database.
3. Click on the PostgreSQL service -> **Variables** tab to see `DATABASE_URL` (Railway automatically connects this to your services when requested).

### B. Deploy FastAPI Backend Service
1. Click **+ New** -> **GitHub Repo** (or use Railway CLI `railway up`).
2. Select your `email_marketin_backend` repository.
3. Railway automatically detects `railway.json` and `Dockerfile`.
4. Go to **Variables** tab for the backend service and add the following:
   - `DATABASE_URL`: `${{ Postgres.DATABASE_URL }}` *(Railway auto-completes database connection)*
   - `EMAIL_PROVIDER`: `resend` *(or `smtp` / `mailjet`)*
   - `RESEND_API_KEY`: `re_123456789_your_real_key`
   - `SECRET_KEY`: `generate-a-strong-jwt-secret-key`
   - `FRONTEND_URL`: `https://your-frontend-service.up.railway.app`
   - `CORS_ORIGINS`: `https://your-frontend-service.up.railway.app`
5. Go to **Settings** tab -> **Networking** -> Click **Generate Domain**.
   - Copy your backend public URL (e.g., `https://email-backend-production.up.railway.app`).

---

## Step 3: Deploy Next.js Frontend

1. In the same Railway project, click **+ New** -> **GitHub Repo**.
2. Select your `email_scraper_frontend` repository.
3. Railway automatically detects `railway.json` and `Dockerfile`.
4. Go to **Variables** tab for the frontend service and add:
   - `NEXT_PUBLIC_API_URL`: `https://email-backend-production.up.railway.app` *(Your backend URL from Step 2B)*
   - `NEXT_PUBLIC_APP_NAME`: `Email Marketing & Scraper`
5. Go to **Settings** tab -> **Networking** -> Click **Generate Domain**.
   - Your frontend will be accessible at your public `.up.railway.app` URL or custom domain!

---

## Step 4: Verify Deployment

1. Visit your Backend API Documentation at `https://email-backend-production.up.railway.app/docs`.
2. Open your Frontend site at `https://your-frontend-service.up.railway.app`.
3. Perform a test signup/login and email scrape operation.

---

## Technical Summary of Railway Enhancements Added

- **`railway.json`**: Added configuration files for both services to ensure Railway uses Dockerfile builds and dynamic `$PORT` bindings.
- **Dynamic `$PORT` handling**: Updated backend Dockerfile (`CMD exec uvicorn ... --port ${PORT:-8000}`) and frontend Dockerfile to prevent Railway port mismatch errors.
- **PostgreSQL Async Compatibility**: `app/db/session.py` automatically converts Railway's `postgres://` or `postgresql://` string to `postgresql+asyncpg://`.
- **CORS Handling**: `app/main.py` parses `CORS_ORIGINS` and `FRONTEND_URL` so browser requests succeed without CORS preflight blocks.
