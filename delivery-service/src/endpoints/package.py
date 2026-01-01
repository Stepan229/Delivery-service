import logging
from fastapi import APIRouter, Path
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from schemas.schemas import CreatePackageSchema, CreateTypePackageSchema
from schemas.schemas import ShowPackageSchema, ShowTypePackageSchema


from core.session import get_session_db

from models import UserSession

from services.package_actions import create_new_package, create_new_type_package, get_packages_by_user_session, get_all_type_packages, get_package_by_id
from services.user_actions import get_user
from domain.dto import PackageData, TypePackageData, UserSessionData, FilterPackageData, PaginationPackageData
from schemas.filters import PaginationParams, PackageFilterParams

from services.utils import dataclass_to_pydantic
logger = logging.getLogger(__name__)

package_router = APIRouter()

@package_router.post("/", response_model=ShowPackageSchema)
async def create_package(body: CreatePackageSchema,
                            db_session: AsyncSession = Depends(get_session_db),
                            user_session: UserSession = Depends(get_user),
                            ) -> ShowPackageSchema:
    try:
        package_data = PackageData(
            user_id=user_session.id,
            title=body.title,
            package_cost=body.cost,
            weight=body.weight
        )
        package = await create_new_package(package_data, body.type_package)
    except Exception:
        raise
    logger.error(f"ОШИБКА {package}")
    return dataclass_to_pydantic(package, ShowPackageSchema)


@package_router.get("/", response_model=list[ShowPackageSchema])
async def get_packages(
    pagination: PaginationParams = Depends(),
    filters: PackageFilterParams = Depends(),
    user_session: UserSessionData = Depends(get_user),
    ):
    packages = await get_packages_by_user_session(user_session,
                                                   FilterPackageData(**filters.model_dump()),
                                                   PaginationPackageData(**pagination.model_dump()))
    return [ShowPackageSchema.model_validate(package) for package in packages]


@package_router.post("/type/", response_model=ShowTypePackageSchema)
async def create_type_package(body: CreateTypePackageSchema) -> ShowTypePackageSchema:
    try:
        type_package = TypePackageData(name=body.name)
        new_type_package = await create_new_type_package(type_package)
    except Exception:
        raise
    return dataclass_to_pydantic(new_type_package, ShowTypePackageSchema)

@package_router.get("/type/", response_model=list[ShowTypePackageSchema])
async def get_type_package() -> list[ShowTypePackageSchema]:
    types = await get_all_type_packages()
    return [dataclass_to_pydantic(type, ShowTypePackageSchema) for type in types]


@package_router.get("/{package_id}")
async def get_package(
    package_id: str = Path(..., description="ID посылки"),
    user_session: UserSession = Depends(get_user),
) -> ShowPackageSchema:
    package = await get_package_by_id(package_id, user_session)
    return ShowPackageSchema.model_validate(package)


