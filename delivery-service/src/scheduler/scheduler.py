import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from scheduler.jobs import add_cost_delivery

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis

scheduler = AsyncIOScheduler()

logger = logging.getLogger(__name__)
logger.error("Планировщик обновления курсов валют запущен")

@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncIterator[None]:
    try:
        start_scheduler(scheduler)
        start_redis_cache()
    except:
        raise

    yield
    stop_scheduler(scheduler)
    

def start_scheduler(scheduler: AsyncIOScheduler):
    try:
        scheduler.add_job(
            add_cost_delivery,
            trigger=IntervalTrigger(minutes=5),
            id='currency_update_job',
            replace_existing=True
        )
        scheduler.start()
        logger.error("Планировщик обновления курсов валют запущен")
    except Exception as e:
        logger.error(f"Ошибка инициализации планировщика: {e}")

def stop_scheduler(scheduler: AsyncIOScheduler):
    scheduler.shutdown()
    logger.info("Планировщик обновления курсов валют остановлен")

def start_redis_cache():
    redis = aioredis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
