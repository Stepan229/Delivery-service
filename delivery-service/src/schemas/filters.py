from typing import Annotated, Optional

from db.models import Package, TypePackage

from decimal import Decimal

from pydantic import Field, BaseModel


class PackageFilterParams(BaseModel):
    delivery_cost_null: Optional[bool] = None
    type_name: Optional[str] = Field(None, min_length=1, max_length=10000)
    
class PaginationParams(BaseModel):
    page: Optional[int] = Field(1, ge=1)
    size: Optional[int] = Field(100, ge=1, le=100)