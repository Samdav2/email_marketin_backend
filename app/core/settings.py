import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///email.db")

    # Email Provider Selection ("resend", "smtp", "mailjet")
    EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "resend")

    # Resend Configuration
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    RESEND_FROM_EMAIL: str = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
    RESEND_FROM_NAME: str = os.getenv("RESEND_FROM_NAME", "Email Marketing")

    # SMTP Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASS: str = os.getenv("SMTP_PASS", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "info@thinkedgeconsultancy.com")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Email Marketing")
    SMTP_TO: str = os.getenv("SMTP_TO", "")

    # Mailjet Configuration
    MAILJET_API_KEY: str = os.getenv("MAILJET_API_KEY", "")
    MAILJET_SECRET_KEY: str = os.getenv("MAILJET_SECRET_KEY", "")
    MAILJET_SENDER_NAME: str = os.getenv("MAILJET_SENDER_NAME", "Email Marketing")

    # General Mail Defaults
    MAIL_FROM: str = os.getenv("MAIL_FROM", os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev"))
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "Email Marketing")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://nextmail.thinkedgeconsultancy.com,https://emailmarketingfrontend-production.up.railway.app")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Email Marketing & Scraper")

    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


settings = Settings()
