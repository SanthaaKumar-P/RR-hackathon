from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class MatchItem(BaseModel):
    match_id: int
    comp_id: Optional[int] = None
    comp_name: Optional[str] = None
    match_format: Optional[str] = None
    season: Optional[str] = None
    match_date: Optional[str] = None
    stage: Optional[str] = None
    venue_id: Optional[int] = None
    venue_country: Optional[str] = None
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    toss_win_team_id: Optional[int] = None
    toss_opted: Optional[str] = None
    result: Optional[str] = None
    win_team_id: Optional[int] = None
    man_of_the_match: Optional[str] = None
    has_ball_data: Optional[bool] = None

class InningsSummaryItem(BaseModel):
    match_id: int
    innings: int
    total_runs: int
    total_wickets: int
    legal_balls: int
    ambiguous_deliveries: int
    maximum_legal_balls: int
    maximum_overs: float

class PressureTimelineDelivery(BaseModel):
    innings: int
    overid: int
    over_ball_num: int
    innings_ball_num: int
    striker_name: str
    bowler_name: str
    runs: int
    total_runs: int
    is_wicket: bool
    current_score: int
    wickets_lost: int
    pressure_category: str
    innings_phase: str
    required_run_rate: Optional[float] = None
    current_run_rate: Optional[float] = None

class OverSummary(BaseModel):
    innings: int
    overid: int
    runs_in_over: int
    wickets_in_over: int
    end_score: int
    end_wickets: int
    predominant_pressure: str
    innings_phase: str

class MatchPressureTimelineResponse(BaseModel):
    match_id: int
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    match_format: Optional[str] = None
    total_pressure_balls: int
    overs: List[OverSummary]
    deliveries: List[PressureTimelineDelivery]
