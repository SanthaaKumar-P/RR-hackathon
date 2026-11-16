from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from .ranking import BatterRankingItem, BowlerRankingItem

class ScenarioDefinition(BaseModel):
    name: str
    description: str
    weights: Dict[str, float]
    top10_overlap_with_baseline: int

class BatterScenarioResponse(BaseModel):
    format: str
    baseline_weights: Dict[str, float]
    scenarios: List[ScenarioDefinition]
    scenario_rankings: Dict[str, List[BatterRankingItem]]

class BowlerAccountingSensitivityRow(BaseModel):
    bowler_id: int
    bowler_name: str
    match_format: str
    pressure_legal_balls: int
    pressure_wickets: int
    pressure_economy_scenario_a: float
    final_rank_scenario_a: int
    pressure_economy_scenario_b: float
    final_rank_scenario_b: int
    rank_change_b_minus_a: int
    top10_scenario_a: bool
    top10_scenario_b: bool
    top10_status_changed: bool

class BowlerScenarioResponse(BaseModel):
    format: str
    baseline_weights: Dict[str, float]
    scenarios: List[ScenarioDefinition]
    scenario_rankings: Dict[str, List[BowlerRankingItem]]
    accounting_sensitivity_summary: Dict[str, Any]
    accounting_sensitivity_items: List[BowlerAccountingSensitivityRow]
