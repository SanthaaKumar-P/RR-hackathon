
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# SUPERR SELECTOR - PRESSURE PERFORMANCE RANKING ENGINE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BATTER_FILE = DATA_DIR / "competition_batter_performance.csv"
BOWLER_FILE = DATA_DIR / "competition_bowler_performance.csv"
PRESSURE_FILE = DATA_DIR / "pressure_classified.csv"
MATCH_FILE = DATA_DIR / "target_matches.csv"

MIN_BATTER_BALLS = 100
MIN_BATTER_MATCHES = 10

MIN_BOWLER_BALLS = 60
MIN_BOWLER_MATCHES = 10

FORMATS = ["T20", "T20I"]

CREDITED_WICKETS = [
    "Bowled",
    "Caught",
    "LBW",
    "Stump",
    "Hit Wicket"
]

PRESSURE_CATEGORIES = [
    "Moderate",
    "High",
    "Extreme"
]

BATTER_SCENARIOS = {
    "Baseline": {
        "strike_rate": 25,
        "runs_per_match": 20,
        "runs_per_dismissal": 15,
        "dot_percentage": 15,
        "consistency": 25
    },
    "Volume_Focused": {
        "strike_rate": 20,
        "runs_per_match": 30,
        "runs_per_dismissal": 10,
        "dot_percentage": 10,
        "consistency": 30
    },
    "Efficiency_Focused": {
        "strike_rate": 30,
        "runs_per_match": 15,
        "runs_per_dismissal": 20,
        "dot_percentage": 20,
        "consistency": 15
    }
}

BOWLER_SCENARIOS = {
    "Baseline": {
        "wickets_per_100": 25,
        "economy": 20,
        "dot_percentage": 15,
        "consistency": 20,
        "wickets_per_match": 20
    },
    "Wicket_Impact": {
        "wickets_per_100": 35,
        "economy": 15,
        "dot_percentage": 10,
        "consistency": 15,
        "wickets_per_match": 25
    },
    "Control_Focused": {
        "wickets_per_100": 20,
        "economy": 25,
        "dot_percentage": 20,
        "consistency": 20,
        "wickets_per_match": 15
    }
}


# ============================================================
# 1. HELPER FUNCTIONS
# ============================================================

def percentile_score(series, higher_is_better=True):
    numeric = pd.to_numeric(series, errors="coerce")

    if higher_is_better:
        return numeric.rank(
            pct=True,
            method="average"
        ) * 100

    return (
        numeric.rank(
            pct=True,
            method="average",
            ascending=True
        )
        .rsub(1)
        .mul(100)
    )


def calculate_weighted_score(data, components, weights):
    weighted_sum = pd.Series(0.0, index=data.index)
    available_weight = pd.Series(0.0, index=data.index)

    for metric, weight in weights.items():
        values = data[components[metric]]
        valid = values.notna()

        weighted_sum.loc[valid] += (
            values.loc[valid] * weight
        )

        available_weight.loc[valid] += weight

    return np.where(
        available_weight > 0,
        weighted_sum / available_weight,
        np.nan
    )


def add_metric_percentiles(data, metric_directions):
    data = data.copy()

    for metric, higher_is_better in metric_directions.items():
        data[f"score_{metric}"] = percentile_score(
            data[metric],
            higher_is_better
        )

    return data


def rank_players(data, score_column):
    data = data.copy()

    data["final_rank"] = (
        data[score_column]
        .rank(
            ascending=False,
            method="min"
        )
        .astype(int)
    )

    return data


# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 75)
print("SUPERR SELECTOR - FINAL PRESSURE RANKING ENGINE")
print("=" * 75)

pressure = pd.read_csv(PRESSURE_FILE)
matches = pd.read_csv(MATCH_FILE)

batter_base = pd.read_csv(BATTER_FILE)
bowler_base = pd.read_csv(BOWLER_FILE)

required_bowler_columns = {
    "pressure_economy",
    "pressure_economy_scenario_b",
    "pressure_legal_balls",
    "pressure_wickets",
    "pressure_matches",
    "pressure_dot_percentage"
}

missing = required_bowler_columns - set(bowler_base.columns)

if missing:
    raise ValueError(
        f"Missing bowler columns: {sorted(missing)}. "
        "Run competition_performance.py first."
    )

metadata = matches[
    ["match_id", "match_format", "comp_name"]
].drop_duplicates("match_id")

pressure = pressure.merge(
    metadata,
    on="match_id",
    how="left",
    validate="many_to_one"
)

if pressure["match_format"].isna().any():
    raise ValueError("Unmatched delivery records found.")

print("\nINPUT VALIDATION")
print("All deliveries:", len(pressure))
print("Unique matches:", pressure["match_id"].nunique())
print("Pressure deliveries will be classified below.")


# ============================================================
# 3. CLEAN DATA
# ============================================================

numeric_columns = [
    "innings",
    "runs",
    "total_runs",
    "extras1_runs",
    "is_legal_ball",
    "ambiguous_extra",
    "is_wicket"
]

for column in numeric_columns:
    pressure[column] = pd.to_numeric(
        pressure[column],
        errors="coerce"
    ).fillna(0)

for column in [
    "striker_id",
    "bowler_id",
    "dismissed_player_id"
]:
    pressure[column] = pd.to_numeric(
        pressure[column],
        errors="coerce"
    )

pressure["extras_type_clean"] = (
    pressure["extras_type_clean"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
)

pressure["dismissal_type"] = (
    pressure["dismissal_type"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ============================================================
# 4. CLASSIFY PRESSURE DELIVERIES
# ============================================================

pressure_flag = (
    (
        (pressure["innings"] == 1) &
        pressure["first_innings_pressure"].isin(
            PRESSURE_CATEGORIES
        )
    ) |
    (
        (pressure["innings"] == 2) &
        pressure["chase_pressure"].isin(
            PRESSURE_CATEGORIES
        )
    )
)

pressure = pressure[pressure_flag].copy()

print("\nPRESSURE DATA")
print("Pressure deliveries:", len(pressure))
print("Pressure matches:", pressure["match_id"].nunique())

print(
    pressure.groupby("match_format")
    .size()
    .to_string()
)


# ============================================================
# 5. MATCH-LEVEL BATTER DATA
# ============================================================

excluded_batter_ball_types = [
    "wide",
    "overstep",
    "other",
    "penalty"
]

pressure["batter_ball_faced"] = (
    ~pressure["extras_type_clean"].isin(
        excluded_batter_ball_types
    )
).astype(int)

pressure["batter_runs"] = pressure["runs"]

pressure["batter_dismissed"] = (
    pressure["dismissed_player_id"].notna() &
    (
        pressure["dismissed_player_id"] ==
        pressure["striker_id"]
    )
).astype(int)

batter_match = (
    pressure.groupby(
        [
            "match_format",
            "striker_id",
            "striker_name",
            "match_id"
        ],
        dropna=False
    )
    .agg(
        match_pressure_runs=("batter_runs", "sum"),
        match_pressure_balls=("batter_ball_faced", "sum"),
        match_dismissals=("batter_dismissed", "sum")
    )
    .reset_index()
)

batter_match["match_strike_rate"] = np.where(
    batter_match["match_pressure_balls"] > 0,
    (
        batter_match["match_pressure_runs"] /
        batter_match["match_pressure_balls"]
    ) * 100,
    np.nan
)


# ============================================================
# 6. MATCH-LEVEL BOWLER DATA
# ============================================================

pressure["verified_legal_ball"] = (
    (pressure["is_legal_ball"] == 1) &
    (pressure["ambiguous_extra"] == 0)
).astype(int)

pressure["bowler_runs_conceded"] = (
    pressure["runs"] +
    np.where(
        pressure["extras_type_clean"].isin(
            ["wide", "overstep"]
        ),
        pressure["extras1_runs"],
        0
    )
)

pressure["credited_wicket"] = (
    (pressure["is_wicket"] == 1) &
    pressure["dismissal_type"].isin(
        CREDITED_WICKETS
    )
).astype(int)

bowler_match = (
    pressure.groupby(
        [
            "match_format",
            "bowler_id",
            "bowler_name",
            "match_id"
        ],
        dropna=False
    )
    .agg(
        match_runs_conceded=("bowler_runs_conceded", "sum"),
        match_legal_balls=("verified_legal_ball", "sum"),
        match_wickets=("credited_wicket", "sum")
    )
    .reset_index()
)

bowler_match["match_economy"] = np.where(
    bowler_match["match_legal_balls"] > 0,
    (
        bowler_match["match_runs_conceded"] /
        bowler_match["match_legal_balls"]
    ) * 6,
    np.nan
)


# ============================================================
# 7. BATTER CONSISTENCY
# ============================================================

batter_consistency = (
    batter_match.groupby(
        ["match_format", "striker_id", "striker_name"]
    )
    .agg(
        consistency_matches=("match_id", "nunique"),
        matches_10_plus=(
            "match_pressure_runs",
            lambda x: (x >= 10).sum()
        ),
        matches_20_plus=(
            "match_pressure_runs",
            lambda x: (x >= 20).sum()
        ),
        match_runs_std=("match_pressure_runs", "std"),
        average_match_strike_rate=(
            "match_strike_rate",
            "mean"
        )
    )
    .reset_index()
)

batter_consistency["matches_10_plus_pct"] = (
    batter_consistency["matches_10_plus"] /
    batter_consistency["consistency_matches"]
) * 100

batter_consistency["matches_20_plus_pct"] = (
    batter_consistency["matches_20_plus"] /
    batter_consistency["consistency_matches"]
) * 100

batter_consistency["consistency"] = (
    0.60 * batter_consistency["matches_10_plus_pct"] +
    0.40 * batter_consistency["matches_20_plus_pct"]
)


# ============================================================
# 8. BOWLER CONSISTENCY
# ============================================================

# Only count matches in which the bowler bowled at least
# one valid pressure legal delivery.
bowler_match = bowler_match[
    bowler_match["match_legal_balls"] > 0
].copy()

bowler_consistency = (
    bowler_match.groupby(
        ["match_format", "bowler_id", "bowler_name"]
    )
    .agg(
        consistency_matches=("match_id", "nunique"),
        matches_1_plus=(
            "match_wickets",
            lambda x: (x >= 1).sum()
        ),
        matches_2_plus=(
            "match_wickets",
            lambda x: (x >= 2).sum()
        ),
        match_wickets_std=("match_wickets", "std"),
        average_match_economy=("match_economy", "mean")
    )
    .reset_index()
)

bowler_consistency["matches_1_plus_pct"] = (
    bowler_consistency["matches_1_plus"] /
    bowler_consistency["consistency_matches"]
) * 100

bowler_consistency["matches_2_plus_pct"] = (
    bowler_consistency["matches_2_plus"] /
    bowler_consistency["consistency_matches"]
) * 100

bowler_consistency["consistency"] = (
    0.70 * bowler_consistency["matches_1_plus_pct"] +
    0.30 * bowler_consistency["matches_2_plus_pct"]
)


# ============================================================
# 9. MERGE PLAYER METRICS
# ============================================================

batters = batter_base.merge(
    batter_consistency,
    on=["match_format", "striker_id", "striker_name"],
    how="left",
    validate="one_to_one"
)

bowlers = bowler_base.merge(
    bowler_consistency,
    on=["match_format", "bowler_id", "bowler_name"],
    how="left",
    validate="one_to_one"
)

# Replace the original pressure-match count with the corrected
# count of matches containing at least one pressure legal ball.
bowlers["pressure_matches"] = (
    bowlers["consistency_matches"]
    .fillna(0)
    .astype(int)
)


# ============================================================
# 10. SAMPLE ELIGIBILITY
# ============================================================

batters["eligible"] = (
    (batters["pressure_balls"] >= MIN_BATTER_BALLS) &
    (batters["pressure_matches"] >= MIN_BATTER_MATCHES)
)

bowlers["eligible"] = (
    (bowlers["pressure_legal_balls"] >= MIN_BOWLER_BALLS) &
    (bowlers["pressure_matches"] >= MIN_BOWLER_MATCHES)
)


# ============================================================
# 11. BATTER METRICS
# ============================================================

batters["runs_per_match"] = (
    batters["pressure_runs"] /
    batters["pressure_matches"]
)

batters["runs_per_dismissal"] = np.where(
    batters["pressure_dismissals"] > 0,
    (
        batters["pressure_runs"] /
        batters["pressure_dismissals"]
    ),
    np.nan
)

batter_directions = {
    "pressure_strike_rate": True,
    "runs_per_match": True,
    "runs_per_dismissal": True,
    "pressure_dot_percentage": False,
    "consistency": True
}

batter_components = {
    "strike_rate": "score_pressure_strike_rate",
    "runs_per_match": "score_runs_per_match",
    "runs_per_dismissal": "score_runs_per_dismissal",
    "dot_percentage": "score_pressure_dot_percentage",
    "consistency": "score_consistency"
}


# ============================================================
# 12. BOWLER METRICS
# ============================================================

bowlers["wickets_per_100"] = np.where(
    bowlers["pressure_legal_balls"] > 0,
    (
        bowlers["pressure_wickets"] /
        bowlers["pressure_legal_balls"]
    ) * 100,
    np.nan
)

bowlers["wickets_per_match"] = (
    bowlers["pressure_wickets"] /
    bowlers["pressure_matches"]
)

bowler_directions = {
    "wickets_per_100": True,
    "pressure_economy": False,
    "pressure_dot_percentage": True,
    "consistency": True,
    "wickets_per_match": True
}

bowler_components = {
    "wickets_per_100": "score_wickets_per_100",
    "economy": "score_pressure_economy",
    "dot_percentage": "score_pressure_dot_percentage",
    "consistency": "score_consistency",
    "wickets_per_match": "score_wickets_per_match"
}


# ============================================================
# 13. FORMAT-WISE RANKINGS
# ============================================================

batter_results = []
bowler_results = []
accounting_comparison_results = []

for fmt in FORMATS:

    print("\n" + "=" * 75)
    print(f"RANKING ANALYSIS: {fmt}")
    print("=" * 75)

    # --------------------------------------------------------
    # BATTER RANKING
    # --------------------------------------------------------

    b = batters[
        (batters["match_format"] == fmt) &
        (batters["eligible"])
    ].copy()

    if b.empty:
        print("No eligible batters.")

    else:
        b = add_metric_percentiles(
            b,
            batter_directions
        )

        for scenario_name, weights in BATTER_SCENARIOS.items():
            b[f"score_{scenario_name}"] = calculate_weighted_score(
                b,
                batter_components,
                weights
            )

        b["final_score"] = b["score_Baseline"]

        b = rank_players(b, "final_score")

        scenario_top10 = {}

        for scenario_name in BATTER_SCENARIOS:
            scenario_top10[scenario_name] = set(
                b.nlargest(
                    10,
                    f"score_{scenario_name}"
                )["striker_id"]
            )

        b["top10_scenario_count"] = b["striker_id"].apply(
            lambda player_id: sum(
                player_id in selected
                for selected in scenario_top10.values()
            )
        )

        batter_results.append(b)

        print("\nBATTER BASELINE TOP 10")

        print(
            b.sort_values("final_rank")[
                [
                    "final_rank",
                    "striker_name",
                    "pressure_runs",
                    "pressure_balls",
                    "pressure_strike_rate",
                    "pressure_dismissals",
                    "pressure_matches",
                    "consistency",
                    "final_score",
                    "top10_scenario_count"
                ]
            ].head(10).round(2).to_string(index=False)
        )

    # --------------------------------------------------------
    # BOWLER SCENARIO A
    # --------------------------------------------------------

    w = bowlers[
        (bowlers["match_format"] == fmt) &
        (bowlers["eligible"])
    ].copy()

    if w.empty:
        print("No eligible bowlers.")

    else:
        # Scenario A uses existing provisional economy.
        w_a = w.copy()

        w_a = add_metric_percentiles(
            w_a,
            bowler_directions
        )

        for scenario_name, weights in BOWLER_SCENARIOS.items():
            w_a[f"score_{scenario_name}"] = calculate_weighted_score(
                w_a,
                bowler_components,
                weights
            )

        w_a["final_score"] = w_a["score_Baseline"]

        w_a = rank_players(w_a, "final_score")

        scenario_top10 = {}

        for scenario_name in BOWLER_SCENARIOS:
            scenario_top10[scenario_name] = set(
                w_a.nlargest(
                    10,
                    f"score_{scenario_name}"
                )["bowler_id"]
            )

        w_a["top10_scenario_count"] = w_a["bowler_id"].apply(
            lambda player_id: sum(
                player_id in selected
                for selected in scenario_top10.values()
            )
        )

        # ----------------------------------------------------
        # BOWLER SCENARIO B
        # ----------------------------------------------------

        w_b = w.copy()

        w_b["pressure_economy"] = (
            w_b["pressure_economy_scenario_b"]
        )

        w_b = add_metric_percentiles(
            w_b,
            bowler_directions
        )

        w_b["score_Baseline"] = calculate_weighted_score(
            w_b,
            bowler_components,
            BOWLER_SCENARIOS["Baseline"]
        )

        w_b = rank_players(
            w_b,
            "score_Baseline"
        )

        # ----------------------------------------------------
        # ACCOUNTING COMPARISON
        # ----------------------------------------------------

        comparison = w_a[
            [
                "match_format",
                "bowler_id",
                "bowler_name",
                "pressure_legal_balls",
                "pressure_wickets",
                "pressure_economy",
                "final_score",
                "final_rank"
            ]
        ].merge(
            w_b[
                [
                    "bowler_id",
                    "pressure_economy",
                    "final_rank",
                    "score_Baseline"
                ]
            ],
            on="bowler_id",
            how="inner",
            validate="one_to_one",
            suffixes=("_scenario_a", "_scenario_b")
        )

        comparison["rank_change_b_minus_a"] = (
            comparison["final_rank_scenario_b"] -
            comparison["final_rank_scenario_a"]
        )

        comparison["top10_scenario_a"] = (
            comparison["final_rank_scenario_a"] <= 10
        )

        comparison["top10_scenario_b"] = (
            comparison["final_rank_scenario_b"] <= 10
        )

        comparison["top10_status_changed"] = (
            comparison["top10_scenario_a"] !=
            comparison["top10_scenario_b"]
        )

        accounting_comparison_results.append(comparison)

        bowler_results.append(w_a)

        # ----------------------------------------------------
        # PRINT BOWLER RANKING RESULTS
        # ----------------------------------------------------

        print("\nBOWLER SCENARIO A BASELINE TOP 10")

        print(
            w_a.sort_values("final_rank")[
                [
                    "final_rank",
                    "bowler_name",
                    "pressure_wickets",
                    "pressure_legal_balls",
                    "pressure_economy",
                    "pressure_dot_percentage",
                    "pressure_matches",
                    "consistency",
                    "final_score",
                    "top10_scenario_count"
                ]
            ].head(10).round(2).to_string(index=False)
        )

        overlap = int(
            (
                comparison["top10_scenario_a"] &
                comparison["top10_scenario_b"]
            ).sum()
        )

        changes = int(
            comparison["top10_status_changed"].sum()
        )

        print("\nACCOUNTING SENSITIVITY")
        print("Scenario A vs B Top 10 overlap:", overlap, "/ 10")
        print("Players whose Top 10 membership changed:", changes)

        print("\nLargest rank movements:")

        print(
            comparison.assign(
                absolute_rank_change=lambda x:
                x["rank_change_b_minus_a"].abs()
            )
            .sort_values(
                "absolute_rank_change",
                ascending=False
            )[
                [
                    "bowler_name",
                    "final_rank_scenario_a",
                    "final_rank_scenario_b",
                    "rank_change_b_minus_a"
                ]
            ]
            .head(10)
            .to_string(index=False)
        )


# ============================================================
# 14. SAVE COMPLETE RANKINGS
# ============================================================

if not batter_results:
    raise ValueError("No batter rankings generated.")

if not bowler_results:
    raise ValueError("No bowler rankings generated.")

batter_rankings = pd.concat(
    batter_results,
    ignore_index=True
)

bowler_rankings = pd.concat(
    bowler_results,
    ignore_index=True
)

batter_rankings = batter_rankings.sort_values(
    ["match_format", "final_rank"]
)

bowler_rankings = bowler_rankings.sort_values(
    ["match_format", "final_rank"]
)

batter_rankings.to_csv(
    OUTPUT_DIR / "final_batter_rankings.csv",
    index=False
)

bowler_rankings.to_csv(
    OUTPUT_DIR / "final_bowler_rankings.csv",
    index=False
)


# ============================================================
# 15. SAVE TOP 10 SHORTLISTS
# ============================================================

batter_top10 = batter_rankings[
    batter_rankings["final_rank"] <= 10
].copy()

bowler_top10 = bowler_rankings[
    bowler_rankings["final_rank"] <= 10
].copy()

batter_top10.to_csv(
    OUTPUT_DIR / "top10_batters_by_format.csv",
    index=False
)

bowler_top10.to_csv(
    OUTPUT_DIR / "top10_bowlers_by_format.csv",
    index=False
)


# ============================================================
# 16. SAVE BOWLER ACCOUNTING SENSITIVITY
# ============================================================

if not accounting_comparison_results:
    raise ValueError("No accounting sensitivity results generated.")

accounting_comparison = pd.concat(
    accounting_comparison_results,
    ignore_index=True
)

accounting_comparison = accounting_comparison.sort_values(
    ["match_format", "final_rank_scenario_a"]
)

accounting_comparison.to_csv(
    OUTPUT_DIR / "bowler_accounting_sensitivity.csv",
    index=False
)


# ============================================================
# 17. SAVE EXISTING WEIGHT SENSITIVITY
# ============================================================

sensitivity_rows = []

for fmt in FORMATS:

    b = batter_rankings[
        batter_rankings["match_format"] == fmt
    ]

    w = bowler_rankings[
        bowler_rankings["match_format"] == fmt
    ]

    for scenario in BATTER_SCENARIOS:

        top = set(
            b.nlargest(
                10,
                f"score_{scenario}"
            )["striker_id"]
        )

        baseline = set(
            b.nlargest(
                10,
                "score_Baseline"
            )["striker_id"]
        )

        sensitivity_rows.append({
            "format": fmt,
            "player_type": "Batter",
            "scenario": scenario,
            "top10_overlap_with_baseline": len(
                top.intersection(baseline)
            )
        })

    for scenario in BOWLER_SCENARIOS:

        top = set(
            w.nlargest(
                10,
                f"score_{scenario}"
            )["bowler_id"]
        )

        baseline = set(
            w.nlargest(
                10,
                "score_Baseline"
            )["bowler_id"]
        )

        sensitivity_rows.append({
            "format": fmt,
            "player_type": "Bowler",
            "scenario": scenario,
            "top10_overlap_with_baseline": len(
                top.intersection(baseline)
            )
        })

sensitivity = pd.DataFrame(sensitivity_rows)

sensitivity.to_csv(
    OUTPUT_DIR / "ranking_sensitivity_analysis.csv",
    index=False
)


# ============================================================
# 18. METHODOLOGY REPORT
# ============================================================

report_path = OUTPUT_DIR / "ranking_methodology.txt"

with open(report_path, "w", encoding="utf-8") as report:

    report.write(
        "SUPERR SELECTOR - PRESSURE PERFORMANCE RANKING METHODOLOGY\n"
    )

    report.write("=" * 75 + "\n\n")

    report.write("1. COMPETITION SEGMENTATION\n")
    report.write(
        "T20 and T20I are ranked independently.\n\n"
    )

    report.write("2. PRESSURE DEFINITION\n")
    report.write(
        "Only Moderate, High and Extreme pressure deliveries "
        "are included. First innings uses first_innings_pressure; "
        "second innings uses chase_pressure.\n\n"
    )

    report.write("3. SAMPLE ELIGIBILITY\n")
    report.write(
        f"Batters: minimum {MIN_BATTER_BALLS} pressure balls "
        f"and {MIN_BATTER_MATCHES} pressure matches.\n"
    )

    report.write(
        f"Bowlers: minimum {MIN_BOWLER_BALLS} pressure legal balls "
        f"and {MIN_BOWLER_MATCHES} pressure matches.\n\n"
    )

    report.write("4. BATTER BASELINE WEIGHTS\n")

    for metric, weight in BATTER_SCENARIOS["Baseline"].items():
        report.write(f"{metric}: {weight}%\n")

    report.write("\n5. BOWLER BASELINE WEIGHTS\n")

    for metric, weight in BOWLER_SCENARIOS["Baseline"].items():
        report.write(f"{metric}: {weight}%\n")

    report.write(
        "\n6. NORMALIZATION\n"
        "Metrics are converted to percentile scores within "
        "eligible players of the same format. Lower-is-better "
        "metrics are reverse-ranked. Missing components are "
        "excluded and remaining weights are renormalized.\n"
    )

    report.write(
        "\n7. BATTER CONSISTENCY\n"
        "60% of the percentage of pressure matches with 10+ runs "
        "and 40% of the percentage with 20+ runs.\n"
    )

    report.write(
        "\n8. BOWLER CONSISTENCY\n"
        "Only matches containing at least one valid pressure "
        "legal delivery are included. Consistency is calculated "
        "as 70% of the percentage of these matches with 1+ "
        "credited wicket and 30% of the percentage with 2+ "
        "credited wickets. The same corrected match count is "
        "used for bowler match eligibility and wickets per match.\n"
    )

    report.write(
        "\n9. BOWLER WICKET CREDIT\n"
        "Bowled, Caught, LBW, Stump and Hit Wicket are credited "
        "to bowlers. Run-outs and other non-bowler dismissals "
        "are excluded.\n"
    )

    report.write(
        "\n10. BOWLER EXTRAS ACCOUNTING\n"
        "Scenario A: Batter runs plus extras1 for wides and "
        "oversteps. Unverified extras_2_runs and other extras "
        "are not charged.\n"
        "Scenario B: Scenario A plus extras_2_runs on oversteps. "
        "This is a sensitivity test, not a verified official "
        "scoring interpretation.\n"
    )

    report.write(
        "\n11. WEIGHT SENSITIVITY\n"
        "Baseline rankings are compared against volume-focused, "
        "efficiency-focused, wicket-impact and control-focused "
        "alternative weighting scenarios.\n"
    )

    report.write(
        "\n12. INTERPRETATION LIMITATIONS\n"
        "This is a project-defined analytical model, not an "
        "official Rajasthan Royals selection formula. "
        "Pressure definitions, delivery classification, "
        "sample thresholds and weights are project assumptions. "
        "The source does not define extras_2_runs sufficiently "
        "to establish its bowler-accounting treatment.\n"
    )


# ============================================================
# 19. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("RANKING ENGINE COMPLETED")
print("=" * 75)

print("\nOUTPUT FILES")

output_files = [
    "final_batter_rankings.csv",
    "final_bowler_rankings.csv",
    "top10_batters_by_format.csv",
    "top10_bowlers_by_format.csv",
    "ranking_sensitivity_analysis.csv",
    "bowler_accounting_sensitivity.csv",
    "ranking_methodology.txt"
]

for filename in output_files:
    print(f"outputs/{filename}")

print("\nACCOUNTING SENSITIVITY SUMMARY")

print(
    accounting_comparison.groupby("match_format").agg(
        eligible_bowlers=("bowler_id", "nunique"),
        top10_membership_changes=("top10_status_changed", "sum"),
        maximum_absolute_rank_change=(
            "rank_change_b_minus_a",
            lambda x: x.abs().max()
        )
    ).to_string()
)

print("\nIMPORTANT:")
print("Scenario A remains the provisional baseline ranking.")
print("Scenario B is an alternative accounting sensitivity test.")
print("Neither is claimed to be the official source scoring formula.")

print("\n" + "=" * 75)
print("SUPERR SELECTOR RANKING ENGINE FINISHED")
print("=" * 75)
