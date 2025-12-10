from enum import Enum
import logging
from os import access
from fastapi import APIRouter, Path
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from schemas.schemas import CreatePackageSchema, CreateTypePackageSchema
from schemas.schemas import ShowHealthCheck, HealthCheckStatus


from db.session import get_session_db

from db.models import UserSession

from services.actions import _create_new_package, create_new_type_package, get_user, get_packages_by_user_session, get_all_type_packages, _get_package_by_id

from fastapi_filter import FilterDepends

from domain.dto import PackageData, TypePackageData, UserSessionData, FilterPackageData, PaginationPackageData
from schemas.filters import PaginationParams, PackageFilterParams
from dataclasses import asdict
from db.session import get_db_session
from sqlalchemy import text
import redis 
from redis import ConnectionError
from redis import asyncio as aioredis
from settings import REDIS_HOST, REDIS_PORT

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
    

