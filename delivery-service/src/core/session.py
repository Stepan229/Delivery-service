from typing import Generator
from core.settings import DATABASE_URL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis

import asyncio
from asyncio import AbstractEventLoop

from core.settings import REDIS_URL

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

def start_redis_cache():
    redis = aioredis.from_url(REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
