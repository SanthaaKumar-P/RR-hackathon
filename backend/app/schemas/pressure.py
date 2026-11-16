from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class PressureMetricSplit(BaseModel):
    deliveries: int
    runs: int
    wickets: int
    run_rate: float
    boundary_percentage: float
    dot_percentage: float

class PressureSummaryResponse(BaseModel):
    format: Optional[str]
    total_deliveries: int
    pressure_deliveries: int
    pressure_delivery_pct: float
    overall_performance: PressureMetricSplit
    pressure_performance: PressureMetricSplit
    pressure_delta: Dict[str, float]

class PressureCategoryItem(BaseModel):
    category: str
    deliveries: int
    percentage: float
    runs: int
    wickets: int
    run_rate: float
    boundary_percentage: float
    dot_percentage: float
    definition: str

class PressurePhaseItem(BaseModel):
    phase: str
    overs: str
    total_deliveries: int
    pressure_deliveries: int
    pressure_pct: float
    runs: int
    wickets: int
    run_rate: float
    dot_percentage: float

class PlayerPressurePerformanceItem(BaseModel):
    player_id: int
    player_name: str
    match_format: Optional[str] = None
    overall_metric: float
    pressure_metric: float
    metric_label: str
    delta: float
    pressure_sample: int
    sample_eligible: bool
