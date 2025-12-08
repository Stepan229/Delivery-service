from abc import abstractmethod
from ast import stmt
from tkinter import N, NO
from typing import Union, Optional
from uuid import UUID, uuid4
from decimal import Decimal
from venv import create

from certifi import where
from click import option
from sqlalchemy import Update, and_, bindparam
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case

from db.models import Package, UserSession, TypePackage
from db.session import get_db_session

from schemas.schemas import ShowTypePackageSchema, ShowPackageSchema


from domain.dto import PackageData, TypePackageData, UserSessionData
from domain.dto import FilterPackageData, PaginationPackageData

import logging
logger = logging.getLogger(__name__)


class BaseDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


class AbstractPackage:
    @abstractmethod
    async def create_package(self, package_data: PackageData) -> PackageData:
        pass
    
    @abstractmethod
    async def get_packages_by_user_session(self) -> PackageData:
        pass

    @abstractmethod
    async def get_package_by_id(self) -> PackageData:
        pass


    @abstractmethod
    async def get_package_delivery_cost_none(self) -> PackageData:
        pass

    @abstractmethod
    async def update_bulk_delivery_cost_by_package(self):
        pass


class PackageDAL():
    data_class = PackageData
    db_model = Package
    async def create_package(self, package_data: PackageData
    ) -> PackageData:
        async with get_db_session() as db_session:
            async with db_session.begin():
                new_package = Package(
                    title=package_data.title,
                    package_cost=package_data.package_cost,
                    weight=package_data.weight,
                    type_package_id=package_data.type_package_id,
                    user_id=package_data.user_id,
                )
                db_session.add(new_package)
                await db_session.flush()
                await db_session.refresh(new_package, ['type_package'])
                await db_session.commit()

        return PackageData.from_orm(new_package)
    

    async def get_packages_by_user_session(
            self, 
            user: UserSessionData,
            filters: FilterPackageData,
            pagination: PaginationPackageData
        ) -> Optional[list[PackageData]]:
        async with get_db_session() as db_session:
            stmt = select(Package).where(Package.user_id == user.id)

            if filters.delivery_cost_null:
                stmt = stmt.where(Package.delivery_cost.isnot(None))

            if filters.type_name:
                stmt = stmt.where(Package.type_package.has(TypePackage.name == filters.type_name))

            stmt = stmt.limit(pagination.size).offset((pagination.page - 1) * pagination.size)

            result = await db_session.execute(stmt)

            packages = result.scalars().unique()
        if packages:
            return [PackageData.from_orm(package) for package in packages]
        return None
    

    async def get_package_by_id(
            self,
            package_id: str,
            user_session: UserSession
    ) -> Optional[PackageData]:
        async with get_db_session() as db_session:
            async with db_session.begin():
                query = select(Package)\
                    .where(Package.user_id == user_session.id)\
                    .where(Package.id == package_id)
                result = await db_session.execute(query)
                package = result.scalars().first()
        if package:
            return PackageData.from_orm(package)
        return None
    

    async def get_package_delivery_cost_none(self) -> Optional[list[PackageData]]:
        async with get_db_session() as db_session:
            async with db_session.begin():
                query = select(Package)\
                    .filter(Package.delivery_cost.is_(None))
                result = await db_session.execute(query)
                packages = result.scalars().unique()
        if packages:
            return list(PackageData.from_orm(package) for package in packages)
        return None
    

    async def update_bulk_delivery_cost(self, data: list[PackageData]):
        # Словарь должен содержать ключи package_id и delivery_cost
        async with get_db_session() as db_session:
            async with db_session.begin():
                when_case = []
                for package in data:
                    if package.id and package.delivery_cost is not None:
                        when_case.append((Package.id == package.id, package.delivery_cost))
                if not when_case:
                    return

                delivery_cost_case = case(*when_case, else_=Package.delivery_cost)
                stmt = update(Package).values(delivery_cost=delivery_cost_case)
                await db_session.execute(stmt)

        
class TypePackageDAL():
    async def create_type_package(
            self,
            type_package_data:TypePackageData
    ) -> TypePackageData:
        async with get_db_session() as db_session:
            async with db_session.begin():
                new_type_package = TypePackage(name=type_package_data.name)
                db_session.add(new_type_package)
                await db_session.commit()
    
        return TypePackageData.from_orm(new_type_package)
    
    async def get_all_type_package(self) -> Optional[list[TypePackageData]]:
        async with get_db_session() as db_session:
            result = await db_session.execute(select(TypePackage))
            types_package = list(result.scalars().unique())
        if types_package:
            return [TypePackageData.from_orm(type_package) for type_package in types_package]
        return None

    async def get_type_package_by_name(
            self,
            name: str
    ) -> Optional[TypePackageData]:
        async with get_db_session() as db_session:
            query = select(TypePackage).where(TypePackage.name == name)
            result = await db_session.execute(query)
            type_package = result.scalars().first()
        if type_package:
            return TypePackageData.from_orm(type_package)
        return None
    
    
class UserSessionDAL():
    async def create_session(
            self,
    ) -> UserSessionData:
        async with get_db_session() as db_session:
            async with db_session.begin():
                id_session = uuid4()
                new_user = UserSession(id_session=id_session)
                db_session.add(new_user)
                await db_session.commit()
        return UserSessionData.from_orm(new_user)
    
    async def get_session_by_session(self, session: str) -> Optional[UserSessionData]:
        async with get_db_session() as db_session:
            query = select(UserSession).where(UserSession.id_session == session)
            result = await db_session.execute(query)
            user_session = result.scalars().first()
        if user_session:
            return UserSessionData.from_orm(user_session)
        return None
    
    async def get_session_by_id(self, session: str) -> Optional[UserSessionData]:
        async with get_db_session() as db_session:
            query = select(UserSession).where(UserSession.id == session)
            result = await db_session.execute(query)
            user_session = result.scalars().first()
        if user_session:
            return UserSessionData.from_orm(user_session)
        return None
    
    async def get_or_create_user(self, session_id: UUID) -> tuple[UserSessionData, bool]:
        "Если пользователя не существует, возвращает True"
        async with get_db_session() as db_session:
            async with db_session.begin():
                user = await self.__get_user_by_session(db_session, session_id)

                
                if user:
                    return (UserSessionData.from_orm(user), False)
                
                user = await self.__create_user(db_session)
                return (UserSessionData.from_orm(user), True)
    
    async def __create_user(self, db_session) -> UserSession:
        id_session = uuid4()
        new_user = UserSession(id_session=id_session)
        db_session.add(new_user)
        await db_session.flush()
        return new_user
    
    async def __get_user_by_session(self, db_session, user_session) -> UserSession:
        query = select(UserSession).where(UserSession.id_session == user_session)
        result = await db_session.execute(query)
        return result.scalars().first()

