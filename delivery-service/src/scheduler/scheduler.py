import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from scheduler.jobs import add_cost_delivery

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis

import asyncio
from asyncio import AbstractEventLoop

logger = logging.getLogger(__name__)
from settings import REDIS_HOST, REDIS_PORT

@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncIterator[None]:
    try:
        start_redis_cache()
    except:
        raise

    yield
    

def start_scheduler():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    scheduler_instance = AsyncIOScheduler(event_loop=loop)

    start_redis_cache()

    try:
        
        scheduler_instance.add_job(
            add_cost_delivery,
            trigger=IntervalTrigger(seconds=2),
            id='currency_update_job',
            replace_existing=True
        )
        loop.run_until_complete(async_start_scheduler(scheduler_instance))
        logger.error("Планировщик обновления курсов валют запущен")


        try:
            loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Получен сигнал остановки")
        finally:
            stop_scheduler(scheduler_instance, loop)

    except Exception as e:
        logger.error(f"Ошибка инициализации планировщика: {e}", exc_info=True)
    
def stop_scheduler(scheduler: AsyncIOScheduler, loop: AbstractEventLoop):
    if scheduler.running:
        loop.run_until_complete(async_stop_scheduler(scheduler))


async def async_start_scheduler(scheduler: AsyncIOScheduler):
    scheduler.start()


async def async_stop_scheduler(scheduler: AsyncIOScheduler):
    scheduler.shutdown(wait=False)
    logger.info("Планировщик обновления курсов валют остановлен")

def start_redis_cache():
    redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
