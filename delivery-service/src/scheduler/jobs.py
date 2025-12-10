from decimal import Decimal
from venv import logger

from db.dals import PackageDAL
from domain.dto import PackageData

from typing import  Optional

from scheduler.work_with_api import get_currency

from decimal import Decimal


def calculation_cost_delivery(weight: Decimal, 
                              package_cost: Decimal,
                              valute_usd: Decimal):
    cost_delivery = (weight * Decimal('0.5') + package_cost * Decimal("0.01")) * valute_usd
    return cost_delivery



async def get_packages_without_cost() -> Optional[list[PackageData]]:
    package_dal = PackageDAL()
    packages = await package_dal.get_package_delivery_cost_none()
    return packages
    
async def update_delivery_cost_packages(packages: list[PackageData]):
    package_dal = PackageDAL()
    await package_dal.update_bulk_delivery_cost(packages)


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

    
    
    