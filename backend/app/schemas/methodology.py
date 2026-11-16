from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class SampleThresholds(BaseModel):
    min_balls: int
    min_matches: int
    denominator_rule: str

class MethodologyResponse(BaseModel):
    title: str
    season: str
    round: str
    competition_segmentation: str
    pressure_definition: str
    eligibility_thresholds: Dict[str, SampleThresholds]
    batter_baseline_weights: Dict[str, float]
    bowler_baseline_weights: Dict[str, float]
    scoring_directions: Dict[str, Dict[str, str]]
    consistency_formulas: Dict[str, str]
    wicket_credit_rules: Dict[str, List[str]]
    extras_accounting_scenarios: Dict[str, str]
    alternative_weight_scenarios: Dict[str, Dict[str, Dict[str, float]]]
    project_assumptions_and_limitations: List[str]
