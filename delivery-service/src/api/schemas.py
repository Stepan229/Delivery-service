from turtle import title
from enum import Enum
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict
from pydantic import constr
from pydantic import EmailStr
from pydantic import validator

import uuid

class TunedModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class ShowTypePackageSchema(TunedModel):
    id: uuid.UUID
    name: str

class CreateTypePackageSchema(BaseModel):
    name: str

class ShowPackageSchema(TunedModel):
    id: uuid.UUID
    title: str
    cost: float
    weight: float
    type_package: ShowTypePackageSchema

class CreatePackageSchema(BaseModel):
    title: constr(min_length=1, max_length=255)
    cost: float
    weight: float
    type_package: str





