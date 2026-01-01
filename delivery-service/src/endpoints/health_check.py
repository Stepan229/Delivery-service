from enum import Enum
import logging

from fastapi import APIRouter


from schemas.schemas import ShowHealthCheck, HealthCheckStatus

from core.session import get_db_session
from sqlalchemy import text
from redis import ConnectionError
from redis import asyncio as aioredis
from core.settings import REDIS_HOST, REDIS_PORT

logger = logging.getLogger(__name__)


health_check_router = APIRouter()

@health_check_router.get("/", response_model=ShowHealthCheck)
async def get_status_api():
    return ShowHealthCheck(status=HealthCheckStatus.access, name_service="API")

@health_check_router.get("/redis/", response_model=ShowHealthCheck)
async def get_status_redis():
    try:
        redis = await aioredis.from_url(
                f"redis://{REDIS_HOST}:{REDIS_PORT}",
                socket_connect_timeout=2,
                socket_timeout=2
            )
        pong = await redis.ping()
        await redis.close()
    except ConnectionError:
        return ShowHealthCheck(status=HealthCheckStatus.unavailable, name_service="Redis")
    if pong == b"PONG" or pong is True:
        return ShowHealthCheck(status=HealthCheckStatus.access, name_service="Redis")
    return ShowHealthCheck(status=HealthCheckStatus.unavailable, name_service="Redis")

@health_check_router.get("/db/", response_model=ShowHealthCheck)
async def get_status_db():
    try:
        async with get_db_session() as db_session:
            sql = text("SELECT 1;")
            result = await db_session.execute(sql)
    except ConnectionRefusedError:
        return ShowHealthCheck(status=HealthCheckStatus.unavailable, name_service="Database")
    if result.scalars().first() == 1:
        return ShowHealthCheck(status=HealthCheckStatus.access, name_service="Database")
    return ShowHealthCheck(status=HealthCheckStatus.unavailable, name_service="Database")
    
@health_check_router.get("/db/", response_model=ShowHealthCheck)
async def get_status_scheduler():
    try:
        async with get_db_session() as db_session:
            sql = text("SELECT 1;")
            result = await db_session.execute(sql)
    except ConnectionRefusedError:
        return ShowHealthCheck(status=HealthCheckStatus.unavailable, name_service="Database")
    if result.scalars().first() == 1:
        return ShowHealthCheck(status=HealthCheckStatus.access, name_service="Database")
    return ShowHealthCheck(status=HealthCheckStatus.unavailable, name_service="Database")
    


