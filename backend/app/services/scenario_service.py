from typing import Any, Dict, List, Optional
import pandas as pd
from app.services.data_loader import data_loader
from app.utils.validation import normalize_format, sanitize_records

BATTER_SCENARIO_CONFIG = {
    "Baseline": {
        "description": "Standard balanced evaluation balancing hitting speed, scoring volume, survivability, dot ball control, and match-by-match consistency.",
        "weights": {
            "strike_rate": 25.0,
            "runs_per_match": 20.0,
            "runs_per_dismissal": 15.0,
            "dot_percentage": 15.0,
            "consistency": 25.0
        }
    },
    "Volume_Focused": {
        "description": "Prioritizes match-winning aggregate run contributions and frequent 10+/20+ score outputs over pure scoring rate.",
        "weights": {
            "strike_rate": 20.0,
            "runs_per_match": 30.0,
            "runs_per_dismissal": 10.0,
            "dot_percentage": 10.0,
            "consistency": 30.0
        }
    },
    "Efficiency_Focused": {
        "description": "Rewards explosive acceleration, boundary hitting efficiency, and wicket preservation in high-pressure match situations.",
        "weights": {
            "strike_rate": 30.0,
            "runs_per_match": 15.0,
            "runs_per_dismissal": 20.0,
            "dot_percentage": 20.0,
            "consistency": 15.0
        }
    }
}

BOWLER_SCENARIO_CONFIG = {
    "Baseline": {
        "description": "Standard balanced evaluation balancing strike capability (strike rate & wickets/match), run prevention (economy & dot ball %), and match reliability.",
        "weights": {
            "wickets_per_100": 25.0,
            "economy": 20.0,
            "dot_percentage": 15.0,
            "consistency": 20.0,
            "wickets_per_match": 20.0
        }
    },
    "Wicket_Impact": {
        "description": "Heavily weights breakthrough strike power and high-wicket hauls in pressure overs.",
        "weights": {
            "wickets_per_100": 35.0,
            "economy": 15.0,
            "dot_percentage": 10.0,
            "consistency": 15.0,
            "wickets_per_match": 25.0
        }
    },
    "Control_Focused": {
        "description": "Heavily rewards run strangulation, low economy rates, and high dot ball pressure builds.",
        "weights": {
            "wickets_per_100": 20.0,
            "economy": 25.0,
            "dot_percentage": 20.0,
            "consistency": 20.0,
            "wickets_per_match": 15.0
        }
    }
}

class ScenarioService:
    @staticmethod
    def get_batter_scenarios(format_str: str = "T20") -> Dict[str, Any]:
        fmt = normalize_format(format_str) or "T20"
        df = data_loader.get_final_batter_rankings()
        df_fmt = df[df["match_format"] == fmt].copy()

        sens_df = data_loader.get_ranking_sensitivity()
        sens_fmt = sens_df[(sens_df["format"] == fmt) & (sens_df["player_type"] == "Batter")]

        overlap_map = dict(zip(sens_fmt["scenario"], sens_fmt["top10_overlap_with_baseline"]))

        scenarios_meta = []
        scenario_rankings = {}

        for name, config in BATTER_SCENARIO_CONFIG.items():
            overlap = int(overlap_map.get(name, 10))
            scenarios_meta.append({
                "name": name,
                "description": config["description"],
                "weights": config["weights"],
                "top10_overlap_with_baseline": overlap
            })

            score_col = f"score_{name}"
            if score_col in df_fmt.columns:
                top_scenario = df_fmt.sort_values(score_col, ascending=False).head(10).copy()
                top_scenario["final_rank"] = range(1, len(top_scenario) + 1)
                scenario_rankings[name] = sanitize_records(top_scenario.to_dict(orient="records"))
            else:
                scenario_rankings[name] = []

        return {
            "format": fmt,
            "baseline_weights": BATTER_SCENARIO_CONFIG["Baseline"]["weights"],
            "scenarios": scenarios_meta,
            "scenario_rankings": scenario_rankings
        }

    @staticmethod
    def get_bowler_scenarios(format_str: str = "T20") -> Dict[str, Any]:
        fmt = normalize_format(format_str) or "T20"
        df = data_loader.get_final_bowler_rankings()
        df_fmt = df[df["match_format"] == fmt].copy()

        sens_df = data_loader.get_ranking_sensitivity()
        sens_fmt = sens_df[(sens_df["format"] == fmt) & (sens_df["player_type"] == "Bowler")]
        overlap_map = dict(zip(sens_fmt["scenario"], sens_fmt["top10_overlap_with_baseline"]))

        scenarios_meta = []
        scenario_rankings = {}

        for name, config in BOWLER_SCENARIO_CONFIG.items():
            overlap = int(overlap_map.get(name, 10))
            scenarios_meta.append({
                "name": name,
                "description": config["description"],
                "weights": config["weights"],
                "top10_overlap_with_baseline": overlap
            })

            score_col = f"score_{name}"
            if score_col in df_fmt.columns:
                top_scenario = df_fmt.sort_values(score_col, ascending=False).head(10).copy()
                top_scenario["final_rank"] = range(1, len(top_scenario) + 1)
                scenario_rankings[name] = sanitize_records(top_scenario.to_dict(orient="records"))
            else:
                scenario_rankings[name] = []

        # Accounting sensitivity data
        acct_df = data_loader.get_bowler_accounting_sensitivity()
        acct_fmt = acct_df[acct_df["match_format"] == fmt].copy()

        overlap_count = int((acct_fmt["top10_scenario_a"] & acct_fmt["top10_scenario_b"]).sum())
        changed_count = int(acct_fmt["top10_status_changed"].sum())
        max_movement = int(acct_fmt["rank_change_b_minus_a"].abs().max()) if not acct_fmt.empty else 0

        summary = {
            "scenario_a_description": "Baseline: Charged runs = batter runs + extras1 (wides + oversteps). Extras 2 uncharged.",
            "scenario_b_description": "Sensitivity: Scenario A + extras_2_runs on oversteps charged to bowler.",
            "top10_overlap": overlap_count,
            "top10_overlap_pct": round((overlap_count / 10) * 100, 1),
            "top10_membership_changed_count": changed_count,
            "max_rank_movement": max_movement
        }

        acct_items = sanitize_records(acct_fmt.to_dict(orient="records"))

        return {
            "format": fmt,
            "baseline_weights": BOWLER_SCENARIO_CONFIG["Baseline"]["weights"],
            "scenarios": scenarios_meta,
            "scenario_rankings": scenario_rankings,
            "accounting_sensitivity_summary": summary,
            "accounting_sensitivity_items": acct_items
        }

scenario_service = ScenarioService()
