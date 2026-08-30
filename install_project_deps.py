import subprocess
import sys

# === List of project-specific required packages ===
packages = [
    "fastapi==0.124.4",
    "sqlmodel==0.0.27",
    "sqlalchemy==2.0.44",
    "pydantic==2.12.3",
    "pydantic-settings==2.6.1",
    "uvicorn==0.38.0",
    "requests==2.32.5",
    "mailjet-rest==1.5.1",
    "Jinja2==3.1.6",
    "python-dotenv==1.2.1",
    "python-jose==3.5.0",
    "python-multipart==0.0.20",
    "passlib==1.7.4",
    "bcrypt==3.2.2",
    "httpx==0.28.1",
    "beautifulsoup4==4.12.3",
    "aiosqlite==0.21.0",
    "slowapi==0.1.9",
    "cdx-toolkit==0.6.14",
    "alembic==1.17.2",
    "starlette==0.49.3",
    "anyio==4.12.0",
    "a2wsgi==1.10.7",
    "psycopg[binary]",
    "email-validator>=2.0.0",
    "cdx-toolkit",
    "asyncpg",
    "resend"
]

def install(package):
    """Install a Python package using pip."""
    try:
        print(f"📦 Installing {package} ...")
        # Use sys.executable to ensure pip is from the correct virtual env
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}\n")

if __name__ == "__main__":
    print("--- Starting project dependency installation ---")
    for pkg in packages:
        install(pkg)
    print("--- All project packages processed ---")
