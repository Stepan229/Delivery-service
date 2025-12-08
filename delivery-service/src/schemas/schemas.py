from tkinter import N, NO
from token import OP
from turtle import title
from enum import Enum
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field
from pydantic import constr
from pydantic import EmailStr
from typing import Annotated, Optional
from pydantic import BeforeValidator
from decimal import Decimal
import uuid



def validate_delivery_cost(value: Optional[Decimal]) -> Decimal | str:
    if value is None:
        return "Не рассчитано"
    return value

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
    package_cost: Decimal
    weight: Decimal
    type_package: ShowTypePackageNameSchema
    delivery_cost: Annotated[Decimal | str, BeforeValidator(validate_delivery_cost)]

        
class CreatePackageSchema(BaseModel):
    title: str = Field(... ,min_length=1 ,max_length=255, description="Имя посылки")
    cost: Decimal = Field(max_digits=5, decimal_places=2, gt=0, description="Стоимость содержимого")
    weight: Decimal = Field(max_digits=5, decimal_places=3, gt=0, description="Вес посылки")
    type_package: str = Field(..., description="Тип посылки")





        



