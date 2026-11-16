from fastapi import APIRouter, Query
from app.schemas.scenario import BatterScenarioResponse, BowlerScenarioResponse
from app.services.scenario_service import scenario_service

router = APIRouter(prefix="/scenarios", tags=["Scenario Analysis"])

@router.get("")
@router.get("/")
def get_scenarios_unified(
    format: str = Query("T20", description="Competition format: T20 or T20I"),
    discipline: str = Query("batter", description="Discipline: batter or bowler"),
    scenario: str = Query("baseline", description="Scenario name")
):
    """
    Unified scenarios endpoint supporting query parameters discipline & scenario.
    """
    if discipline.lower().startswith("bowl"):
        return scenario_service.get_bowler_scenarios(format_str=format)
    return scenario_service.get_batter_scenarios(format_str=format)

@router.get("/batters", response_model=BatterScenarioResponse)
def get_batter_scenarios(
    format: str = Query("T20", description="Competition format: T20 or T20I")
):
    """
    Returns verified scenario scores and Top 10 rankings across:
    - Baseline (25% SR, 20% RPM, 15% RPD, 15% Dot%, 25% Consistency)
    - Volume Focused (20% SR, 30% RPM, 10% RPD, 10% Dot%, 30% Consistency)
    - Efficiency Focused (30% SR, 15% RPM, 20% RPD, 20% Dot%, 15% Consistency)
    Along with baseline overlap metrics from ranking_sensitivity_analysis.csv.
    """
    return scenario_service.get_batter_scenarios(format_str=format)

@router.get("/bowlers", response_model=BowlerScenarioResponse)
def get_bowler_scenarios(
    format: str = Query("T20", description="Competition format: T20 or T20I")
):
    """
    Returns verified scenario scores and Top 10 rankings across:
    - Baseline (25% W/100, 20% Econ, 15% Dot%, 20% Consistency, 20% WPM)
    - Wicket Impact (35% W/100, 15% Econ, 10% Dot%, 15% Consistency, 25% WPM)
    - Control Focused (20% W/100, 25% Econ, 20% Dot%, 20% Consistency, 15% WPM)
    Includes baseline overlap metrics and Scenario A vs Scenario B extras accounting sensitivity data.
    """
    return scenario_service.get_bowler_scenarios(format_str=format)
