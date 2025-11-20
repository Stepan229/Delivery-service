import logging
from fastapi import APIRouter, Path
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.filters import PackageFilter
from api.schemas import CreatePackageSchema, CreateTypePackageSchema
from api.schemas import ShowPackageSchema, ShowTypePackageSchema

from db.session import get_session_db

from db.models import UserSession

from api.actions import _create_new_package, _create_new_type_package, get_user, get_packages_by_user_session, get_all_type_packages, _get_package_by_id

from fastapi_filter import FilterDepends


logger = logging.getLogger(__name__)

package_router = APIRouter()

@package_router.post("/", response_model=ShowPackageSchema)
async def create_package(body: CreatePackageSchema,
                            db_session: AsyncSession = Depends(get_session_db),
                            user_session: UserSession = Depends(get_user),
                            ) -> ShowPackageSchema:
    try:  
        package = await _create_new_package(body=body,
                                            db_session=db_session, 
                                            user_session=user_session)
    except Exception:
        raise
    return ShowPackageSchema.model_validate(package)


@package_router.post("/type/", response_model=ShowTypePackageSchema)
async def create_type_package(
        body: CreateTypePackageSchema,
        db_session: AsyncSession = Depends(get_session_db)
) -> ShowTypePackageSchema:
    
    try:
        type_package = await _create_new_type_package(body.name, db_session)
    except Exception:
        raise

    return ShowTypePackageSchema.model_validate(type_package)

@package_router.get("/", response_model=list[ShowPackageSchema])
async def get_packages(
    package_filter: PackageFilter = FilterDepends(PackageFilter),
    db_session: AsyncSession = Depends(get_session_db),
    user_session: UserSession = Depends(get_user),
    ):
    packages = await get_packages_by_user_session(db_session, user_session, package_filter)
    return [ShowPackageSchema.model_validate(package) for package in packages]

@package_router.get("/type/", response_model=list[ShowTypePackageSchema])
async def get_type_package(db_session: AsyncSession = Depends(get_session_db)) -> list[ShowTypePackageSchema]:
    types = await get_all_type_packages(db_session)
    return [ShowTypePackageSchema.model_validate(type) for type in types]

@package_router.get("/{package_id}")
async def get_package_by_id(
    package_id: str = Path(..., description="ID посылки"),
    db_session: AsyncSession = Depends(get_session_db),
    user_session: UserSession = Depends(get_user),
) -> ShowPackageSchema:
    package = await _get_package_by_id(db_session, package_id, user_session)
    return ShowPackageSchema.model_validate(package)
