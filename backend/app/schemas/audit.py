from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class AuditCheckItem(BaseModel):
    audit_name: str
    category: str
    status: str  # PASS, WARNING, NOT VERIFIED
    description: str
    records_checked: int
    findings: str
    action_taken: str

class AuditSummaryResponse(BaseModel):
    total_audits: int
    passed_count: int
    warning_count: int
    not_verified_count: int
    overall_health: str
    audits: List[AuditCheckItem]

class DataQualityTableStatus(BaseModel):
    table_name: str
    total_records: int
    issues_detected: int
    severity: str
    description: str

class DataQualityResponse(BaseModel):
    total_deliveries: int
    total_matches: int
    tables: List[DataQualityTableStatus]
    limitations: List[str]
