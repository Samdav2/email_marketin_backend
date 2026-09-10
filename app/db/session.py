from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession as SQLAlchemyAsyncSession
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.settings import settings

# Import all models to ensure they're registered with SQLModel
from app.model.user import User, Profile
from app.model.emails import Email, Campaign, ScrapedDomain, ScraperState
from app.model.email_template import EmailTemplate


db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine_kwargs = {"pool_pre_ping": True}
if "sqlite" in db_url:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 2
    engine_kwargs["connect_args"] = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0
    }

engine = create_async_engine(
    url=db_url,
    **engine_kwargs
)

async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

async def init_db() -> None:
    # 1. Ensure all tables are created
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    is_postgres = "postgres" in engine.dialect.name
    logger.info(f"Running database initialization (dialect: {engine.dialect.name})")

    if is_postgres:
        migrations = [
            # Ensure columns exist on PostgreSQL
            "ALTER TABLE emails ADD COLUMN IF NOT EXISTS domain VARCHAR",
            "ALTER TABLE emails ADD COLUMN IF NOT EXISTS subcategory VARCHAR",
            "ALTER TABLE emails ADD COLUMN IF NOT EXISTS country VARCHAR",
            "ALTER TABLE emails ADD COLUMN IF NOT EXISTS location VARCHAR",
            "ALTER TABLE scraped_domains ADD COLUMN IF NOT EXISTS category VARCHAR",
            "ALTER TABLE scraped_domains ADD COLUMN IF NOT EXISTS country VARCHAR",
            "ALTER TABLE scraped_domains ADD COLUMN IF NOT EXISTS location VARCHAR",
            # Drop check constraints that might enforce enum values
            "ALTER TABLE emails DROP CONSTRAINT IF EXISTS emails_category_check",
            "ALTER TABLE campaigns DROP CONSTRAINT IF EXISTS campaigns_category_check",
            # Convert emails.category from ENUM or VARCHAR(X) to VARCHAR(100)
            "ALTER TABLE emails ALTER COLUMN category DROP DEFAULT",
            "ALTER TABLE emails ALTER COLUMN category TYPE VARCHAR(100) USING category::text",
            "ALTER TABLE emails ALTER COLUMN category SET DEFAULT 'GENERAL'",
            # Convert campaigns.category from ENUM or VARCHAR(X) to VARCHAR(100)
            "ALTER TABLE campaigns ALTER COLUMN category DROP DEFAULT",
            "ALTER TABLE campaigns ALTER COLUMN category TYPE VARCHAR(100) USING category::text",
            # Normalize legacy lowercase categories to uppercase
            "UPDATE emails SET category = UPPER(category) WHERE category IS NOT NULL",
            "UPDATE campaigns SET category = UPPER(category) WHERE category IS NOT NULL",
        ]
    else:
        # SQLite migrations
        migrations = [
            "ALTER TABLE emails ADD COLUMN domain VARCHAR",
            "ALTER TABLE emails ADD COLUMN subcategory VARCHAR",
            "ALTER TABLE emails ADD COLUMN country VARCHAR",
            "ALTER TABLE emails ADD COLUMN location VARCHAR",
            "ALTER TABLE scraped_domains ADD COLUMN category VARCHAR",
            "ALTER TABLE scraped_domains ADD COLUMN country VARCHAR",
            "ALTER TABLE scraped_domains ADD COLUMN location VARCHAR",
            "UPDATE emails SET category = UPPER(category) WHERE category IS NOT NULL",
            "UPDATE campaigns SET category = UPPER(category) WHERE category IS NOT NULL",
        ]

    for stmt in migrations:
        try:
            async with engine.begin() as conn:
                await conn.execute(text(stmt))
        except Exception as e:
            # Expected for SQLite if column already exists or if constraint/default doesn't exist
            logger.debug(f"Migration note for '{stmt}': {e}")

    logger.info("Database initialization and migrations completed successfully.")

