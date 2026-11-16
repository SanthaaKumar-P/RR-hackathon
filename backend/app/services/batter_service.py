from typing import Any, Dict, List, Optional
import pandas as pd
from fastapi import HTTPException
from app.services.data_loader import data_loader
from app.utils.validation import normalize_format, paginate_records, sanitize_record, sanitize_records

class BatterService:
    @staticmethod
    def get_batters(
        format_str: Optional[str] = None,
        search: Optional[str] = None,
        eligible: Optional[bool] = None,
        sort_by: str = "final_rank",
        sort_order: str = "asc",
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        fmt = normalize_format(format_str)
        df = data_loader.get_final_batter_rankings()

        if fmt:
            df = df[df["match_format"] == fmt]

        if eligible is not None:
            if eligible is True:
                df = df[df["eligible"] == True]
            else:
                # If specifically asking for ineligible, fetch from competition_batter
                comp_df = data_loader.get_competition_batter()
                if comp_df is not None:
                    ranked_ids = set(df["striker_id"])
                    ineligible_df = comp_df[~comp_df["striker_id"].isin(ranked_ids)].copy()
                    if fmt:
                        ineligible_df = ineligible_df[ineligible_df["match_format"] == fmt]
                    ineligible_df["eligible"] = False
                    ineligible_df["final_rank"] = None
                    ineligible_df["final_score"] = None
                    df = ineligible_df

        if search:
            query = search.strip().lower()
            if query.isdigit():
                df = df[df["striker_id"] == int(query)]
            else:
                df = df[df["striker_name"].astype(str).str.lower().str.contains(query, na=False)]

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
        top10_df = data_loader.get_top10_batters()
        fmt_top10 = top10_df[top10_df["match_format"] == fmt].sort_values("final_rank")
        
        items = sanitize_records(fmt_top10.to_dict(orient="records"))
        return {
            "format": fmt,
            "count": len(items),
            "items": items
        }

    @staticmethod
    def get_batter_by_id(player_id: int, format_str: Optional[str] = None) -> Dict[str, Any]:
        fmt = normalize_format(format_str)
        df = data_loader.get_final_batter_rankings()
        
        player_matches = df[df["striker_id"] == player_id]
        if fmt:
            player_matches = player_matches[player_matches["match_format"] == fmt]
        
        if player_matches.empty:
            # Check competition performance for unranked player
            comp_df = data_loader.get_competition_batter()
            if comp_df is not None:
                p_comp = comp_df[comp_df["striker_id"] == player_id]
                if fmt:
                    p_comp = p_comp[p_comp["match_format"] == fmt]
                if not p_comp.empty:
                    rec = sanitize_record(p_comp.iloc[0].to_dict())
                    rec["eligible"] = False
                    rec["final_rank"] = None
                    rec["final_score"] = None
                    return {
                        "player_id": player_id,
                        "player_name": rec.get("striker_name", "Unknown"),
                        "match_format": rec.get("match_format", fmt or "Unknown"),
                        "ranking": rec,
                        "methodology_weights": {
                            "strike_rate": 0.25,
                            "runs_per_match": 0.20,
                            "runs_per_dismissal": 0.15,
                            "dot_percentage": 0.15,
                            "consistency": 0.25
                        },
                        "scenarios": {},
                        "raw_stats": rec
                    }
            raise HTTPException(
                status_code=404,
                detail=f"Batter with ID {player_id} not found" + (f" for format '{fmt}'" if fmt else "")
            )

        row = player_matches.iloc[0].to_dict()
        clean_row = sanitize_record(row)

        return {
            "player_id": player_id,
            "player_name": clean_row.get("striker_name"),
            "match_format": clean_row.get("match_format"),
            "ranking": clean_row,
            "methodology_weights": {
                "strike_rate": 0.25,
                "runs_per_match": 0.20,
                "runs_per_dismissal": 0.15,
                "dot_percentage": 0.15,
                "consistency": 0.25
            },
            "scenarios": {
                "Baseline": clean_row.get("score_Baseline"),
                "Volume_Focused": clean_row.get("score_Volume_Focused"),
                "Efficiency_Focused": clean_row.get("score_Efficiency_Focused")
            },
            "raw_stats": {
                "pressure_runs": clean_row.get("pressure_runs"),
                "pressure_balls": clean_row.get("pressure_balls"),
                "pressure_matches": clean_row.get("pressure_matches"),
                "pressure_strike_rate": clean_row.get("pressure_strike_rate"),
                "pressure_dot_percentage": clean_row.get("pressure_dot_percentage"),
                "runs_per_match": clean_row.get("runs_per_match"),
                "runs_per_dismissal": clean_row.get("runs_per_dismissal"),
                "consistency": clean_row.get("consistency")
            }
        }

batter_service = BatterService()
