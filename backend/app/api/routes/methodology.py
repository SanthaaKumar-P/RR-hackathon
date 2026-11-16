from fastapi import APIRouter
from app.schemas.methodology import MethodologyResponse
from app.services.methodology_service import methodology_service

router = APIRouter(prefix="/methodology", tags=["Methodology"])

@router.get("", response_model=MethodologyResponse)
def get_methodology():
    """
    Returns complete project methodology documentation:
    - Eligibility sample cutoffs
    - Baseline weights for batters and bowlers
    - Metric definitions & directionality
    - Consistency calculation formulas
    - Dismissal classification & wicket accounting rules
    - Extras accounting sensitivity definitions
    - Core assumptions & analytical limitations
    """
    return methodology_service.get_methodology()
