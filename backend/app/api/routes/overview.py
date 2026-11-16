from fastapi import APIRouter
from app.schemas.overview import OverviewResponse
from app.services.overview_service import overview_service

router = APIRouter(prefix="", tags=["Overview"])

@router.get("/overview", response_model=OverviewResponse)
def get_overview():
    """
    Returns platform-wide summary statistics:
    - Total matches and deliveries analyzed
    - Total pressure deliveries
    - Match and player breakdown by format (T20 vs T20I)
    - Pressure category and phase distributions
    - Top 5 batters and bowlers per format
    """
    return overview_service.get_overview_data()
