import aiohttp
import asyncio
import json
import logging
from decimal import Decimal
from fastapi_cache.decorator import cache



logger = logging.getLogger(__name__)

BASE_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

async def fetch_get(session: aiohttp.ClientSession):
    async with session.get(f"{BASE_URL}") as response:
       return await response.json(content_type="application/javascript")

@cache(expire=60*60)
async def get_currency(name_valute: str = 'USD') -> Decimal:
    async with aiohttp.ClientSession() as session:
        async with aiohttp.ClientSession() as session:
            response = await asyncio.gather(fetch_get(session))
    valute = response[0]["Valute"][name_valute]["Value"]
    logger.debug(f"USD {valute}")
    return Decimal(valute)


