from typing import Any, Dict, List
from pydantic import BaseModel, Field

class FormatCount(BaseModel):
    T20: int
    T20I: int

class RankedPlayerCounts(BaseModel):
    total: int
    T20: int
    T20I: int

class TopPlayerCard(BaseModel):
    final_rank: int
    player_id: int
    player_name: str
    match_format: str
    final_score: float
    key_metric_label: str
    key_metric_value: float

class OverviewResponse(BaseModel):
    total_matches: int
    total_selected_deliveries: int
    total_pressure_deliveries: int
    match_counts: FormatCount
    ranked_batters_count: RankedPlayerCounts
    ranked_bowlers_count: RankedPlayerCounts
    pressure_category_distribution: Dict[str, int]
    phase_distribution: Dict[str, int]
    top5_batters: Dict[str, List[Dict[str, Any]]]
    top5_bowlers: Dict[str, List[Dict[str, Any]]]
