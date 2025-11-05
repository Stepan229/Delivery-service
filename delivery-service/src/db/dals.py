from typing import Union
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Package
from db.models import TypePackage

import logging

logger = logging.getLogger(__name__)

class BaseDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

class PackageDAL(BaseDAL):
    async def create_package(
            self,
            title: str,
            cost: float,
            weight: float,
            type_package_id: UUID
    ) -> Package:
        new_package = Package(
            title=title,
            cost=cost,
            weight=weight,
            type_package_id=type_package_id
        )
        self.db_session.add(new_package)
        await self.db_session.flush()
        return new_package
        
class TypePackageDAL(BaseDAL):
    async def create_type_package(
            self,
            name: str
    ) -> TypePackage:
        new_type_package = TypePackage(
            name=name
        )
        self.db_session.add(new_type_package)
        await self.db_session.flush()
        return new_type_package

    async def get_type_package_by_name(
            self,
            name: str
    ) -> Union[TypePackage, None]:
        query = select(TypePackage).where(TypePackage.name == name)
        result = await self.db_session.execute(query)
        type_package = result.scalars().first()
        logger.info(f"Retrieved type package: {type_package}")
        return type_package