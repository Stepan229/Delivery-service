import logging
from typing import Optional
from uuid import UUID, uuid4

from repositories.dals import PackageDAL, TypePackageDAL

from models import UserSession

from fastapi import HTTPException, status

from sqlalchemy.exc import IntegrityError



from domain.dto import PackageData, TypePackageData, UserSessionData
from domain.dto import FilterPackageData, PaginationPackageData

logger = logging.getLogger(__name__)

async def create_new_package(package_data: PackageData, name_type_package: str) -> PackageData:
    try:
        type_package = await get_type_package_by_name(name_type_package)
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

async def get_type_package_by_name(name_type_package: str) -> TypePackageData:
   
    type_package_dal = TypePackageDAL()
    type_package = await type_package_dal.get_type_package_by_name(name_type_package)
    
    if not type_package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Type package: {name_type_package} not found"
        )
    return type_package


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
    


async def get_package_by_id(id_package: str, user_session: UserSession) -> PackageData:
    package_dal = PackageDAL()
    package = await package_dal.get_package_by_id(UUID(id_package), user_session)
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

        
async def get_packages_without_cost() -> Optional[list[PackageData]]:
    package_dal = PackageDAL()
    packages = await package_dal.get_package_delivery_cost_none()
    return packages
    
async def update_delivery_cost_packages(packages: list[PackageData]):
    package_dal = PackageDAL()
    await package_dal.update_bulk_delivery_cost(packages)

    





