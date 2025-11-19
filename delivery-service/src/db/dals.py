from tkinter import N, NO
from typing import Union, Optional
from uuid import UUID
from decimal import Decimal
from venv import create

from certifi import where
from click import option
from sqlalchemy import Update, and_, bindparam
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Package, UserSession, TypePackage
from api.schemas import ShowTypePackageSchema, ShowPackageSchema
import logging
logger = logging.getLogger(__name__)


class BaseDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


class PackageDAL(BaseDAL):
    async def create_package(
            self,
            title: str,
            package_cost: Decimal,
            weight: Decimal,
            type_package_id: UUID,
            type_package: TypePackage,
            user_id: UUID,
            user: UserSession
    ) -> Package:
        
        new_package = Package(
            title=title,
            package_cost=package_cost,
            weight=weight,
            type_package_id=type_package_id,
            type_package=type_package,
            user_id=user_id,
            user=user
        )

        self.db_session.add(new_package)
        await self.db_session.flush()
        return new_package
    
    async def get_packages_by_user_session(
            self, 
            user: UserSession
        ) -> Optional[list[Package]]:
        query = select(Package).where(Package.user_id == user.id)
        result = await self.db_session.execute(query)
        packages = result.scalars().unique()
        if packages:
            return list(packages)
        return None
    
    async def get_package_by_id(
            self,
            package_id: str,
            user_session: UserSession
    ) -> Optional[Package]:
        query = select(Package)\
            .where(Package.user_id == user_session.id)\
            .where(Package.id == package_id)
        result = await self.db_session.execute(query)
        package = result.scalars().first()
        if package:
            return package
        return None
    
    async def get_package_delivery_cost_none(self) -> Optional[list[Package]]:
        query = select(Package)\
            .filter(Package.delivery_cost.is_(None))
        result = await self.db_session.execute(query)
        packages = result.scalars().unique()
        if packages:
            return list(packages)
        return None
    
    async def update_bulk_delivery_cost_by_package(self, data: dict[Package, Decimal]):
        # Словарь должен содержать ключи package_id и delivery_cost
        for package, delivery_cost  in data.items():
            package.delivery_cost = delivery_cost
        await self.db_session.commit()


        
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
    
    async def get_all_type_package(self) -> Optional[list[TypePackage]]:
        result = await self.db_session.execute(select(TypePackage))
        types_package = list(result.scalars().unique())
        if types_package:
            return types_package
        return None

    async def get_type_package_by_name(
            self,
            name: str
    ) -> Optional[TypePackage]:
        query = select(TypePackage).where(TypePackage.name == name)
        result = await self.db_session.execute(query)
        type_package = result.scalars().first()
        if type_package:
            return type_package
        return None
    
    
class UserSessionDAL(BaseDAL):
    async def create_session(
            self,
            id_session

    ) -> UserSession:
        
        new_user = UserSession(
            id_session = id_session
        )

        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user
    
    async def get_session_by_session(self, session: str) -> Optional[UserSession]:
        query = select(UserSession).where(UserSession.id_session == session)
        result = await self.db_session.execute(query)
        user_session = result.scalars().first()
        if result:
            return user_session
        return None
    
    async def get_session_by_id(self, session: str) -> Optional[UserSession]:
        query = select(UserSession).where(UserSession.id == id)
        result = await self.db_session.execute(query)
        user_session = result.scalars().first()
        if result:
            return user_session
        return None



