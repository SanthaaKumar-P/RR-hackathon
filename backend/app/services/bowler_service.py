from typing import Any, Dict, List, Optional
import pandas as pd
from fastapi import HTTPException
from app.services.data_loader import data_loader
from app.utils.validation import normalize_format, paginate_records, sanitize_record, sanitize_records

class BowlerService:
    @staticmethod
    def get_bowlers(
        format_str: Optional[str] = None,
        search: Optional[str] = None,
        eligible: Optional[bool] = None,
        sort_by: str = "final_rank",
        sort_order: str = "asc",
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        fmt = normalize_format(format_str)
        df = data_loader.get_final_bowler_rankings()

        if fmt:
            df = df[df["match_format"] == fmt]

        if eligible is not None:
            if eligible is True:
                df = df[df["eligible"] == True]
            else:
                comp_df = data_loader.get_competition_bowler()
                if comp_df is not None:
                    ranked_ids = set(df["bowler_id"])
                    ineligible_df = comp_df[~comp_df["bowler_id"].isin(ranked_ids)].copy()
                    if fmt:
                        ineligible_df = ineligible_df[ineligible_df["match_format"] == fmt]
                    ineligible_df["eligible"] = False
                    ineligible_df["final_rank"] = None
                    ineligible_df["final_score"] = None
                    df = ineligible_df

        if search:
            query = search.strip().lower()
            if query.isdigit():
                df = df[df["bowler_id"] == int(query)]
            else:
                df = df[df["bowler_name"].astype(str).str.lower().str.contains(query, na=False)]

        # Sorting
        if sort_by in df.columns:
            ascending = (sort_order.lower() == "asc")
            df = df.sort_values(by=sort_by, ascending=ascending, na_position="last")
        else:
            df = df.sort_values(by="final_rank", ascending=True)

        records = sanitize_records(df.to_dict(orient="records"))
        paginated = paginate_records(records, page=page, limit=limit)
        paginated["format"] = fmt
        return paginated

    @staticmethod
    def get_top10(format_str: str = "T20") -> Dict[str, Any]:
        fmt = normalize_format(format_str) or "T20"
        top10_df = data_loader.get_top10_bowlers()
        fmt_top10 = top10_df[top10_df["match_format"] == fmt].sort_values("final_rank")
        
        items = sanitize_records(fmt_top10.to_dict(orient="records"))
        return {
            "format": fmt,
            "count": len(items),
            "items": items
        }

    @staticmethod
    def get_bowler_by_id(player_id: int, format_str: Optional[str] = None) -> Dict[str, Any]:
        fmt = normalize_format(format_str)
        df = data_loader.get_final_bowler_rankings()
        
        player_matches = df[df["bowler_id"] == player_id]
        if fmt:
            player_matches = player_matches[player_matches["match_format"] == fmt]
        
        if player_matches.empty:
            comp_df = data_loader.get_competition_bowler()
            if comp_df is not None:
                p_comp = comp_df[comp_df["bowler_id"] == player_id]
                if fmt:
                    p_comp = p_comp[p_comp["match_format"] == fmt]
                if not p_comp.empty:
                    rec = sanitize_record(p_comp.iloc[0].to_dict())
                    rec["eligible"] = False
                    rec["final_rank"] = None
                    rec["final_score"] = None
                    return {
                        "player_id": player_id,
                        "player_name": rec.get("bowler_name", "Unknown"),
                        "match_format": rec.get("match_format", fmt or "Unknown"),
                        "ranking": rec,
                        "methodology_weights": {
                            "wickets_per_100": 0.25,
                            "economy": 0.20,
                            "dot_percentage": 0.15,
                            "consistency": 0.20,
                            "wickets_per_match": 0.20
                        },
                        "scenarios": {},
                        "accounting_sensitivity": None,
                        "raw_stats": rec
                    }
            raise HTTPException(
                status_code=404,
                detail=f"Bowler with ID {player_id} not found" + (f" for format '{fmt}'" if fmt else "")
            )

        row = player_matches.iloc[0].to_dict()
        clean_row = sanitize_record(row)

        # Check bowler accounting sensitivity
        sensitivity_df = data_loader.get_bowler_accounting_sensitivity()
        sens_match = sensitivity_df[(sensitivity_df["bowler_id"] == player_id)]
        if fmt:
            sens_match = sens_match[sens_match["match_format"] == fmt]
        accounting_sensitivity = sanitize_record(sens_match.iloc[0].to_dict()) if not sens_match.empty else None

        return {
            "player_id": player_id,
            "player_name": clean_row.get("bowler_name"),
            "match_format": clean_row.get("match_format"),
            "ranking": clean_row,
            "methodology_weights": {
                "wickets_per_100": 0.25,
                "economy": 0.20,
                "dot_percentage": 0.15,
                "consistency": 0.20,
                "wickets_per_match": 0.20
            },
            "scenarios": {
                "Baseline": clean_row.get("score_Baseline"),
                "Wicket_Impact": clean_row.get("score_Wicket_Impact"),
                "Control_Focused": clean_row.get("score_Control_Focused")
            },
            "accounting_sensitivity": accounting_sensitivity,
            "raw_stats": {
                "pressure_runs_conceded": clean_row.get("pressure_runs_conceded"),
                "pressure_legal_balls": clean_row.get("pressure_legal_balls"),
                "pressure_wickets": clean_row.get("pressure_wickets"),
                "pressure_matches": clean_row.get("pressure_matches"),
                "pressure_economy": clean_row.get("pressure_economy"),
                "pressure_dot_percentage": clean_row.get("pressure_dot_percentage"),
                "wickets_per_100": clean_row.get("wickets_per_100"),
                "wickets_per_match": clean_row.get("wickets_per_match"),
                "consistency": clean_row.get("consistency")
            }
        }

bowler_service = BowlerService()
