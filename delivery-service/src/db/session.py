from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

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

from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        session: AsyncSession = session
        try:
            yield session
        except Exception:
            await session.rollback()  
            raise
        finally:
            await session.close() 
