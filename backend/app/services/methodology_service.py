from typing import Any, Dict
from app.services.data_loader import data_loader

class MethodologyService:
    @staticmethod
    def get_methodology() -> Dict[str, Any]:
        return {
            "title": "SupeRR Selector - Pressure Performance Ranking Methodology",
            "season": "Season 2",
            "round": "Round 1",
            "competition_segmentation": "T20 and T20I are ranked strictly independently. No cross-format percentile normalization or pooled ranking.",
            "pressure_definition": "Only Moderate, High and Extreme pressure deliveries are included. First innings leverage uses first_innings_pressure; second innings chase uses chase_pressure. Low and Not Applicable deliveries are excluded from pressure metrics.",
            "eligibility_thresholds": {
                "batters": {
                    "min_balls": 100,
                    "min_matches": 10,
                    "denominator_rule": "Minimum 100 pressure balls faced and minimum 10 pressure matches played."
                },
                "bowlers": {
                    "min_balls": 60,
                    "min_matches": 10,
                    "denominator_rule": "Minimum 60 pressure legal balls and minimum 10 verified pressure matches (containing >=1 valid pressure legal delivery)."
                }
            },
            "batter_baseline_weights": {
                "strike_rate": 0.25,
                "runs_per_match": 0.20,
                "runs_per_dismissal": 0.15,
                "dot_percentage": 0.15,
                "consistency": 0.25
            },
            "bowler_baseline_weights": {
                "wickets_per_100": 0.25,
                "economy": 0.20,
                "dot_percentage": 0.15,
                "consistency": 0.20,
                "wickets_per_match": 0.20
            },
            "scoring_directions": {
                "batters": {
                    "pressure_strike_rate": "higher_is_better",
                    "runs_per_match": "higher_is_better",
                    "runs_per_dismissal": "higher_is_better",
                    "pressure_dot_percentage": "lower_is_better",
                    "consistency": "higher_is_better"
                },
                "bowlers": {
                    "wickets_per_100": "higher_is_better",
                    "pressure_economy": "lower_is_better",
                    "pressure_dot_percentage": "higher_is_better",
                    "consistency": "higher_is_better",
                    "wickets_per_match": "higher_is_better"
                }
            },
            "consistency_formulas": {
                "batters": "0.60 * (% of pressure matches with 10+ runs) + 0.40 * (% of pressure matches with 20+ runs)",
                "bowlers": "0.70 * (% of verified matches with 1+ credited wickets) + 0.30 * (% of verified matches with 2+ credited wickets). Denominator strictly includes matches with >=1 valid pressure legal delivery."
            },
            "wicket_credit_rules": {
                "credited_dismissals": [
                    "Bowled",
                    "Caught",
                    "LBW",
                    "Stump",
                    "Hit Wicket"
                ],
                "excluded_dismissals": [
                    "Run Out",
                    "Retired Out",
                    "Obstructing Field",
                    "Handled Ball",
                    "Timed Out"
                ]
            },
            "extras_accounting_scenarios": {
                "Scenario_A (Baseline)": "Charged bowler runs = batter runs + extras1 for wides and oversteps. Unverified extras_2_runs and other extras are not charged to the bowler.",
                "Scenario_B (Sensitivity)": "Scenario A + extras_2_runs on oversteps charged to bowler. Used strictly as a sensitivity test, not an official scoring standard."
            },
            "alternative_weight_scenarios": {
                "batters": {
                    "Baseline": {"strike_rate": 25, "runs_per_match": 20, "runs_per_dismissal": 15, "dot_percentage": 15, "consistency": 25},
                    "Volume_Focused": {"strike_rate": 20, "runs_per_match": 30, "runs_per_dismissal": 10, "dot_percentage": 10, "consistency": 30},
                    "Efficiency_Focused": {"strike_rate": 30, "runs_per_match": 15, "runs_per_dismissal": 20, "dot_percentage": 20, "consistency": 15}
                },
                "bowlers": {
                    "Baseline": {"wickets_per_100": 25, "economy": 20, "dot_percentage": 15, "consistency": 20, "wickets_per_match": 20},
                    "Wicket_Impact": {"wickets_per_100": 35, "economy": 15, "dot_percentage": 10, "consistency": 15, "wickets_per_match": 25},
                    "Control_Focused": {"wickets_per_100": 20, "economy": 25, "dot_percentage": 20, "consistency": 20, "wickets_per_match": 15}
                }
            },
            "project_assumptions_and_limitations": [
                "This analytical framework is a project-defined research model developed for Rajasthan Royals SupeRR Selector Season 2, not an official ICC or IPL selection committee metric.",
                "Pressure classifications (Moderate, High, Extreme) are derived from match leverage conditions including required run rate and wickets lost.",
                "Percentiles are calculated strictly among eligible players within the same format using average rank ties.",
                "Bowler pressure match denominator replaces the legacy pressure_matches field with verified legal delivery matches to prevent denominator inflation."
            ]
        }

methodology_service = MethodologyService()
