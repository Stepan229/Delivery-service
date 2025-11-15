from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql+asyncpg://postgres:30062001@localhost:5434/db_delivery_service"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    execution_options={"isolation_level": "READ COMMITTED"},
)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_session_db() -> Generator:
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()