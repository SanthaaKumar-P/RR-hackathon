from typing import Any, Dict, List
import numpy as np
import pandas as pd
from app.services.data_loader import data_loader
from app.utils.validation import sanitize_records

class OverviewService:
    @staticmethod
    def get_overview_data() -> Dict[str, Any]:
        matches = data_loader.get_target_matches()
        pressure = data_loader.get_pressure_classified()
        batters = data_loader.get_final_batter_rankings()
        bowlers = data_loader.get_final_bowler_rankings()

        total_matches = int(len(matches))
        total_selected_deliveries = int(len(pressure))

        # Pressure deliveries criteria:
        # Innings 1: Moderate, High, Extreme
        # Innings 2: Moderate, High, Extreme
        p_flag = (
            ((pressure["innings"] == 1) & pressure["first_innings_pressure"].isin(["Moderate", "High", "Extreme"])) |
            ((pressure["innings"] == 2) & pressure["chase_pressure"].isin(["Moderate", "High", "Extreme"]))
        )
        total_pressure_deliveries = int(p_flag.sum())

        format_match_counts = {
            "T20": int((matches["match_format"] == "T20").sum()),
            "T20I": int((matches["match_format"] == "T20I").sum())
        }

        ranked_batters_count = {
            "total": int(len(batters)),
            "T20": int((batters["match_format"] == "T20").sum()),
            "T20I": int((batters["match_format"] == "T20I").sum())
        }

        ranked_bowlers_count = {
            "total": int(len(bowlers)),
            "T20": int((bowlers["match_format"] == "T20").sum()),
            "T20I": int((bowlers["match_format"] == "T20I").sum())
        }

        # Effective pressure distribution
        eff_pressure = np.where(pressure["innings"] == 1, pressure["first_innings_pressure"], pressure["chase_pressure"])
        eff_series = pd.Series(eff_pressure).value_counts()
        pressure_category_distribution = {str(k): int(v) for k, v in eff_series.items()}

        # Phase distribution
        phase_counts = pressure["innings_phase"].value_counts()
        phase_distribution = {str(k): int(v) for k, v in phase_counts.items()}

        # Top 5 batters
        top5_batters = {}
        for fmt in ["T20", "T20I"]:
            b_fmt = batters[batters["match_format"] == fmt].sort_values("final_rank").head(5)
            top5_batters[fmt] = sanitize_records(b_fmt.to_dict(orient="records"))

        # Top 5 bowlers
        top5_bowlers = {}
        for fmt in ["T20", "T20I"]:
            w_fmt = bowlers[bowlers["match_format"] == fmt].sort_values("final_rank").head(5)
            top5_bowlers[fmt] = sanitize_records(w_fmt.to_dict(orient="records"))

        return {
            "total_matches": total_matches,
            "total_selected_deliveries": total_selected_deliveries,
            "total_pressure_deliveries": total_pressure_deliveries,
            "match_counts": format_match_counts,
            "ranked_batters_count": ranked_batters_count,
            "ranked_bowlers_count": ranked_bowlers_count,
            "pressure_category_distribution": pressure_category_distribution,
            "phase_distribution": phase_distribution,
            "top5_batters": top5_batters,
            "top5_bowlers": top5_bowlers
        }

overview_service = OverviewService()
