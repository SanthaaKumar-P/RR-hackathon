
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================================
# SUPERR SELECTOR - MATCH SITUATION ENGINE
# ==========================================================

BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

PROCESSED.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("SUPERR SELECTOR - MATCH SITUATION ENGINE")
print("=" * 70)

# ==========================================================
# 1. LOAD DATA
# ==========================================================

balls = pd.read_csv(RAW / "ball_by_ball.csv")
matches = pd.read_csv(PROCESSED / "target_matches.csv")

selected_ids = set(matches["match_id"])

df = balls[
    balls["match_id"].isin(selected_ids)
    & balls["innings"].isin([1, 2])
].copy()

print("\n1. FILTERED DATA")
print("Deliveries:", len(df))
print("Matches:", df["match_id"].nunique())

# ==========================================================
# 2. CLEAN NUMERIC COLUMNS
# ==========================================================

numeric_cols = [
    "runs",
    "extras1_runs",
    "extras_2_runs",
    "innings_ball_num",
    "overid",
    "over_ball_num"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(
        df[col], errors="coerce"
    ).fillna(0)

# ==========================================================
# 3. TOTAL TEAM RUNS
# ==========================================================

df["total_runs"] = (
    df["runs"]
    + df["extras1_runs"]
    + df["extras_2_runs"]
)

# ==========================================================
# 4. EXTRAS CLASSIFICATION
# ==========================================================

df["extras_type_clean"] = (
    df["extras_type"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
)

# Known illegal deliveries
known_illegal = ["wide", "overstep"]

# "other" is ambiguous in this dataset.
# Do not silently assume its legal-ball status.
df["ambiguous_extra"] = (
    df["extras_type_clean"] == "other"
)

df["is_legal_ball"] = (
    ~df["extras_type_clean"].isin(known_illegal)
    & ~df["ambiguous_extra"]
)

df["delivery_classification"] = np.select(
    [
        df["extras_type_clean"].isin(known_illegal),
        df["ambiguous_extra"]
    ],
    [
        "known_illegal",
        "ambiguous_other"
    ],
    default="legal"
)

print("\n2. DELIVERY CLASSIFICATION")

print(
    df.groupby("delivery_classification")
    .size()
    .to_string()
)

print("\nExtras distribution:")
print(
    df["extras_type_clean"]
    .replace("", "NULL")
    .value_counts()
    .to_string()
)

# ==========================================================
# 5. WICKET NORMALIZATION
# ==========================================================

df["is_wicket"] = (
    df["is_wicket"]
    .fillna(False)
    .astype(bool)
)

# ==========================================================
# 6. SORT DELIVERIES
# ==========================================================

df["_source_order"] = np.arange(len(df))

df = df.sort_values(
    [
        "match_id",
        "innings",
        "innings_ball_num",
        "overid",
        "over_ball_num",
        "_source_order"
    ],
    kind="stable"
).reset_index(drop=True)

# ==========================================================
# 7. CUMULATIVE MATCH SITUATION
# ==========================================================

group = df.groupby(
    ["match_id", "innings"],
    sort=False
)

df["current_score"] = (
    group["total_runs"].cumsum()
)

df["wickets_lost"] = (
    group["is_wicket"].cumsum()
)

df["legal_balls_bowled"] = (
    group["is_legal_ball"].cumsum()
)

df["wickets_remaining"] = (
    10 - df["wickets_lost"]
).clip(lower=0)

# ==========================================================
# 8. FIRST INNINGS TOTALS
# ==========================================================

first_innings_totals = (
    df[df["innings"] == 1]
    .groupby("match_id")["total_runs"]
    .sum()
)

# ==========================================================
# 9. MATCH LIMITS
# ==========================================================

match_limits = matches.set_index("match_id")

first_limits = pd.to_numeric(
    match_limits["first_inn_revised_overs"],
    errors="coerce"
)

second_limits = pd.to_numeric(
    match_limits["second_inn_revised_overs"],
    errors="coerce"
)

# Default normal T20 limit.
# Revised-overs fields are provisionally interpreted
# as legal-ball limits based on the earlier audit.
first_limits = first_limits.where(
    first_limits.notna() & (first_limits > 0),
    120
)

second_limits = second_limits.where(
    second_limits.notna() & (second_limits > 0),
    120
)

df["maximum_legal_balls"] = np.where(
    df["innings"] == 1,
    df["match_id"].map(first_limits),
    df["match_id"].map(second_limits)
)

df["maximum_legal_balls"] = (
    pd.to_numeric(
        df["maximum_legal_balls"],
        errors="coerce"
    )
    .fillna(120)
    .astype(int)
)

df["overs_limit"] = (
    df["maximum_legal_balls"] / 6
)

# ==========================================================
# 10. BALLS REMAINING
# ==========================================================

df["balls_remaining"] = (
    df["maximum_legal_balls"]
    - df["legal_balls_bowled"]
).clip(lower=0)

df["overs_remaining"] = (
    df["balls_remaining"] / 6
)

# ==========================================================
# 11. CHASE TARGET
# ==========================================================

df["first_innings_score"] = (
    df["match_id"].map(first_innings_totals)
)

df["revised_target"] = (
    df["match_id"].map(
        match_limits["revised_target"]
    )
)

df["target_runs"] = (
    df["first_innings_score"] + 1
)

revised_mask = (
    df["innings"].eq(2)
    & df["revised_target"].notna()
    & (df["revised_target"] > 0)
)

df.loc[revised_mask, "target_runs"] = (
    df.loc[revised_mask, "revised_target"]
)

# ==========================================================
# 12. RUNS REQUIRED
# ==========================================================

second = df["innings"].eq(2)

df["runs_required"] = np.nan

df.loc[second, "runs_required"] = (
    df.loc[second, "target_runs"]
    - df.loc[second, "current_score"]
).clip(lower=0)

# ==========================================================
# 13. REQUIRED RUN RATE
# ==========================================================

df["required_run_rate"] = np.nan

valid_chase = (
    second
    & (df["balls_remaining"] > 0)
)

df.loc[valid_chase, "required_run_rate"] = (
    df.loc[valid_chase, "runs_required"]
    * 6
    / df.loc[valid_chase, "balls_remaining"]
)

# ==========================================================
# 14. CURRENT RUN RATE
# ==========================================================

df["current_run_rate"] = np.where(
    df["legal_balls_bowled"] > 0,
    df["current_score"] * 6
    / df["legal_balls_bowled"],
    0
)

# ==========================================================
# 15. SAVE MATCH SITUATION
# ==========================================================

df = df.drop(columns=["_source_order"])

df.to_csv(
    PROCESSED / "match_situation.csv",
    index=False
)

# ==========================================================
# 16. INNINGS SUMMARY
# ==========================================================

summary = (
    df.groupby(["match_id", "innings"])
    .agg(
        total_runs=("total_runs", "sum"),
        total_wickets=("is_wicket", "sum"),
        legal_balls=("is_legal_ball", "sum"),
        ambiguous_deliveries=("ambiguous_extra", "sum"),
        maximum_legal_balls=(
            "maximum_legal_balls", "first"
        ),
        maximum_overs=("overs_limit", "first")
    )
    .reset_index()
)

summary.to_csv(
    PROCESSED / "innings_summary.csv",
    index=False
)

# ==========================================================
# 17. VALIDATION
# ==========================================================

print("\n3. MATCH SITUATION VALIDATION")

print("Total runs:", df["total_runs"].sum())
print("Legal deliveries:", df["is_legal_ball"].sum())
print("Ambiguous deliveries:", df["ambiguous_extra"].sum())
print("Known illegal deliveries:", 
      (~df["is_legal_ball"] & ~df["ambiguous_extra"]).sum())
print("Wicket events:", df["is_wicket"].sum())

print("\n4. BALL LIMIT DISTRIBUTION")

print(
    summary["maximum_legal_balls"]
    .value_counts()
    .sort_index()
    .to_string()
)

print("\n5. INNINGS EXCEEDING BALL LIMIT")

violations = summary[
    summary["legal_balls"] > summary["maximum_legal_balls"]
]

print("Affected innings:", len(violations))

if len(violations) > 0:
    print(violations.head(25).to_string(index=False))

print("\n6. AMBIGUOUS DELIVERY INNINGS")

ambiguous_summary = summary[
    summary["ambiguous_deliveries"] > 0
]

print("Innings containing ambiguous extras:",
      len(ambiguous_summary))

print("\n7. NEGATIVE RUNS REQUIRED")

negative_required = df[
    df["runs_required"] < 0
]

print("Rows:", len(negative_required))

print("\n8. SAMPLE MATCH SITUATION")

if not df.empty:
    sample_match = df["match_id"].iloc[0]

    sample = df[
        df["match_id"] == sample_match
    ].tail(10)

    columns = [
        "match_id",
        "innings",
        "overid",
        "over_ball_num",
        "total_runs",
        "current_score",
        "wickets_lost",
        "legal_balls_bowled",
        "maximum_legal_balls",
        "balls_remaining",
        "runs_required",
        "required_run_rate",
        "delivery_classification"
    ]

    print(sample[columns].to_string(index=False))

# ==========================================================
# 18. OUTPUT
# ==========================================================

print("\n9. OUTPUT FILES")
print("1. match_situation.csv")
print("2. innings_summary.csv")

print("\n" + "=" * 70)
print("MATCH SITUATION ENGINE COMPLETED")
print("=" * 70)
