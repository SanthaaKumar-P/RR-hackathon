
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# SUPERR SELECTOR - PLAYER PERFORMANCE ENGINE
# ============================================================

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "processed"

INPUT_FILE = DATA / "pressure_classified.csv"
BATTER_OUTPUT = DATA / "batter_performance.csv"
BOWLER_OUTPUT = DATA / "bowler_performance.csv"

print("=" * 70)
print("SUPERR SELECTOR - PLAYER PERFORMANCE ENGINE")
print("=" * 70)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)


# ============================================================
# 1. REQUIRED COLUMNS
# ============================================================

required_columns = [
    "match_id", "striker_id", "striker_name",
    "bowler_id", "bowler_name",
    "runs", "total_runs",
    "extras1_runs", "extras_2_runs",
    "is_four", "is_six", "is_wicket",
    "is_legal_ball", "ambiguous_extra",
    "extras_type_clean", "dismissal_type",
    "dismissed_player_id",
    "first_innings_pressure", "chase_pressure"
]

missing = [c for c in required_columns if c not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")


# ============================================================
# 2. DATA CLEANING
# ============================================================

for col in [
    "runs", "total_runs",
    "extras1_runs", "extras_2_runs"
]:
    df[col] = pd.to_numeric(
        df[col], errors="coerce"
    ).fillna(0)


def convert_bool(series):
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)

    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(0).ne(0)

    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes"])
    )


for col in [
    "is_four", "is_six", "is_wicket",
    "is_legal_ball", "ambiguous_extra"
]:
    df[col] = convert_bool(df[col])


df["extras_type_clean"] = (
    df["extras_type_clean"]
    .fillna("normal")
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

for col in [
    "striker_id", "bowler_id", "dismissed_player_id"
]:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# ============================================================
# 3. PRESSURE FLAG
# ============================================================

df["pressure_flag"] = (
    df["first_innings_pressure"].isin(["High", "Extreme"])
    |
    df["chase_pressure"].isin(["High", "Extreme"])
)


# ============================================================
# 4. VERIFIED LEGAL BALLS AND BATTER BALLS
# ============================================================

# Provisional conservative classification.
# Exclude wide, overstep, ambiguous and penalty deliveries.

df["verified_legal_ball"] = (
    df["is_legal_ball"]
    &
    (~df["ambiguous_extra"])
    &
    (~df["extras_type_clean"].isin(
        ["wide", "overstep", "other", "penalty"]
    ))
)

# Byes and leg-byes count as balls faced.
df["batter_ball_faced"] = df["verified_legal_ball"]


# ============================================================
# 5. BOWLER RUNS CONCEDED
# ============================================================

# Provisional calculation:
# Batter runs + wide extras + overstep extras.
# Byes and leg-byes are not charged.
# Ambiguous other and penalty extras are excluded.
# Additional no-ball extras require verification.

df["bowler_runs_conceded"] = (
    df["runs"]
    +
    np.where(
        df["extras_type_clean"] == "wide",
        df["extras1_runs"], 0
    )
    +
    np.where(
        df["extras_type_clean"] == "overstep",
        df["extras1_runs"], 0
    )
)


# ============================================================
# 6. BOWLER-CREDITED WICKETS
# ============================================================

bowler_wicket_types = [
    "Bowled",
    "Caught",
    "LBW",
    "Stump",
    "Hit Wicket"
]

df["bowler_wicket"] = (
    df["is_wicket"]
    &
    df["dismissal_type"].isin(bowler_wicket_types)
)


# ============================================================
# 7. CREATE PRESSURE DATAFRAME
# IMPORTANT: CREATE AFTER ALL FEATURE COLUMNS
# ============================================================

pressure_df = df.loc[
    df["pressure_flag"]
].copy()

# Confirm that every required feature exists.
feature_columns = [
    "batter_ball_faced",
    "verified_legal_ball",
    "bowler_runs_conceded",
    "bowler_wicket"
]

for col in feature_columns:
    if col not in pressure_df.columns:
        raise RuntimeError(
            f"Missing {col} in pressure dataframe."
        )


# ============================================================
# 8. BATTER AGGREGATION
# ============================================================

def aggregate_batter(data, suffix):

    result = data.groupby(
        ["striker_id", "striker_name"],
        dropna=False
    ).agg(
        runs=("runs", "sum"),
        balls_faced=("batter_ball_faced", "sum"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum"),
        deliveries=("match_id", "size")
    ).reset_index()

    result = result.rename(columns={
        "runs": f"{suffix}_runs",
        "balls_faced": f"{suffix}_balls",
        "fours": f"{suffix}_fours",
        "sixes": f"{suffix}_sixes",
        "deliveries": f"{suffix}_deliveries"
    })

    result[f"{suffix}_strike_rate"] = np.where(
        result[f"{suffix}_balls"] > 0,
        result[f"{suffix}_runs"] * 100 /
        result[f"{suffix}_balls"],
        np.nan
    )

    return result


# ============================================================
# 9. BOWLER AGGREGATION
# ============================================================

def aggregate_bowler(data, suffix):

    work = data.copy()

    # Only verified legal zero-total-run deliveries
    # count as bowling dot balls.
    work["verified_dot_ball"] = (
        work["verified_legal_ball"]
        &
        (work["total_runs"] == 0)
    )

    result = work.groupby(
        ["bowler_id", "bowler_name"],
        dropna=False
    ).agg(
        runs_conceded=("bowler_runs_conceded", "sum"),
        legal_balls=("verified_legal_ball", "sum"),
        wickets=("bowler_wicket", "sum"),
        dots=("verified_dot_ball", "sum"),
        deliveries=("match_id", "size")
    ).reset_index()

    result = result.rename(columns={
        "runs_conceded": f"{suffix}_runs_conceded",
        "legal_balls": f"{suffix}_legal_balls",
        "wickets": f"{suffix}_wickets",
        "dots": f"{suffix}_dot_balls",
        "deliveries": f"{suffix}_deliveries"
    })

    result[f"{suffix}_overs"] = (
        result[f"{suffix}_legal_balls"] / 6
    )

    result[f"{suffix}_economy"] = np.where(
        result[f"{suffix}_legal_balls"] > 0,
        result[f"{suffix}_runs_conceded"] * 6 /
        result[f"{suffix}_legal_balls"],
        np.nan
    )

    result[f"{suffix}_dot_percentage"] = np.where(
        result[f"{suffix}_legal_balls"] > 0,
        result[f"{suffix}_dot_balls"] * 100 /
        result[f"{suffix}_legal_balls"],
        np.nan
    )

    return result


# ============================================================
# 10. OVERALL AND PRESSURE BATTER PERFORMANCE
# ============================================================

bat_all = aggregate_batter(df, "overall")

bat_pressure = aggregate_batter(
    pressure_df, "pressure"
)


# ============================================================
# 11. BATTER DISMISSALS
# ============================================================

dismissals = df.loc[
    df["is_wicket"]
    &
    df["dismissed_player_id"].notna()
].copy()

dismissal_overall = (
    dismissals.groupby("dismissed_player_id")
    .size()
    .rename("overall_dismissals")
    .reset_index()
)

dismissal_pressure = (
    dismissals.loc[dismissals["pressure_flag"]]
    .groupby("dismissed_player_id")
    .size()
    .rename("pressure_dismissals")
    .reset_index()
)


# ============================================================
# 12. MERGE BATTER PERFORMANCE
# ============================================================

bat_all = bat_all.merge(
    dismissal_overall,
    left_on="striker_id",
    right_on="dismissed_player_id",
    how="left"
).drop(columns=["dismissed_player_id"])

bat_pressure = bat_pressure.merge(
    dismissal_pressure,
    left_on="striker_id",
    right_on="dismissed_player_id",
    how="left"
).drop(columns=["dismissed_player_id"])

batters = bat_all.merge(
    bat_pressure,
    on=["striker_id", "striker_name"],
    how="left"
)

for col in [
    "overall_dismissals",
    "pressure_runs",
    "pressure_balls",
    "pressure_fours",
    "pressure_sixes",
    "pressure_deliveries",
    "pressure_dismissals"
]:
    batters[col] = batters[col].fillna(0)


# ============================================================
# 13. BATTER DOT BALLS AND BOUNDARIES
# ============================================================

# Batter dot = zero batter runs on a ball faced.
# A bye or leg-bye is zero batter runs but not a
# zero-total-run delivery.

overall_dots = (
    df.loc[
        df["batter_ball_faced"]
        &
        (df["runs"] == 0)
    ]
    .groupby("striker_id")
    .size()
)

pressure_dots = (
    pressure_df.loc[
        pressure_df["batter_ball_faced"]
        &
        (pressure_df["runs"] == 0)
    ]
    .groupby("striker_id")
    .size()
)

batters["overall_dot_balls"] = (
    batters["striker_id"].map(overall_dots).fillna(0)
)

batters["pressure_dot_balls"] = (
    batters["striker_id"].map(pressure_dots).fillna(0)
)

batters["overall_dot_percentage"] = np.where(
    batters["overall_balls"] > 0,
    batters["overall_dot_balls"] * 100 /
    batters["overall_balls"],
    np.nan
)

batters["pressure_dot_percentage"] = np.where(
    batters["pressure_balls"] > 0,
    batters["pressure_dot_balls"] * 100 /
    batters["pressure_balls"],
    np.nan
)

batters["overall_boundary_runs"] = (
    batters["overall_fours"] * 4
    +
    batters["overall_sixes"] * 6
)

batters["pressure_boundary_runs"] = (
    batters["pressure_fours"] * 4
    +
    batters["pressure_sixes"] * 6
)


# ============================================================
# 14. OVERALL AND PRESSURE BOWLER PERFORMANCE
# ============================================================

bowl_all = aggregate_bowler(df, "overall")

bowl_pressure = aggregate_bowler(
    pressure_df, "pressure"
)


# ============================================================
# 15. MERGE BOWLER PERFORMANCE
# ============================================================

bowlers = bowl_all.merge(
    bowl_pressure,
    on=["bowler_id", "bowler_name"],
    how="left"
)

for col in [
    "pressure_runs_conceded",
    "pressure_legal_balls",
    "pressure_wickets",
    "pressure_dot_balls",
    "pressure_deliveries",
    "pressure_overs"
]:
    bowlers[col] = bowlers[col].fillna(0)


# ============================================================
# 16. SAMPLE ELIGIBILITY
# ============================================================

# Initial project screening thresholds, not official rules.

batters["sample_eligible"] = (
    (batters["pressure_balls"] >= 30)
    &
    (batters["overall_balls"] >= 60)
)

bowlers["sample_eligible"] = (
    (bowlers["pressure_legal_balls"] >= 12)
    &
    (bowlers["overall_legal_balls"] >= 24)
)


# ============================================================
# 17. VALIDATION
# ============================================================

print("\nVALIDATION CHECKS")

checks = {
    "Batter overall dots <= balls": (
        batters["overall_dot_balls"]
        <= batters["overall_balls"]
    ).all(),

    "Batter pressure dots <= balls": (
        batters["pressure_dot_balls"]
        <= batters["pressure_balls"]
    ).all(),

    "Bowler overall dots <= legal balls": (
        bowlers["overall_dot_balls"]
        <= bowlers["overall_legal_balls"]
    ).all(),

    "Bowler pressure dots <= legal balls": (
        bowlers["pressure_dot_balls"]
        <= bowlers["pressure_legal_balls"]
    ).all()
}

for name, passed in checks.items():
    print(f"{name}: {'PASS' if passed else 'FAIL'}")

if not all(checks.values()):
    raise ValueError("Performance validation failed.")


# ============================================================
# 18. SAVE OUTPUT FILES
# ============================================================

batters.to_csv(BATTER_OUTPUT, index=False)
bowlers.to_csv(BOWLER_OUTPUT, index=False)


# ============================================================
# 19. SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("1. PLAYER COVERAGE")
print("=" * 70)

print("Batters:", len(batters))
print("Bowlers:", len(bowlers))

print("\n2. BATTER SAMPLE ELIGIBILITY")
print("Eligible:", int(batters["sample_eligible"].sum()))
print("Not eligible:", int((~batters["sample_eligible"]).sum()))

print("\n3. BOWLER SAMPLE ELIGIBILITY")
print("Eligible:", int(bowlers["sample_eligible"].sum()))
print("Not eligible:", int((~bowlers["sample_eligible"]).sum()))

print("\n4. TOP BATTER PRESSURE RUN SCORERS")

print(
    batters.loc[batters["sample_eligible"]]
    .sort_values("pressure_runs", ascending=False)[
        [
            "striker_name",
            "pressure_runs",
            "pressure_balls",
            "pressure_strike_rate",
            "pressure_dot_percentage",
            "pressure_dismissals",
            "sample_eligible"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\n5. TOP BOWLER PRESSURE WICKET TAKERS")

print(
    bowlers.loc[bowlers["sample_eligible"]]
    .sort_values("pressure_wickets", ascending=False)[
        [
            "bowler_name",
            "pressure_wickets",
            "pressure_legal_balls",
            "pressure_economy",
            "pressure_dot_percentage",
            "sample_eligible"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\n6. OUTPUT FILES")
print(BATTER_OUTPUT)
print(BOWLER_OUTPUT)

print("\n" + "=" * 70)
print("PLAYER PERFORMANCE ENGINE COMPLETED")
print("=" * 70)
