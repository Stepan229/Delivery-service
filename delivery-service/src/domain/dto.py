import datetime
from dataclasses import dataclass
from os import name
# from importlib.resources import Package

from models import Package, TypePackage, UserSession
from typing import Optional
from uuid import UUID
from decimal import Decimal
#Data Transfer Objects

@dataclass
class TypePackageData:
    id: Optional[UUID] = None
    name: Optional[str] = None

    @classmethod
    def from_orm(cls, db_model: TypePackage):
        return cls(
            id=db_model.id,
            name=db_model.name
        )

@dataclass
class UserSessionData:
    id: UUID
    id_session: UUID

    @classmethod
    def from_orm(cls, db_model: UserSession):
        return cls(
            id=db_model.id,
            id_session=db_model.id_session
        )

@dataclass
class PackageData:
    weight: Decimal
    package_cost: Decimal
    id: Optional[UUID] = None
    user_id: Optional[UUID]= None
    type_package_id: Optional[UUID] = None
    type_package: Optional[TypePackageData] = None
    title: Optional[str] = None
    delivery_cost: Optional[Decimal] = None

    @classmethod
    def from_orm(cls, db_model: Package):
        return cls(
            id=db_model.id,
            type_package=TypePackageData().from_orm(db_model.type_package),
            title = db_model.title,
            package_cost = db_model.package_cost,
            weight = db_model.weight,
            delivery_cost = db_model.delivery_cost,
        )

@dataclass
class FilterPackageData:
    delivery_cost_null: Optional[bool]
    type_name: Optional[str]

@dataclass
class PaginationPackageData:
    page: int
    size: int