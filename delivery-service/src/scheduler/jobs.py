from decimal import Decimal
from venv import logger
from db.session import get_session_db, get_db_session
from db.dals import PackageDAL
from db.models import Package

from typing import  Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from scheduler.work_with_api import get_currency

from decimal import Decimal

def calculation_cost_delivery(weight: Decimal, 
                              package_cost: Decimal,
                              valute_usd: Decimal):
    cost_delivery = (weight * Decimal('0.5') + package_cost * Decimal("0.01")) * valute_usd
    return cost_delivery



async def get_packages_without_cost(db_session: AsyncSession) -> Optional[list[Package]]:
    package_dal = PackageDAL(db_session)
    packages = await package_dal.get_package_delivery_cost_none()
    return packages
    
async def update_delivery_cost_packages(db_session: AsyncSession, package_mappings: dict[Package, Decimal]):
    package_dal = PackageDAL(db_session)
    await package_dal.update_bulk_delivery_cost_by_package(package_mappings)


async def add_cost_delivery():
    async with get_db_session() as db_session:
        async with db_session.begin():
            packages = await get_packages_without_cost(db_session)
            if not packages:
                return False
            
            valute_usd = await get_currency('USD')
            package_mappings = {}
            for package in packages:
                delivery_cost = calculation_cost_delivery(
                    package.weight,
                    package.package_cost,
                    Decimal(valute_usd)
                )
                package_mappings[package] = delivery_cost
            await update_delivery_cost_packages(db_session, package_mappings)
        
    return True

    
    
    