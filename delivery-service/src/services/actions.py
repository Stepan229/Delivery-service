import logging
from typing import Optional
from uuid import UUID, uuid4


from db.dals import PackageDAL, UserSessionDAL, TypePackageDAL
from schemas.schemas import CreatePackageSchema, CreateTypePackageSchema
from schemas.schemas import ShowPackageSchema, ShowTypePackageSchema



from h11 import Response
from sqlalchemy import true
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import TypePackage, Package, UserSession
from asyncpg import exceptions
from fastapi import HTTPException, status

from sqlalchemy.exc import IntegrityError

from fastapi import Depends, Request, Response

from db.session import get_session_db


from domain.dto import PackageData, TypePackageData, UserSessionData
from domain.dto import FilterPackageData, PaginationPackageData

logger = logging.getLogger(__name__)

async def _create_new_package(package_data: PackageData, name_type_package: str) -> PackageData:
    try:
        type_package = await _get_type_package_by_name(name_type_package)
    except HTTPException:
        raise
    
    package_data.type_package_id = type_package.id

    try:
        package_dal = PackageDAL()
        package = await package_dal.create_package(package_data)
            
    except Exception as e:
        logger.error(f"Ошибка при создании посылки: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't create a parcel"
        )
    return package

async def _get_type_package_by_name(name_type_package: str) -> TypePackageData:
   
    type_package_dal = TypePackageDAL()
    type_package = await type_package_dal.get_type_package_by_name(name_type_package)
    
    if not type_package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Type package: {name_type_package} not found"
        )
    return type_package




async def create_new_session_user(response: Response) -> UserSessionData:


    user_session_dal = UserSessionDAL()
    user = await user_session_dal.create_session()

    
    return user

async def get_or_create_user(session_id: UUID) -> Optional[UUID]:
    "Возвращает идентификатор сессии"

    if not session_id:
        user_session = await create_new_session_user(response)
        return user_session.id_session

async def get_user(request: Request, response: Response) -> UserSessionData:
    session_id = request.headers.get("X-Session-ID")

    if not session_id:
        session_id = request.cookies.get("session_id")

    
    user_session_dal = UserSessionDAL()
    if session_id:
        user, created = await user_session_dal.get_or_create_user(UUID(session_id))
    else:
        user = await user_session_dal.create_session()
        created = True
    if created:
        response.set_cookie(key="session_id", 
                    value=str(user.id_session),
                    httponly=True,
                    samesite="lax")
    return user

async def get_packages_by_user_session(user_session: UserSessionData,
                                       filters: FilterPackageData,
                                       pagination: PaginationPackageData) -> list[PackageData]:
    user_package_dal = PackageDAL()
    packages = await user_package_dal.get_packages_by_user_session(
        user=user_session,
        filters=filters,
        pagination=pagination
    )
    if not packages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"You don't have any packages available"
        )
    return packages
    


async def _get_package_by_id(id_package: str, user_session: UserSession) -> PackageData:
    package_dal = PackageDAL()
    package = await package_dal.get_package_by_id(id_package, user_session)
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"This package does not exist"
        )
    return package

    
async def get_all_type_packages() -> list[TypePackageData]:
    type_dal = TypePackageDAL()
    types = await type_dal.get_all_type_package()
    if not types:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There are no parcel types right now"
        )
    return types

async def create_new_type_package(type_package: TypePackageData) -> TypePackageData:
    try:
        type_package_dal = TypePackageDAL()
        new_type_package = await type_package_dal.create_type_package(type_package)
    except IntegrityError as e:
        logger.error(f"Ошибка при создании типа посылки: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"This type of parcel already exists"
        )
    return new_type_package

        
        
    





