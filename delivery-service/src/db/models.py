from turtle import title
from unicodedata import numeric
import uuid
from enum import Enum

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from sqlalchemy import Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship




# declarative base class
class Base(DeclarativeBase):
    pass


class Package(Base):

    __tablename__ = "packages"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    cost: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    weight: Mapped[Numeric] = mapped_column(Numeric(10, 3), nullable=False)

    type_package_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("type_packages.id"), nullable=False
    )
    type_package: Mapped["TypePackage"] = relationship(
        "TypePackage",
        back_populates="packages",
        lazy="joined"
    )
    user_package: Mapped["UserPackageAssociation"] = relationship(
        "UserPackageAssociation",
        back_populates="package",
        lazy="select",
        uselist=False
    )

class TypePackage(Base):
    __tablename__ = "type_packages"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    packages: Mapped[list["Package"]] = relationship(
        "Package",
        back_populates="type_package",
        lazy="select"
    )

class UserPackageAssociation(Base):
    __tablename__ = "user_package_associations"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    package_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("packages.id"),
        nullable=False
    )
    package: Mapped["Package"] = relationship("Package", back_populates="user_package")

class ShippingCost(Base):
    __tablename__ = "shipping_costs"

    package_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("packages.id"),
        primary_key=True
    )
    cost: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=False)