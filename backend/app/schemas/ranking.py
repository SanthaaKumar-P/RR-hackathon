from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class BatterRankingItem(BaseModel):
    match_format: str
    striker_id: int
    striker_name: str
    final_rank: Optional[int] = None
    final_score: Optional[float] = None
    eligible: bool = True
    top10_scenario_count: Optional[int] = None
    
    # Raw Counting Metrics
    pressure_runs: Optional[float] = None
    pressure_balls: Optional[float] = None
    pressure_fours: Optional[float] = None
    pressure_sixes: Optional[float] = None
    pressure_deliveries: Optional[float] = None
    pressure_dot_balls: Optional[float] = None
    pressure_matches: Optional[int] = None
    pressure_dismissals: Optional[float] = None
    
    # Analytical Rates
    pressure_strike_rate: Optional[float] = None
    pressure_dot_percentage: Optional[float] = None
    runs_per_match: Optional[float] = None
    runs_per_dismissal: Optional[float] = None
    consistency: Optional[float] = None
    
    # Consistency Sub-metrics
    matches_10_plus: Optional[float] = None
    matches_20_plus: Optional[float] = None
    matches_10_plus_pct: Optional[float] = None
    matches_20_plus_pct: Optional[float] = None
    
    # Normalized Percentile Component Scores (0-100)
    score_pressure_strike_rate: Optional[float] = None
    score_runs_per_match: Optional[float] = None
    score_runs_per_dismissal: Optional[float] = None
    score_pressure_dot_percentage: Optional[float] = None
    score_consistency: Optional[float] = None
    
    # Scenario Scores
    score_Baseline: Optional[float] = None
    score_Volume_Focused: Optional[float] = None
    score_Efficiency_Focused: Optional[float] = None


class BowlerRankingItem(BaseModel):
    match_format: str
    bowler_id: int
    bowler_name: str
    final_rank: Optional[int] = None
    final_score: Optional[float] = None
    eligible: bool = True
    top10_scenario_count: Optional[int] = None
    
    # Raw Counting Metrics
    pressure_runs_conceded: Optional[float] = None
    pressure_runs_conceded_scenario_b: Optional[float] = None
    pressure_legal_balls: Optional[float] = None
    pressure_wickets: Optional[float] = None
    pressure_dot_balls: Optional[float] = None
    pressure_deliveries: Optional[float] = None
    pressure_matches: Optional[int] = None
    pressure_overs: Optional[float] = None
    
    # Analytical Rates
    pressure_economy: Optional[float] = None
    pressure_economy_scenario_b: Optional[float] = None
    pressure_dot_percentage: Optional[float] = None
    wickets_per_100: Optional[float] = None
    wickets_per_match: Optional[float] = None
    consistency: Optional[float] = None
    
    # Consistency Sub-metrics
    matches_1_plus: Optional[float] = None
    matches_2_plus: Optional[float] = None
    matches_1_plus_pct: Optional[float] = None
    matches_2_plus_pct: Optional[float] = None
    
    # Normalized Percentile Component Scores (0-100)
    score_wickets_per_100: Optional[float] = None
    score_pressure_economy: Optional[float] = None
    score_pressure_dot_percentage: Optional[float] = None
    score_consistency: Optional[float] = None
    score_wickets_per_match: Optional[float] = None
    
    # Scenario Scores
    score_Baseline: Optional[float] = None
    score_Wicket_Impact: Optional[float] = None
    score_Control_Focused: Optional[float] = None


class BatterListResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    format: Optional[str] = None
    items: List[BatterRankingItem]


class BowlerListResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    format: Optional[str] = None
    items: List[BowlerRankingItem]


class Top10BatterResponse(BaseModel):
    format: str
    count: int
    items: List[BatterRankingItem]


class Top10BowlerResponse(BaseModel):
    format: str
    count: int
    items: List[BowlerRankingItem]
