from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.player import BowlerDetailResponse
from app.schemas.ranking import BowlerListResponse, Top10BowlerResponse
from app.services.bowler_service import bowler_service

router = APIRouter(prefix="/bowlers", tags=["Bowlers"])

@router.get("", response_model=BowlerListResponse)
def get_bowlers(
    format: Optional[str] = Query(None, description="Competition format: T20 or T20I"),
    search: Optional[str] = Query(None, description="Search by bowler name or bowler ID"),
    eligible: Optional[bool] = Query(None, description="Filter by sample eligibility (>=60 legal balls & >=10 verified matches)"),
    sort_by: str = Query("final_rank", description="Field to sort by (final_rank, final_score, wickets_per_100, pressure_economy, etc.)"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort direction: asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=500, description="Items per page")
):
    """
    Search, filter, sort and paginate through bowler pressure performance rankings.
    Source of truth: final_bowler_rankings.csv.
    """
    return bowler_service.get_bowlers(
        format_str=format,
        search=search,
        eligible=eligible,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit
    )

@router.get("/top10", response_model=Top10BowlerResponse)
def get_top10_bowlers(
    format: str = Query("T20", description="Competition format: T20 or T20I")
):
    """
    Returns the verified baseline Top 10 bowlers for the specified format.
    Matches top10_bowlers_by_format.csv exactly.
    """
    return bowler_service.get_top10(format_str=format)

@router.get("/{player_id}", response_model=BowlerDetailResponse)
def get_bowler_by_id(
    player_id: int,
    format: Optional[str] = Query(None, description="Competition format: T20 or T20I")
):
    """
    Retrieve granular analytical profile, percentile metric scores, alternative scenario scores,
    and accounting sensitivity comparison for a specific bowler.
    """
    return bowler_service.get_bowler_by_id(player_id=player_id, format_str=format)
