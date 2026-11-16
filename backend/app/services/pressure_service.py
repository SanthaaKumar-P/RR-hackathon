from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from app.services.data_loader import data_loader
from app.utils.validation import normalize_format, paginate_records, sanitize_records

CATEGORY_DEFINITIONS = {
    "Extreme": "Critical match leverage moments where required run rate is high or multiple wickets have fallen in quick succession.",
    "High": "Significant pressure deliveries: required run rate above benchmark or batting collapse in progress.",
    "Moderate": "Above-average leverage where the match balance hangs in the balance.",
    "Low": "Normal baseline deliveries with comfortable run rate and ample wickets remaining.",
    "Not Applicable": "Deliveries where pressure calculation does not apply or innings data is incomplete."
}

PHASE_OVERS = {
    "Powerplay": "Overs 1 - 6",
    "Middle": "Overs 7 - 15",
    "Death": "Overs 16 - 20"
}

class PressureService:
    @staticmethod
    def get_summary(format_str: Optional[str] = None) -> Dict[str, Any]:
        fmt = normalize_format(format_str)
        pressure = data_loader.get_pressure_classified()
        matches = data_loader.get_target_matches()

        if fmt:
            fmt_matches = set(matches[matches["match_format"] == fmt]["match_id"])
            pressure = pressure[pressure["match_id"].isin(fmt_matches)]

        total_del = len(pressure)
        if total_del == 0:
            return {}

        p_flag = (
            ((pressure["innings"] == 1) & pressure["first_innings_pressure"].isin(["Moderate", "High", "Extreme"])) |
            ((pressure["innings"] == 2) & pressure["chase_pressure"].isin(["Moderate", "High", "Extreme"]))
        )

        p_df = pressure[p_flag]
        p_count = len(p_df)
        p_pct = round((p_count / total_del) * 100, 2)

        # Overall numbers
        tot_runs = int(pressure["total_runs"].sum())
        tot_wkts = int(pressure["is_wicket"].astype(bool).sum())
        tot_dots = int((pressure["total_runs"] == 0).sum())
        tot_boundaries = int((pressure["is_four"].astype(bool) | pressure["is_six"].astype(bool)).sum())
        overall_rr = round((tot_runs / total_del) * 6, 2)
        overall_boundary_pct = round((tot_boundaries / total_del) * 100, 2)
        overall_dot_pct = round((tot_dots / total_del) * 100, 2)

        # Pressure numbers
        p_runs = int(p_df["total_runs"].sum())
        p_wkts = int(p_df["is_wicket"].astype(bool).sum())
        p_dots = int((p_df["total_runs"] == 0).sum())
        p_boundaries = int((p_df["is_four"].astype(bool) | p_df["is_six"].astype(bool)).sum())
        p_rr = round((p_runs / p_count) * 6, 2) if p_count > 0 else 0.0
        p_boundary_pct = round((p_boundaries / p_count) * 100, 2) if p_count > 0 else 0.0
        p_dot_pct = round((p_dots / p_count) * 100, 2) if p_count > 0 else 0.0

        return {
            "format": fmt,
            "total_deliveries": total_del,
            "pressure_deliveries": p_count,
            "pressure_delivery_pct": p_pct,
            "overall_performance": {
                "deliveries": total_del,
                "runs": tot_runs,
                "wickets": tot_wkts,
                "run_rate": overall_rr,
                "boundary_percentage": overall_boundary_pct,
                "dot_percentage": overall_dot_pct
            },
            "pressure_performance": {
                "deliveries": p_count,
                "runs": p_runs,
                "wickets": p_wkts,
                "run_rate": p_rr,
                "boundary_percentage": p_boundary_pct,
                "dot_percentage": p_dot_pct
            },
            "pressure_delta": {
                "run_rate_diff": round(p_rr - overall_rr, 2),
                "boundary_pct_diff": round(p_boundary_pct - overall_boundary_pct, 2),
                "dot_pct_diff": round(p_dot_pct - overall_dot_pct, 2)
            }
        }

    @staticmethod
    def get_categories() -> List[Dict[str, Any]]:
        pressure = data_loader.get_pressure_classified()
        eff_pressure = np.where(pressure["innings"] == 1, pressure["first_innings_pressure"], pressure["chase_pressure"])
        pressure = pressure.copy()
        pressure["effective_category"] = eff_pressure

        total_del = len(pressure)
        result = []

        for cat in ["Extreme", "High", "Moderate", "Low", "Not Applicable"]:
            sub = pressure[pressure["effective_category"] == cat]
            sub_count = len(sub)
            if sub_count == 0:
                continue
            runs = int(sub["total_runs"].sum())
            wkts = int(sub["is_wicket"].astype(bool).sum())
            dots = int((sub["total_runs"] == 0).sum())
            boundaries = int((sub["is_four"].astype(bool) | sub["is_six"].astype(bool)).sum())

            result.append({
                "category": cat,
                "deliveries": sub_count,
                "percentage": round((sub_count / total_del) * 100, 2),
                "runs": runs,
                "wickets": wkts,
                "run_rate": round((runs / sub_count) * 6, 2),
                "boundary_percentage": round((boundaries / sub_count) * 100, 2),
                "dot_percentage": round((dots / sub_count) * 100, 2),
                "definition": CATEGORY_DEFINITIONS.get(cat, "")
            })

        return result

    @staticmethod
    def get_phases() -> List[Dict[str, Any]]:
        pressure = data_loader.get_pressure_classified()
        p_flag = (
            ((pressure["innings"] == 1) & pressure["first_innings_pressure"].isin(["Moderate", "High", "Extreme"])) |
            ((pressure["innings"] == 2) & pressure["chase_pressure"].isin(["Moderate", "High", "Extreme"]))
        )
        pressure = pressure.copy()
        pressure["is_pressure"] = p_flag

        result = []
        for phase in ["Powerplay", "Middle", "Death"]:
            sub = pressure[pressure["innings_phase"] == phase]
            total_sub = len(sub)
            if total_sub == 0:
                continue
            p_sub = sub[sub["is_pressure"]]
            p_count = len(p_sub)
            runs = int(sub["total_runs"].sum())
            wkts = int(sub["is_wicket"].astype(bool).sum())
            dots = int((sub["total_runs"] == 0).sum())

            result.append({
                "phase": phase,
                "overs": PHASE_OVERS.get(phase, ""),
                "deliveries": p_count,
                "total_deliveries": total_sub,
                "pressure_deliveries": p_count,
                "pressure_pct": round((p_count / total_sub) * 100, 2),
                "runs": runs,
                "wickets": wkts,
                "run_rate": round((runs / total_sub) * 6, 2),
                "dot_percentage": round((dots / total_sub) * 100, 2)
            })

        return result

    @staticmethod
    def get_batter_performance(search: Optional[str] = None, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        df = data_loader.get_batter_performance()
        if df is None:
            return {"total": 0, "page": page, "limit": limit, "total_pages": 1, "items": []}

        if search:
            query = search.strip().lower()
            if query.isdigit():
                df = df[df["striker_id"] == int(query)]
            else:
                df = df[df["striker_name"].astype(str).str.lower().str.contains(query, na=False)]

        records = sanitize_records(df.to_dict(orient="records"))
        return paginate_records(records, page=page, limit=limit)

    @staticmethod
    def get_bowler_performance(search: Optional[str] = None, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        df = data_loader.get_bowler_performance()
        if df is None:
            return {"total": 0, "page": page, "limit": limit, "total_pages": 1, "items": []}

        if search:
            query = search.strip().lower()
            if query.isdigit():
                df = df[df["bowler_id"] == int(query)]
            else:
                df = df[df["bowler_name"].astype(str).str.lower().str.contains(query, na=False)]

        records = sanitize_records(df.to_dict(orient="records"))
        return paginate_records(records, page=page, limit=limit)

pressure_service = PressureService()
