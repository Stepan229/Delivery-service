import logging
import uuid


from db.dals import PackageDAL, UserSessionDAL, TypePackageDAL
from api.schemas import CreatePackageSchema, CreateTypePackageSchema
from api.schemas import ShowPackageSchema, ShowTypePackageSchema
from h11 import Response
from sqlalchemy import true
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import TypePackage, Package, UserSession
from asyncpg import exceptions
from fastapi import HTTPException, status

from sqlalchemy.exc import IntegrityError

from fastapi import Depends, Request, Response

from db.session import get_session_db

logger = logging.getLogger(__name__)

async def _create_new_package(body: CreatePackageSchema, 
                              db_session: AsyncSession,
                              user_session: UserSession) -> Package:
    try:
    
        type_package = await _get_type_package_by_name(body.type_package, db_session)
    except HTTPException:
        raise
    
    try:
        async with db_session.begin():
            package_dal = PackageDAL(db_session)

            package = await package_dal.create_package(
                title=body.title,
                package_cost=body.cost,
                weight=body.weight,
                type_package_id=type_package.id,
                type_package=type_package,
                user_id=user_session.id,
                user=user_session
            )
            # await db_session.refresh(package, ['type_package'])
    except Exception as e:
        logger.error(f"Ошибка при создании посылки: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't create a parcel"
        )
    return package

async def _get_type_package_by_name(name_type_package: str, db_session: AsyncSession) -> TypePackage:
    async with db_session.begin():
        type_package_dal = TypePackageDAL(db_session)
        type_package = await type_package_dal.get_type_package_by_name(name_type_package)
    
    if not type_package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Type package: {name_type_package} not found"
        )
    return type_package


async def _create_new_type_package(name_type_package: str, db_session: AsyncSession) -> TypePackage:
    try:
        async with db_session.begin():
            type_package_dal = TypePackageDAL(db_session)
            type_package = await type_package_dal.create_type_package(
                name=name_type_package
            )
    except IntegrityError as e:
        logger.error(f"Ошибка при создании типа посылки: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"This type of parcel already exists"
        )
    return type_package

def create_new_session_user(response: Response) -> uuid.UUID:
    session_id = uuid.uuid4()
    response.set_cookie(key="session_id", 
                        value=str(session_id),
                        httponly=True,
                        samesite="lax")
    return session_id

def get_session_user(request: Request, response: Response) -> tuple[str, bool]:
    "Возвращает идентификатор сессии пользователя и флаг существования сессии"
    session_id = request.headers.get("X-Session-ID")

    if not session_id:
        session_id = request.cookies.get("session_id")

    if not session_id:
        session_id = create_new_session_user(response)
        return str(session_id), False
    return str(session_id), True

async def get_user(request: Request, 
             response: Response, 
             db_session: AsyncSession = Depends(get_session_db),
             result_get_session: tuple[str, bool] = Depends(get_session_user)) -> UserSession:
    session_id, session_exist = result_get_session
    async with db_session.begin():
        user_session_dal = UserSessionDAL(db_session)

        if session_exist:
            user_session = await user_session_dal.get_session_by_session(session_id)
            if not user_session:
                user_session = create_new_session_user(response)
                user_session = await user_session_dal.create_session(session_id)
                # raise HTTPException(
                # status_code=status.HTTP_404_NOT_FOUND,
                # detail=f"Session {session_id} not found"
                # )
        
        if not session_exist:
            user_session = await user_session_dal.create_session(session_id)
    return user_session

async def get_packages_by_user_session(db_session: AsyncSession,
                                       user_session: UserSession) -> list[Package]:
    user_session_dal = PackageDAL(db_session)
    packages = await user_session_dal.get_packages_by_user_session(user_session)
    if not packages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"You don't have any packages available"
        )
    return packages
    
async def get_all_type_packages(db_session: AsyncSession) -> list[TypePackage]:
    type_dal = TypePackageDAL(db_session)
    types = await type_dal.get_all_type_package()
    if not types:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There are no parcel types right now"
        )
    return types

async def _get_package_by_id(db_session: AsyncSession, 
                            id_package: str,
                            user_session: UserSession) -> Package:
    package_dal = PackageDAL(db_session)
    package = await package_dal.get_package_by_id(id_package, user_session)
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"This package does not exist"
        )
    return package

    


        
        
    





