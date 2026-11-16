from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from .ranking import BatterRankingItem, BowlerRankingItem

class BatterDetailResponse(BaseModel):
    player_id: int
    player_name: str
    match_format: str
    ranking: BatterRankingItem
    methodology_weights: Dict[str, float]
    scenarios: Dict[str, Optional[float]]
    raw_stats: Dict[str, Any]

class BowlerDetailResponse(BaseModel):
    player_id: int
    player_name: str
    match_format: str
    ranking: BowlerRankingItem
    methodology_weights: Dict[str, float]
    scenarios: Dict[str, Optional[float]]
    accounting_sensitivity: Optional[Dict[str, Any]] = None
    raw_stats: Dict[str, Any]
