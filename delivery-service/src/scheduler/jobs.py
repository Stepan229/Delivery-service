from decimal import Decimal
from venv import logger

from repositories.dals import PackageDAL
from domain.dto import PackageData

from typing import  Optional

from repositories.work_with_api import get_currency
from services.package_actions import get_packages_without_cost, update_delivery_cost_packages

from decimal import Decimal


def calculation_cost_delivery(weight: Decimal, 
                              package_cost: Decimal,
                              valute_usd: Decimal):
    cost_delivery = (weight * Decimal('0.5') + package_cost * Decimal("0.01")) * valute_usd
    return cost_delivery


async def add_cost_delivery():

    packages = await get_packages_without_cost()
    if not packages:
        return False
    
    valute_usd = await get_currency('USD')

    for package in packages:
        delivery_cost = calculation_cost_delivery(
            package.weight,
            package.package_cost,
            valute_usd
        )
        package.delivery_cost = delivery_cost
    await update_delivery_cost_packages(packages)
    logger.info(f"Стоимость доставки расчитана для {len(packages)} посылок")
    return True

    
    
    