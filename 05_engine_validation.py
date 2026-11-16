
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "processed"

df = pd.read_csv(DATA / "match_situation.csv")
summary = pd.read_csv(DATA / "innings_summary.csv")
matches = pd.read_csv(DATA / "target_matches.csv")

print("=" * 65)
print("SUPERR SELECTOR - ENGINE VALIDATION")
print("=" * 65)

# 1. Basic validation
print("\n1. BASIC CHECKS")

print("Rows:", len(df))
print("Unique matches:", df["match_id"].nunique())
print("Missing match IDs:", df["match_id"].isna().sum())

# 2. Score calculation validation
print("\n2. SCORE VALIDATION")

df["expected_runs"] = (
    df["runs"]
    + df["extras1_runs"]
    + df["extras_2_runs"]
)

score_errors = (
    df["total_runs"] != df["expected_runs"]
).sum()

print("Score calculation errors:", score_errors)

# 3. Legal delivery validation
print("\n3. LEGAL BALL VALIDATION")

illegal_types = ["wide", "overstep"]

expected_legal = ~(
    df["extras_type_clean"].isin(illegal_types)
)

legal_errors = (
    df["is_legal_ball"] != expected_legal
).sum()

print("Legal ball classification errors:", legal_errors)

# 4. Cumulative score validation
print("\n4. CUMULATIVE SCORE VALIDATION")

score_diff = (
    df.groupby(["match_id", "innings"])["total_runs"]
    .cumsum()
    - df["current_score"]
)

print("Cumulative score errors:", (score_diff != 0).sum())

# 5. Wicket validation
print("\n5. WICKET VALIDATION")

wicket_diff = (
    df.groupby(["match_id", "innings"])["is_wicket"]
    .cumsum()
    - df["wickets_lost"]
)

print("Cumulative wicket errors:", (wicket_diff != 0).sum())

print("Maximum wickets in an innings:",
      df["wickets_lost"].max())

# 6. Innings coverage
print("\n6. INNINGS COVERAGE")

innings_count = (
    df.groupby("innings")["match_id"].nunique()
)

print(innings_count)

matches_with_second = (
    df.loc[df["innings"] == 2, "match_id"].nunique()
)

all_matches = matches["match_id"].nunique()

print("Matches without second innings:",
      all_matches - matches_with_second)

# 7. Overs validation
print("\n7. OVERS VALIDATION")

print("Overs limit distribution:")
print(df["overs_limit"].value_counts().sort_index().to_string())

invalid_limits = df[
    (df["overs_limit"] <= 0)
    | (df["overs_limit"] > 20)
]

print("Unusual overs limit rows:", len(invalid_limits))

# 8. Ball limit validation
print("\n8. BALL LIMIT VALIDATION")

over_limit = df[
    df["legal_balls_bowled"]
    > df["maximum_legal_balls"]
]

print("Rows exceeding maximum balls:", len(over_limit))

# 9. Runs required validation
print("\n9. CHASE VALIDATION")

second = df[df["innings"] == 2]

negative_required = second[
    second["runs_required"] < 0
]

print("Negative runs required:", len(negative_required))

# 10. Innings summary
print("\n10. INNINGS SUMMARY")

print(summary.head(10).to_string(index=False))

# 11. Extras categories
print("\n11. EXTRAS CATEGORY AUDIT")

print(
    df["extras_type_clean"]
    .value_counts(dropna=False)
    .to_string()
)

# 12. Save innings-level diagnostics
diagnostics = (
    df.groupby(["match_id", "innings"])
    .agg(
        final_score=("current_score", "max"),
        wickets=("wickets_lost", "max"),
        legal_balls=("legal_balls_bowled", "max"),
        overs_limit=("overs_limit", "first"),
        final_runs_required=("runs_required", "last")
    )
    .reset_index()
)

diagnostics.to_csv(
    DATA / "innings_diagnostics.csv",
    index=False
)

print("\nVALIDATION COMPLETED!")
print("Saved: innings_diagnostics.csv")
