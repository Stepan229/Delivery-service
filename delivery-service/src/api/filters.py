from typing import Annotated, Optional

from db.models import Package, TypePackage

from decimal import Decimal

from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_filter import with_prefix
from fastapi_filter import FilterDepends


from pydantic import Field

class TypePackageFilter(Filter):
    name__neq: Optional[str] = None

    class Constants(Filter.Constants):
        model = TypePackage
        
    class Config:
        allow_population_by_field_name = True

class PackageFilter(Filter):
    delivery_cost__isnull: Optional[bool] = None
    # type: Optional[TypePackageFilter] = FilterDepends(with_prefix("type", TypePackageFilter))
    type: Optional[TypePackageFilter] = FilterDepends(TypePackageFilter)
    
    class Constants(Filter.Constants):
        model = Package

    class Config:
        allow_population_by_field_name = True

    # def filter(self, query):
    #     query = super().filter(query)
        
    #     if self.type:
    #         query = self.type.filter(query)
        
    #     return query
