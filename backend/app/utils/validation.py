import math
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from fastapi import HTTPException

VALID_FORMATS = ["T20", "T20I"]

def normalize_format(format_str: Optional[str]) -> Optional[str]:
    if not format_str:
        return None
    fmt = format_str.strip().upper()
    if fmt in ["T20", "IPL"]:
        return "T20"
    if fmt in ["T20I", "INTERNATIONAL"]:
        return "T20I"
    if fmt == "ALL":
        return None
    raise HTTPException(
        status_code=400,
        detail=f"Invalid format '{format_str}'. Supported formats: {', '.join(VALID_FORMATS)}"
    )

def sanitize_value(val: Any) -> Any:
    if val is None:
        return None
    if isinstance(val, (float, np.floating)):
        if np.isnan(val) or np.isinf(val) or math.isnan(val) or math.isinf(val):
            return None
        return float(val)
    if isinstance(val, (int, np.integer)):
        return int(val)
    if isinstance(val, (bool, np.bool_)):
        return bool(val)
    if pd.isna(val):
        return None
    return val

def sanitize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    return {k: sanitize_value(v) for k, v in record.items()}

def sanitize_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [sanitize_record(r) for r in records]

def paginate_records(records: List[Dict[str, Any]], page: int = 1, limit: int = 20) -> Dict[str, Any]:
    total = len(records)
    total_pages = max(1, math.ceil(total / limit)) if total > 0 else 1
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    items = records[start_idx:end_idx]
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "items": items
    }
