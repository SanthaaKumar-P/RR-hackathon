from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from app.services.data_loader import data_loader
from app.utils.validation import normalize_format, sanitize_records

BATTER_METRICS = [
    ("final_rank", "Final Rank", False), # lower rank is better (rank 1 is best)
    ("final_score", "Ranking Score", True),
    ("pressure_strike_rate", "Pressure Strike Rate", True),
    ("runs_per_match", "Runs Per Match", True),
    ("runs_per_dismissal", "Runs Per Dismissal", True),
    ("pressure_dot_percentage", "Dot Ball %", False), # lower is better
    ("consistency", "Consistency %", True),
    ("pressure_runs", "Pressure Runs", True),
    ("pressure_balls", "Pressure Balls Faced", True),
    ("pressure_matches", "Pressure Matches", True),
    ("top10_scenario_count", "Scenario Robustness (Top 10 count)", True)
]

BOWLER_METRICS = [
    ("final_rank", "Final Rank", False), # lower rank is better
    ("final_score", "Ranking Score", True),
    ("wickets_per_100", "Wickets Per 100 Balls", True),
    ("pressure_economy", "Pressure Economy", False), # lower is better
    ("pressure_dot_percentage", "Dot Ball %", True), # higher is better
    ("consistency", "Consistency %", True),
    ("wickets_per_match", "Wickets Per Match", True),
    ("pressure_wickets", "Pressure Wickets", True),
    ("pressure_legal_balls", "Pressure Legal Balls", True),
    ("pressure_matches", "Pressure Matches", True),
    ("top10_scenario_count", "Scenario Robustness (Top 10 count)", True)
]

class ComparisonService:
    @staticmethod
    def compare_batters(player_ids: List[int], format_str: Optional[str] = "T20") -> Dict[str, Any]:
        fmt = normalize_format(format_str) or "T20"
        df = data_loader.get_final_batter_rankings()
        df_fmt = df[df["match_format"] == fmt]

        players_df = df_fmt[df_fmt["striker_id"].isin(player_ids)]
        if players_df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"None of the requested batter IDs {player_ids} found in format {fmt}"
            )

        players_list = sanitize_records(players_df.to_dict(orient="records"))

        matrix = []
        for metric_key, metric_label, higher_is_better in BATTER_METRICS:
            values = {}
            percentiles = {}
            best_val = None
            best_player_id = None

            for p in players_list:
                pid = str(p["striker_id"])
                val = p.get(metric_key)
                values[pid] = val

                # Percentile score if available
                pct_key = f"score_{metric_key}"
                percentiles[pid] = p.get(pct_key, None)

                if val is not None:
                    if best_val is None:
                        best_val = val
                        best_player_id = p["striker_id"]
                    else:
                        if higher_is_better and val > best_val:
                            best_val = val
                            best_player_id = p["striker_id"]
                        elif not higher_is_better and val < best_val:
                            best_val = val
                            best_player_id = p["striker_id"]

            matrix.append({
                "metric_key": metric_key,
                "metric_label": metric_label,
                "higher_is_better": higher_is_better,
                "values": values,
                "percentiles": percentiles,
                "leader_player_id": best_player_id
            })

        return {
            "player_type": "Batter",
            "format": fmt,
            "player_ids": [p["striker_id"] for p in players_list],
            "players": players_list,
            "metric_matrix": matrix
        }

    @staticmethod
    def compare_bowlers(player_ids: List[int], format_str: Optional[str] = "T20") -> Dict[str, Any]:
        fmt = normalize_format(format_str) or "T20"
        df = data_loader.get_final_bowler_rankings()
        df_fmt = df[df["match_format"] == fmt]

        players_df = df_fmt[df_fmt["bowler_id"].isin(player_ids)]
        if players_df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"None of the requested bowler IDs {player_ids} found in format {fmt}"
            )

        players_list = sanitize_records(players_df.to_dict(orient="records"))

        matrix = []
        for metric_key, metric_label, higher_is_better in BOWLER_METRICS:
            values = {}
            percentiles = {}
            best_val = None
            best_player_id = None

            for p in players_list:
                pid = str(p["bowler_id"])
                val = p.get(metric_key)
                values[pid] = val

                pct_key = f"score_{metric_key}"
                percentiles[pid] = p.get(pct_key, None)

                if val is not None:
                    if best_val is None:
                        best_val = val
                        best_player_id = p["bowler_id"]
                    else:
                        if higher_is_better and val > best_val:
                            best_val = val
                            best_player_id = p["bowler_id"]
                        elif not higher_is_better and val < best_val:
                            best_val = val
                            best_player_id = p["bowler_id"]

            matrix.append({
                "metric_key": metric_key,
                "metric_label": metric_label,
                "higher_is_better": higher_is_better,
                "values": values,
                "percentiles": percentiles,
                "leader_player_id": best_player_id
            })

        return {
            "player_type": "Bowler",
            "format": fmt,
            "player_ids": [p["bowler_id"] for p in players_list],
            "players": players_list,
            "metric_matrix": matrix
        }

comparison_service = ComparisonService()
