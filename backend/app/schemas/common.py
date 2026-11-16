from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "2.0.0"
    project: str = "SupeRR Selector – Cricket Intelligence Platform"
    datasets_loaded: bool = True
    total_matches: int
    total_pressure_deliveries: int

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    limit: int
    total_pages: int
    items: List[T]
