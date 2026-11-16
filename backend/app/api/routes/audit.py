from fastapi import APIRouter
from app.schemas.audit import AuditSummaryResponse, DataQualityResponse
from app.services.audit_service import audit_service

router = APIRouter(prefix="/audit", tags=["Audit & Verification"])

@router.get("")
@router.get("/")
def get_audit_root():
    """
    Returns default audit summary for /audit endpoint.
    """
    return audit_service.get_audit_summary()

@router.get("/summary", response_model=AuditSummaryResponse)
def get_audit_summary():
    """
    Returns system audit checkpoints categorized into PASS, WARNING, and NOT VERIFIED:
    - Delivery deduplication and reconciliation (PASS)
    - Competition segmentation (PASS)
    - Wicket credit accounting (PASS)
    - Bowler match denominator correction (PASS)
    - Innings ball limit over-deliveries (WARNING)
    - Matches missing ball-by-ball logs (WARNING)
    - Extras 2 bowler accounting treatment (NOT VERIFIED - Sensitivity analysis)
    - Dismissed player ID imputation policy (PASS)
    """
    return audit_service.get_audit_summary()

@router.get("/data-quality", response_model=DataQualityResponse)
def get_data_quality():
    """
    Returns granular data quality table health reports, issue metrics, and documented limitations.
    """
    return audit_service.get_data_quality()
