from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from .ranking import BatterRankingItem, BowlerRankingItem

class MetricComparisonRow(BaseModel):
    metric_key: str
    metric_label: str
    higher_is_better: bool
    values: Dict[str, Optional[float]]
    percentiles: Dict[str, Optional[float]]
    leader_player_id: Optional[int] = None

class PlayerComparisonResponse(BaseModel):
    player_type: str
    format: str
    player_ids: List[int]
    players: List[Dict[str, Any]]
    metric_matrix: List[MetricComparisonRow]
