from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.schemas.comparison import PlayerComparisonResponse
from app.services.comparison_service import comparison_service

router = APIRouter(prefix="/compare", tags=["Player Comparison"])

def parse_ids(id_str: str):
    if not id_str:
        return []
    parts = id_str.split(",")
    ids = []
    for p in parts:
        clean = p.strip()
        if clean.isdigit():
            ids.append(int(clean))
    return ids

@router.get("/batters", response_model=PlayerComparisonResponse)
def compare_batters(
    player_ids: str = Query(..., description="Comma-separated player IDs (e.g. '1699,4260')"),
    format: Optional[str] = Query("T20", description="Competition format: T20 or T20I")
):
    """
    Side-by-side metric comparison and percentile matrix for two or more batters.
    """
    parsed_ids = parse_ids(player_ids)
    if len(parsed_ids) < 1:
        raise HTTPException(status_code=400, detail="Please provide at least one valid integer player ID in player_ids")
    return comparison_service.compare_batters(player_ids=parsed_ids, format_str=format)

@router.get("/bowlers", response_model=PlayerComparisonResponse)
def compare_bowlers(
    player_ids: str = Query(..., description="Comma-separated player IDs (e.g. '4641,8661')"),
    format: Optional[str] = Query("T20", description="Competition format: T20 or T20I")
):
    """
    Side-by-side metric comparison and percentile matrix for two or more bowlers.
    """
    parsed_ids = parse_ids(player_ids)
    if len(parsed_ids) < 1:
        raise HTTPException(status_code=400, detail="Please provide at least one valid integer player ID in player_ids")
    return comparison_service.compare_bowlers(player_ids=parsed_ids, format_str=format)
