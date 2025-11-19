from email.mime import base
from turtle import title
from unicodedata import numeric
import uuid
from enum import Enum, unique

from annotated_types import T
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

from decimal import Decimal


# declarative base class
class Base(DeclarativeBase):
    pass


class Package(Base):

    __tablename__ = "packages"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    package_cost: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(5, 3), nullable=False)
    delivery_cost: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=True)

    type_package_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("type_packages.id"), nullable=False
    )
    type_package: Mapped["TypePackage"] = relationship(
        "TypePackage",
        back_populates="packages",
        lazy="joined"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_session.id"), nullable=False)
    user: Mapped["UserSession"] = relationship("UserSession", 
                                               back_populates="packages",
                                               lazy="joined")
# Сделать имя уникальным
class TypePackage(Base):
    __tablename__ = "type_packages"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    packages: Mapped[list["Package"]] = relationship(
        "Package",
        back_populates="type_package",
        lazy="joined",
    )

class UserSession(Base):
    __tablename__ = "user_session"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_session: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    packages: Mapped[list["Package"]] = relationship(
        "Package",
        back_populates="user",
        lazy="joined",
    )

    
    

