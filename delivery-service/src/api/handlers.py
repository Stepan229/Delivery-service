from logging import getLogger
from uuid import UUID
import logging
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import CreatePackageSchema, CreateTypePackageSchema
from api.schemas import ShowPackageSchema, ShowTypePackageSchema
from db.dals import PackageDAL
from db.dals import TypePackageDAL
from db.session import get_session




logger = logging.getLogger(__name__)

package_router = APIRouter()

@package_router.post("/", response_model=ShowPackageSchema)
async def create_package(body: CreatePackageSchema,
                            db_session: AsyncSession = Depends(get_session)) -> ShowPackageSchema:
    async with db_session.begin():
        type_package_dal = TypePackageDAL(db_session)
        type_package = await type_package_dal.get_type_package_by_name(body.type_package)
        package_dal = PackageDAL(db_session)
        package = await package_dal.create_package(
            title=body.title,
            cost=body.cost,
            weight=body.weight,
            type_package_id=type_package.id
            
        )
        logger.info(f"Created package with ID: {package.type_package}")
    return ShowPackageSchema.from_orm(package)


@package_router.post("/type/", response_model=ShowTypePackageSchema)
async def create_type_package(
        body: CreateTypePackageSchema,
        db_session: AsyncSession = Depends(get_session)
) -> ShowTypePackageSchema:
    print(body)
    # logger.info(f"Creating type package with name: {body.name}")
    # logger.warning(f"Creating type package with name: {body.name}")
    async with db_session.begin():
        type_package_dal = TypePackageDAL(db_session)
        type_package = await type_package_dal.create_type_package(
            name=body.name
        )

    return ShowTypePackageSchema.from_orm(type_package)