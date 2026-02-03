from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import declarative_base
from app.config import settings

engine = create_async_engine(
    settings.db_url,
    echo=False,
    poolclass=NullPool,
)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)
Base = declarative_base()


async def get_db():
    async with SessionLocal() as session:
        yield session
