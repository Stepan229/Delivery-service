from turtle import title
from enum import Enum
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field
from pydantic import constr
from pydantic import EmailStr
from pydantic import validator
from decimal import Decimal
import uuid


class TunedModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class ShowTypePackageSchema(TunedModel):
    id: uuid.UUID
    name: str = Field(..., description="Тип посылки")

class ShowTypePackageNameSchema(TunedModel):
    name: str

class CreateTypePackageSchema(BaseModel):
    name: str

class ShowPackageSchema(TunedModel):
    id: uuid.UUID
    title: str
    cost: Decimal
    weight: Decimal
    type_package: ShowTypePackageNameSchema

class CreatePackageSchema(BaseModel):
    title: str = Field(... ,min_length=1 ,max_length=255, description="Имя посылки")
    cost: Decimal = Field(max_digits=5, decimal_places=2, gt=0, description="Стоимость содержимого")
    weight: Decimal = Field(max_digits=5, decimal_places=3, gt=0, description="Вес посылки")
    type_package: str = Field(..., description="Тип посылки")

    





