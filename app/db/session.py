from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession as SQLAlchemyAsyncSession
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.settings import settings

# Import all models to ensure they're registered with SQLModel
from app.model.user import User, Profile
from app.model.emails import Email, Campaign
from app.model.email_template import EmailTemplate


engine = create_async_engine(
    url=settings.DATABASE_URL,
    pool_size=10,
    max_overflow=2,
    pool_pre_ping=True,
    echo=True
)

async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
