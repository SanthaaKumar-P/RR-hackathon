from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from fastapi import HTTPException
from app.services.data_loader import data_loader
from app.utils.validation import normalize_format, paginate_records, sanitize_record, sanitize_records

class MatchService:
    @staticmethod
    def get_matches(
        format_str: Optional[str] = None,
        season: Optional[str] = None,
        stage: Optional[str] = None,
        team: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "match_date",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        fmt = normalize_format(format_str)
        df = data_loader.get_target_matches()

        if fmt:
            df = df[df["match_format"] == fmt]

        if season:
            df = df[df["season"].astype(str) == str(season)]

        if stage:
            df = df[df["stage"].astype(str).str.lower() == stage.strip().lower()]

        if team:
            t = team.strip().lower()
            df = df[(df["home_team"].astype(str).str.lower().str.contains(t, na=False)) |
                    (df["away_team"].astype(str).str.lower().str.contains(t, na=False))]

        if search:
            q = search.strip().lower()
            df = df[(df["home_team"].astype(str).str.lower().str.contains(q, na=False)) |
                    (df["away_team"].astype(str).str.lower().str.contains(q, na=False)) |
                    (df["comp_name"].astype(str).str.lower().str.contains(q, na=False))]

        if sort_by in df.columns:
            ascending = (sort_order.lower() == "asc")
            df = df.sort_values(by=sort_by, ascending=ascending)

        records = sanitize_records(df.to_dict(orient="records"))
        paginated = paginate_records(records, page=page, limit=limit)
        paginated["format"] = fmt
        return paginated

    @staticmethod
    def get_match_by_id(match_id: int) -> Dict[str, Any]:
        df = data_loader.get_target_matches()
        match_rows = df[df["match_id"] == match_id]
        if match_rows.empty:
            raise HTTPException(status_code=404, detail=f"Match with ID {match_id} not found")
        
        row = match_rows.iloc[0].to_dict()
        return sanitize_record(row)

    @staticmethod
    def get_match_innings(match_id: int) -> List[Dict[str, Any]]:
        # Verify match exists
        MatchService.get_match_by_id(match_id)
        
        summary = data_loader.get_innings_summary()
        match_innings = summary[summary["match_id"] == match_id].sort_values("innings")
        return sanitize_records(match_innings.to_dict(orient="records"))

    @staticmethod
    def get_pressure_timeline(match_id: int) -> Dict[str, Any]:
        match_meta = MatchService.get_match_by_id(match_id)
        pressure = data_loader.get_pressure_classified()
        match_del = pressure[pressure["match_id"] == match_id].sort_values(["innings", "innings_ball_num"])
        
        if match_del.empty:
            raise HTTPException(status_code=404, detail=f"No delivery data found for match {match_id}")

        eff_cat = np.where(match_del["innings"] == 1, match_del["first_innings_pressure"], match_del["chase_pressure"])
        match_del = match_del.copy()
        match_del["pressure_category"] = eff_cat

        p_deliveries = []
        overs_map = {}

        for _, row in match_del.iterrows():
            inn = int(row["innings"])
            ov = int(row["overid"])
            p_cat = str(row["pressure_category"])
            phase = str(row.get("innings_phase", "Unknown"))
            runs = int(row.get("runs", 0))
            tot_runs = int(row.get("total_runs", 0))
            is_wkt = bool(row.get("is_wicket", False))

            key = (inn, ov)
            if key not in overs_map:
                overs_map[key] = {
                    "innings": inn,
                    "overid": ov,
                    "runs_in_over": 0,
                    "wickets_in_over": 0,
                    "end_score": int(row.get("current_score", 0)),
                    "end_wickets": int(row.get("wickets_lost", 0)),
                    "pressure_categories": [],
                    "innings_phase": phase
                }

            overs_map[key]["runs_in_over"] += tot_runs
            if is_wkt:
                overs_map[key]["wickets_in_over"] += 1
            overs_map[key]["end_score"] = int(row.get("current_score", 0))
            overs_map[key]["end_wickets"] = int(row.get("wickets_lost", 0))
            overs_map[key]["pressure_categories"].append(p_cat)

            p_deliveries.append({
                "innings": inn,
                "overid": ov,
                "over_ball_num": int(row.get("over_ball_num", 0)),
                "innings_ball_num": int(row.get("innings_ball_num", 0)),
                "striker_name": str(row.get("striker_name", "")),
                "bowler_name": str(row.get("bowler_name", "")),
                "runs": runs,
                "total_runs": tot_runs,
                "is_wicket": is_wkt,
                "current_score": int(row.get("current_score", 0)),
                "wickets_lost": int(row.get("wickets_lost", 0)),
                "pressure_category": p_cat,
                "innings_phase": phase,
                "required_run_rate": float(row["required_run_rate"]) if pd.notna(row.get("required_run_rate")) else None,
                "current_run_rate": float(row["current_run_rate"]) if pd.notna(row.get("current_run_rate")) else None
            })

        overs_list = []
        for key in sorted(overs_map.keys()):
            o = overs_map[key]
            cats = o["pressure_categories"]
            # predominant pressure category
            predom = max(set(cats), key=cats.count) if cats else "Low"
            overs_list.append({
                "innings": o["innings"],
                "overid": o["overid"],
                "runs_in_over": o["runs_in_over"],
                "wickets_in_over": o["wickets_in_over"],
                "end_score": o["end_score"],
                "end_wickets": o["end_wickets"],
                "predominant_pressure": predom,
                "innings_phase": o["innings_phase"]
            })

        total_p_balls = sum(1 for d in p_deliveries if d["pressure_category"] in ["Moderate", "High", "Extreme"])

        return {
            "match_id": match_id,
            "home_team": match_meta.get("home_team"),
            "away_team": match_meta.get("away_team"),
            "match_format": match_meta.get("match_format"),
            "total_pressure_balls": total_p_balls,
            "overs": overs_list,
            "deliveries": p_deliveries
        }

match_service = MatchService()
