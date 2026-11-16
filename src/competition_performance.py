
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# SUPERR SELECTOR - COMPETITION-WISE PLAYER PERFORMANCE ENGINE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PRESSURE_FILE = PROCESSED_DIR / "pressure_classified.csv"
MATCH_FILE = PROCESSED_DIR / "target_matches.csv"

FORMATS = ["T20", "T20I"]

PRESSURE_CATEGORIES = ["Moderate", "High", "Extreme"]

BATTER_EXCLUDED_BALL_TYPES = [
    "wide", "overstep", "other", "penalty"
]

BOWLER_CREDITED_DISMISSALS = [
    "Bowled", "Caught", "LBW", "Stump", "Hit Wicket"
]


def load_data():
    print("=" * 75)
    print("SUPERR SELECTOR - COMPETITION PERFORMANCE ENGINE")
    print("=" * 75)

    df = pd.read_csv(PRESSURE_FILE)
    matches = pd.read_csv(MATCH_FILE)

    print("\nLoaded deliveries:", len(df))
    print("Loaded target matches:", len(matches))

    required_delivery_columns = [
        "match_id", "innings", "runs", "total_runs",
        "extras1_runs", "extras_2_runs", "extras_type_clean",
        "is_four", "is_six", "is_wicket", "is_legal_ball",
        "ambiguous_extra", "striker_id", "striker_name",
        "bowler_id", "bowler_name", "dismissed_player_id",
        "dismissal_type", "first_innings_pressure", "chase_pressure"
    ]

    required_match_columns = [
        "match_id", "comp_name", "match_format",
        "season", "has_ball_data"
    ]

    missing_delivery = set(required_delivery_columns) - set(df.columns)
    missing_match = set(required_match_columns) - set(matches.columns)

    if missing_delivery:
        raise ValueError(
            f"Missing delivery columns: {sorted(missing_delivery)}"
        )

    if missing_match:
        raise ValueError(
            f"Missing match columns: {sorted(missing_match)}"
        )

    metadata = matches[required_match_columns].drop_duplicates(
        subset=["match_id"]
    )

    df = df.merge(
        metadata,
        on="match_id",
        how="left",
        validate="many_to_one"
    )

    if df["match_format"].isna().any():
        raise ValueError("Some deliveries have unmatched match metadata.")

    print("\nMATCH COVERAGE")
    print(
        df.groupby("match_format")["match_id"]
        .nunique()
        .to_string()
    )

    return df


def clean_data(df):
    numeric_columns = [
        "innings", "runs", "total_runs",
        "extras1_runs", "extras_2_runs",
        "is_four", "is_six", "is_wicket",
        "is_legal_ball", "ambiguous_extra"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

    for col in [
        "striker_id",
        "bowler_id",
        "dismissed_player_id"
    ]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df["extras_type_clean"] = (
        df["extras_type_clean"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["dismissal_type"] = (
        df["dismissal_type"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return df


def classify_pressure(df):
    first_innings = (
        (df["innings"] == 1) &
        df["first_innings_pressure"].isin(PRESSURE_CATEGORIES)
    )

    second_innings = (
        (df["innings"] == 2) &
        df["chase_pressure"].isin(PRESSURE_CATEGORIES)
    )

    pressure_df = df[first_innings | second_innings].copy()

    print("\nPRESSURE CLASSIFICATION")
    print("Pressure deliveries:", len(pressure_df))
    print("Pressure matches:", pressure_df["match_id"].nunique())

    print("\nPressure deliveries by format:")
    print(pressure_df.groupby("match_format").size().to_string())

    return pressure_df


def engineer_batter_metrics(df):
    df["batter_ball_faced"] = (
        ~df["extras_type_clean"].isin(
            BATTER_EXCLUDED_BALL_TYPES
        )
    ).astype(int)

    df["batter_dot"] = (
        (df["batter_ball_faced"] == 1) &
        (df["runs"] == 0)
    ).astype(int)

    df["batter_runs"] = df["runs"]

    df["batter_dismissed"] = (
        df["dismissed_player_id"].notna() &
        (df["dismissed_player_id"] == df["striker_id"])
    ).astype(int)

    return df


def engineer_bowler_metrics(df):
    # Scenario A: Current provisional accounting.
    # Batter runs + extras1 on wides and oversteps.
    # extras_2_runs and "other" extras remain uncharged
    # because their meanings are not verified in the source.

    df["bowler_runs_conceded"] = (
        df["runs"] +
        np.where(
            df["extras_type_clean"].isin(["wide", "overstep"]),
            df["extras1_runs"],
            0
        )
    )

    # Scenario B: Sensitivity test only.
    # Additionally includes extras_2_runs on oversteps.
    # This is not assumed to be official scoring treatment.

    df["bowler_runs_conceded_scenario_b"] = (
        df["bowler_runs_conceded"] +
        np.where(
            df["extras_type_clean"] == "overstep",
            df["extras_2_runs"],
            0
        )
    )

    df["verified_legal_ball"] = (
        (df["is_legal_ball"] == 1) &
        (df["ambiguous_extra"] == 0)
    ).astype(int)

    # Bowler dot: legal delivery with zero total runs.
    df["bowler_dot"] = (
        (df["verified_legal_ball"] == 1) &
        (df["total_runs"] == 0)
    ).astype(int)

    df["bowler_wicket"] = (
        (df["is_wicket"] == 1) &
        df["dismissal_type"].isin(
            BOWLER_CREDITED_DISMISSALS
        )
    ).astype(int)

    return df


def aggregate_batters(df):
    group_columns = [
        "match_format",
        "striker_id",
        "striker_name"
    ]

    batters = (
        df.groupby(group_columns, dropna=False)
        .agg(
            pressure_runs=("batter_runs", "sum"),
            pressure_balls=("batter_ball_faced", "sum"),
            pressure_fours=("is_four", "sum"),
            pressure_sixes=("is_six", "sum"),
            pressure_deliveries=("match_id", "size"),
            pressure_dot_balls=("batter_dot", "sum"),
            pressure_matches=("match_id", "nunique")
        )
        .reset_index()
    )

    dismissals = (
        df[
            df["dismissed_player_id"].notna() &
            (df["dismissed_player_id"] == df["striker_id"])
        ]
        .groupby(["match_format", "striker_id"])
        .size()
        .reset_index(name="pressure_dismissals")
    )

    batters = batters.merge(
        dismissals,
        on=["match_format", "striker_id"],
        how="left",
        validate="one_to_one"
    )

    batters["pressure_dismissals"] = (
        batters["pressure_dismissals"]
        .fillna(0)
        .astype(int)
    )

    batters["pressure_strike_rate"] = np.where(
        batters["pressure_balls"] > 0,
        batters["pressure_runs"] /
        batters["pressure_balls"] * 100,
        np.nan
    )

    batters["pressure_dot_percentage"] = np.where(
        batters["pressure_balls"] > 0,
        batters["pressure_dot_balls"] /
        batters["pressure_balls"] * 100,
        np.nan
    )

    batters["pressure_boundary_runs"] = (
        batters["pressure_fours"] * 4 +
        batters["pressure_sixes"] * 6
    )

    batters["pressure_runs_per_match"] = np.where(
        batters["pressure_matches"] > 0,
        batters["pressure_runs"] /
        batters["pressure_matches"],
        np.nan
    )

    batters["pressure_runs_per_dismissal"] = np.where(
        batters["pressure_dismissals"] > 0,
        batters["pressure_runs"] /
        batters["pressure_dismissals"],
        np.nan
    )

    return batters


def aggregate_bowlers(df):
    group_columns = [
        "match_format",
        "bowler_id",
        "bowler_name"
    ]

    bowlers = (
        df.groupby(group_columns, dropna=False)
        .agg(
            pressure_runs_conceded=("bowler_runs_conceded", "sum"),
            pressure_runs_conceded_scenario_b=(
                "bowler_runs_conceded_scenario_b", "sum"
            ),
            pressure_legal_balls=("verified_legal_ball", "sum"),
            pressure_wickets=("bowler_wicket", "sum"),
            pressure_dot_balls=("bowler_dot", "sum"),
            pressure_deliveries=("match_id", "size"),
            pressure_matches=("match_id", "nunique")
        )
        .reset_index()
    )

    bowlers["pressure_overs"] = (
        bowlers["pressure_legal_balls"] / 6
    )

    bowlers["pressure_economy"] = np.where(
        bowlers["pressure_legal_balls"] > 0,
        bowlers["pressure_runs_conceded"] /
        bowlers["pressure_legal_balls"] * 6,
        np.nan
    )

    bowlers["pressure_economy_scenario_b"] = np.where(
        bowlers["pressure_legal_balls"] > 0,
        bowlers["pressure_runs_conceded_scenario_b"] /
        bowlers["pressure_legal_balls"] * 6,
        np.nan
    )

    bowlers["pressure_dot_percentage"] = np.where(
        bowlers["pressure_legal_balls"] > 0,
        bowlers["pressure_dot_balls"] /
        bowlers["pressure_legal_balls"] * 100,
        np.nan
    )

    bowlers["pressure_wickets_per_match"] = np.where(
        bowlers["pressure_matches"] > 0,
        bowlers["pressure_wickets"] /
        bowlers["pressure_matches"],
        np.nan
    )

    bowlers["pressure_wickets_per_100_balls"] = np.where(
        bowlers["pressure_legal_balls"] > 0,
        bowlers["pressure_wickets"] /
        bowlers["pressure_legal_balls"] * 100,
        np.nan
    )

    return bowlers


def validate_outputs(batters, bowlers):
    checks = {
        "Batter dots <= balls": (
            batters["pressure_dot_balls"] <=
            batters["pressure_balls"]
        ).all(),

        "Bowler dots <= legal balls": (
            bowlers["pressure_dot_balls"] <=
            bowlers["pressure_legal_balls"]
        ).all(),

        "Non-negative batter runs": (
            batters["pressure_runs"] >= 0
        ).all(),

        "Non-negative bowler runs": (
            bowlers["pressure_runs_conceded"] >= 0
        ).all(),

        "Non-negative bowler wickets": (
            bowlers["pressure_wickets"] >= 0
        ).all(),

        "Unique batter IDs per format": (
            batters.duplicated(
                ["match_format", "striker_id"]
            ).sum() == 0
        ),

        "Unique bowler IDs per format": (
            bowlers.duplicated(
                ["match_format", "bowler_id"]
            ).sum() == 0
        ),

        "No missing batter IDs": (
            batters["striker_id"].notna().all()
        ),

        "No missing bowler IDs": (
            bowlers["bowler_id"].notna().all()
        ),

        "Scenario B economy is not below Scenario A": (
            (
                bowlers["pressure_economy_scenario_b"] +
                1e-9 >= bowlers["pressure_economy"]
            ).all()
        )
    }

    print("\n" + "=" * 75)
    print("VALIDATION CHECKS")
    print("=" * 75)

    for name, passed in checks.items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")

    if not all(checks.values()):
        raise ValueError(
            "Validation failed. Do not use these performance tables."
        )


def print_top_performers(batters, bowlers):
    for fmt in FORMATS:
        print("\n" + "=" * 75)
        print(f"{fmt} - TOP PRESSURE BATTERS BY RUNS")
        print("=" * 75)

        top_batters = (
            batters[batters["match_format"] == fmt]
            .sort_values(
                ["pressure_runs", "pressure_strike_rate"],
                ascending=[False, False]
            )
            .head(10)
        )

        print(
            top_batters[
                [
                    "striker_name",
                    "pressure_runs",
                    "pressure_balls",
                    "pressure_strike_rate",
                    "pressure_dismissals",
                    "pressure_matches"
                ]
            ].round(2).to_string(index=False)
        )

        print("\n" + "=" * 75)
        print(f"{fmt} - TOP PRESSURE BOWLERS BY WICKETS")
        print("=" * 75)

        top_bowlers = (
            bowlers[bowlers["match_format"] == fmt]
            .sort_values(
                ["pressure_wickets", "pressure_economy"],
                ascending=[False, True]
            )
            .head(10)
        )

        print(
            top_bowlers[
                [
                    "bowler_name",
                    "pressure_wickets",
                    "pressure_legal_balls",
                    "pressure_economy",
                    "pressure_economy_scenario_b",
                    "pressure_dot_percentage",
                    "pressure_matches"
                ]
            ].round(2).to_string(index=False)
        )


def main():
    df = load_data()
    df = clean_data(df)

    pressure_df = classify_pressure(df)

    if pressure_df.empty:
        raise ValueError("No pressure deliveries found.")

    pressure_df = engineer_batter_metrics(pressure_df)
    pressure_df = engineer_bowler_metrics(pressure_df)

    batters = aggregate_batters(pressure_df)
    bowlers = aggregate_bowlers(pressure_df)

    validate_outputs(batters, bowlers)

    batter_output = (
        PROCESSED_DIR / "competition_batter_performance.csv"
    )

    bowler_output = (
        PROCESSED_DIR / "competition_bowler_performance.csv"
    )

    batters.to_csv(batter_output, index=False)
    bowlers.to_csv(bowler_output, index=False)

    print_top_performers(batters, bowlers)

    print("\n" + "=" * 75)
    print("COMPETITION PERFORMANCE ENGINE COMPLETED")
    print("=" * 75)

    print("\nSaved:")
    print(batter_output)
    print(bowler_output)

    print("\nBatter records:", len(batters))
    print("Bowler records:", len(bowlers))

    print("\nBowler accounting scenarios:")
    print("Scenario A: Current provisional accounting.")
    print("Scenario B: Scenario A + overstep extras_2_runs.")
    print("Scenario B is sensitivity analysis, not verified official scoring.")


if __name__ == "__main__":
    main()
