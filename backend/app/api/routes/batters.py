from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.player import BatterDetailResponse
from app.schemas.ranking import BatterListResponse, Top10BatterResponse
from app.services.batter_service import batter_service

router = APIRouter(prefix="/batters", tags=["Batters"])

@router.get("", response_model=BatterListResponse)
def get_batters(
    format: Optional[str] = Query(None, description="Competition format: T20 or T20I"),
    search: Optional[str] = Query(None, description="Search by player name or player ID"),
    eligible: Optional[bool] = Query(None, description="Filter by sample eligibility (>=100 balls & >=10 matches)"),
    sort_by: str = Query("final_rank", description="Field to sort by (final_rank, final_score, pressure_strike_rate, etc.)"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort direction: asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=500, description="Items per page")
):
    """
    Search, filter, sort and paginate through batter pressure performance rankings.
    Source of truth: final_batter_rankings.csv.
    """
    return batter_service.get_batters(
        format_str=format,
        search=search,
        eligible=eligible,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit
    )

@router.get("/top10", response_model=Top10BatterResponse)
def get_top10_batters(
    format: str = Query("T20", description="Competition format: T20 or T20I")
):
    """
    Returns the verified baseline Top 10 batters for the specified format.
    Matches top10_batters_by_format.csv exactly.
    """
    return batter_service.get_top10(format_str=format)

@router.get("/{player_id}", response_model=BatterDetailResponse)
def get_batter_by_id(
    player_id: int,
    format: Optional[str] = Query(None, description="Competition format: T20 or T20I")
):
    """
    Retrieve granular analytical profile, percentile metric scores, and scenario evaluations for a specific batter.
    """
    return batter_service.get_batter_by_id(player_id=player_id, format_str=format)
