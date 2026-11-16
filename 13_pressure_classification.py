
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# SUPERR SELECTOR - PRESSURE CLASSIFICATION ENGINE
# ============================================================

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "processed"

INPUT_FILE = DATA / "match_situation.csv"
OUTPUT_FILE = DATA / "pressure_classified.csv"

df = pd.read_csv(INPUT_FILE)

print("=" * 65)
print("SUPERR SELECTOR - PRESSURE CLASSIFICATION ENGINE")
print("=" * 65)

# ============================================================
# 1. PRE-DELIVERY MATCH STATE
# ============================================================

group = df.groupby(["match_id", "innings"], sort=False)

# State before the current delivery
df["score_before"] = (
    group["current_score"].shift(1).fillna(0)
)

df["wickets_lost_before"] = (
    group["wickets_lost"].shift(1).fillna(0)
)

df["wickets_remaining_before"] = (
    10 - df["wickets_lost_before"]
).clip(lower=0)

df["legal_balls_before"] = (
    group["legal_balls_bowled"].shift(1).fillna(0)
)

df["balls_remaining_before"] = (
    df["maximum_legal_balls"] -
    df["legal_balls_before"]
).clip(lower=0)

# Chase requirements before the current delivery
df["runs_required_before"] = (
    df["target_runs"] - df["score_before"]
)

df["required_run_rate_before"] = np.where(
    (df["innings"] == 2) &
    (df["balls_remaining_before"] > 0),
    df["runs_required_before"] * 6 /
    df["balls_remaining_before"],
    np.nan
)

# Current scoring rate before the current delivery
df["current_run_rate_before"] = np.where(
    df["legal_balls_before"] > 0,
    df["score_before"] * 6 /
    df["legal_balls_before"],
    0
)

# ============================================================
# 2. INNINGS PHASE
# ============================================================

df["innings_phase"] = np.select(
    [
        df["legal_balls_before"] < 36,
        df["legal_balls_before"] < 90
    ],
    [
        "Powerplay",
        "Middle"
    ],
    default="Death"
)

# ============================================================
# 3. CHASE PRESSURE CLASSIFICATION
# ============================================================

conditions = [
    df["required_run_rate_before"] < 8,

    df["required_run_rate_before"].between(
        8, 10, inclusive="left"
    ),

    df["required_run_rate_before"].between(
        10, 12, inclusive="left"
    ),

    df["required_run_rate_before"] >= 12
]

df["chase_pressure"] = np.select(
    conditions,
    ["Low", "Moderate", "High", "Extreme"],
    default="Not Applicable"
)

# Exclude first innings, completed chases and invalid chase states
invalid_chase = (
    (df["innings"] != 2) |
    (df["runs_required_before"] <= 0) |
    (df["balls_remaining_before"] <= 0) |
    (df["required_run_rate_before"].isna())
)

df.loc[invalid_chase, "chase_pressure"] = "Not Applicable"

# ============================================================
# 4. WICKET PRESSURE CLASSIFICATION
# ============================================================

df["wicket_pressure"] = np.select(
    [
        df["wickets_remaining_before"] <= 2,
        df["wickets_remaining_before"] <= 4,
        df["wickets_remaining_before"] <= 6
    ],
    [
        "Extreme",
        "High",
        "Moderate"
    ],
    default="Low"
)

# ============================================================
# 5. FIRST-INNINGS SCORING PRESSURE
# ============================================================

df["first_innings_pressure"] = "Not Applicable"

first = df["innings"] == 1

df.loc[first, "first_innings_pressure"] = np.select(
    [
        (
            (df.loc[first, "innings_phase"] == "Death") &
            (df.loc[first, "wickets_remaining_before"] <= 4)
        ),

        (
            df.loc[first, "innings_phase"] == "Death"
        ),

        (
            df.loc[first, "wickets_remaining_before"] <= 3
        ),

        (
            df.loc[first, "current_run_rate_before"] < 6
        )
    ],
    [
        "Extreme",
        "High",
        "High",
        "Moderate"
    ],
    default="Low"
)

# ============================================================
# 6. COMBINED CHASE PRESSURE SCORE
# ============================================================

pressure_values = {
    "Low": 1,
    "Moderate": 2,
    "High": 3,
    "Extreme": 4
}

df["chase_pressure_score"] = np.nan

chase_mask = df["chase_pressure"] != "Not Applicable"

df.loc[chase_mask, "chase_pressure_score"] = (
    df.loc[chase_mask, "chase_pressure"].map(pressure_values) * 0.6
    +
    df.loc[chase_mask, "wicket_pressure"].map(pressure_values) * 0.4
)

# ============================================================
# 7. DATA VALIDATION
# ============================================================

print("\n1. TOTAL DELIVERIES")
print(len(df))

print("\n2. INNINGS PHASE DISTRIBUTION")
print(df["innings_phase"].value_counts().to_string())

print("\n3. CHASE PRESSURE DISTRIBUTION")
print(df["chase_pressure"].value_counts().to_string())

print("\n4. FIRST-INNINGS PRESSURE DISTRIBUTION")
print(df["first_innings_pressure"].value_counts().to_string())

print("\n5. WICKET PRESSURE DISTRIBUTION")
print(df["wicket_pressure"].value_counts().to_string())

print("\n6. CHASE PRESSURE SCORE")
print(df["chase_pressure_score"].describe().to_string())

print("\n7. VALIDATION CHECKS")

print(
    "Missing pre-delivery scores:",
    df["score_before"].isna().sum()
)

print(
    "Negative wickets remaining:",
    (df["wickets_remaining_before"] < 0).sum()
)

print(
    "Negative balls remaining:",
    (df["balls_remaining_before"] < 0).sum()
)

print(
    "Invalid chase pressure assignments:",
    (
        (df["innings"] != 2) &
        (df["chase_pressure"] != "Not Applicable")
    ).sum()
)

print(
    "Missing chase pressure scores:",
    df.loc[chase_mask, "chase_pressure_score"].isna().sum()
)

# ============================================================
# 8. SAVE OUTPUT
# ============================================================

df.to_csv(OUTPUT_FILE, index=False)

print("\n8. OUTPUT SAVED")
print(OUTPUT_FILE)

print("\n" + "=" * 65)
print("PRESSURE CLASSIFICATION COMPLETED")
print("=" * 65)
