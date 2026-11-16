from typing import List, Optional
from fastapi import APIRouter, Query
from app.schemas.common import PaginatedResponse
from app.schemas.pressure import PressureCategoryItem, PressurePhaseItem, PressureSummaryResponse
from app.services.pressure_service import pressure_service

router = APIRouter(prefix="/pressure", tags=["Pressure Analytics"])

@router.get("")
@router.get("/")
def get_pressure_combined(
    format: Optional[str] = Query(None, description="Filter by format: T20 or T20I (optional)")
):
    """
    Returns unified pressure intelligence including categories, phases, format breakdown, and summary.
    """
    summary = pressure_service.get_summary(format_str=format)
    categories = pressure_service.get_categories()
    phases = pressure_service.get_phases()

    from app.services.data_loader import data_loader
    matches = data_loader.get_target_matches()
    pressure = data_loader.get_pressure_classified()
    t20_matches = set(matches[matches["match_format"] == "T20"]["match_id"])
    t20i_matches = set(matches[matches["match_format"] == "T20I"]["match_id"])
    t20_del = int(pressure["match_id"].isin(t20_matches).sum())
    t20i_del = int(pressure["match_id"].isin(t20i_matches).sum())

    return {
        "categories": categories,
        "phases": phases,
        "by_format": [
            {"format": "T20 (IPL)", "deliveries": t20_del},
            {"format": "T20I", "deliveries": t20i_del},
        ],
        "summary": summary,
    }

@router.get("/summary", response_model=PressureSummaryResponse)
def get_pressure_summary(
    format: Optional[str] = Query(None, description="Filter by format: T20 or T20I (optional)")
):
    """
    Returns high-level aggregate comparison between baseline cricket deliveries and pressure deliveries.
    """
    return pressure_service.get_summary(format_str=format)

@router.get("/categories", response_model=List[PressureCategoryItem])
def get_pressure_categories():
    """
    Returns delivery volume, percentage, scoring rate, boundary rate, and dot ball rate across all pressure tiers:
    Extreme, High, Moderate, Low, and Not Applicable.
    """
    return pressure_service.get_categories()

@router.get("/phases", response_model=List[PressurePhaseItem])
def get_pressure_phases():
    """
    Returns phase-wise analysis across Powerplay, Middle, and Death overs,
    showing pressure delivery density, scoring dynamics, and wicket distribution.
    """
    return pressure_service.get_phases()

@router.get("/batter-performance")
def get_batter_pressure_performance(
    search: Optional[str] = Query(None, description="Search by player name or ID"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Returns player-level overall vs pressure performance for batters.
    """
    return pressure_service.get_batter_performance(search=search, page=page, limit=limit)

@router.get("/bowler-performance")
def get_bowler_pressure_performance(
    search: Optional[str] = Query(None, description="Search by bowler name or ID"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Returns player-level overall vs pressure performance for bowlers.
    """
    return pressure_service.get_bowler_performance(search=search, page=page, limit=limit)
