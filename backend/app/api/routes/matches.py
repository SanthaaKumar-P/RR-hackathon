from typing import List, Optional
from fastapi import APIRouter, Query
from app.schemas.match import InningsSummaryItem, MatchItem, MatchPressureTimelineResponse
from app.services.match_service import match_service

router = APIRouter(prefix="/matches", tags=["Match Insights"])

@router.get("")
def get_matches(
    format: Optional[str] = Query(None, description="Competition format: T20 or T20I"),
    season: Optional[str] = Query(None, description="Season year or identifier"),
    stage: Optional[str] = Query(None, description="Match stage (e.g. League, Final)"),
    team: Optional[str] = Query(None, description="Filter by team name"),
    search: Optional[str] = Query(None, description="General search by team or competition"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("match_date", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """
    Search and paginate through target matches analyzed in the SupeRR Selector project.
    """
    return match_service.get_matches(
        format_str=format,
        season=season,
        stage=stage,
        team=team,
        search=search,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get("/{match_id}")
def get_match_by_id(match_id: int):
    """
    Returns full metadata for a specific match.
    """
    return match_service.get_match_by_id(match_id=match_id)

@router.get("/{match_id}/innings", response_model=List[InningsSummaryItem])
def get_match_innings(match_id: int):
    """
    Returns innings scorecards and legal delivery breakdowns for the match.
    """
    return match_service.get_match_innings(match_id=match_id)

@router.get("/{match_id}/pressure-timeline", response_model=MatchPressureTimelineResponse)
def get_match_pressure_timeline(match_id: int):
    """
    Returns over-by-over pressure progression and ball-by-ball leverage timeline for a match.
    """
    return match_service.get_pressure_timeline(match_id=match_id)
