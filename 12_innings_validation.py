
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw"
DATA = BASE / "data" / "processed"

summary = pd.read_csv(DATA / "innings_summary.csv")
matches = pd.read_csv(RAW / "matches.csv")

print("=" * 65)
print("SUPERR SELECTOR - INNINGS VALIDATION")
print("=" * 65)

# 1. INNINGS COUNT
print("\n1. INNINGS COVERAGE")

print("First innings:", len(summary[summary["innings"] == 1]))
print("Second innings:", len(summary[summary["innings"] == 2]))

# 2. CHECK WICKET COUNTS
print("\n2. WICKET VALIDATION")

print("Maximum wickets:", summary["total_wickets"].max())
print("Negative wickets:", (summary["total_wickets"] < 0).sum())

# 3. CHECK LEGAL BALL COUNTS
print("\n3. LEGAL BALL VALIDATION")

print("Minimum legal balls:", summary["legal_balls"].min())
print("Maximum legal balls:", summary["legal_balls"].max())

# 4. AMBIGUOUS DELIVERIES
print("\n4. AMBIGUOUS DELIVERY COUNTS")

print(
    summary["ambiguous_deliveries"]
    .value_counts()
    .sort_index()
    .to_string()
)

# 5. MERGE MATCH INFORMATION
print("\n5. MATCH RESULT COMPARISON")

comparison = summary.merge(
    matches[
        ["match_id", "result", "win_team_id",
         "home_team", "away_team"]
    ],
    on="match_id",
    how="left"
)

print("Missing match results:", comparison["result"].isna().sum())

# 6. SAVE VALIDATION DATA
comparison.to_csv(
    DATA / "innings_validation.csv",
    index=False
)

print("\n6. SAVED")
print("data/processed/innings_validation.csv")

print("\nVALIDATION SCRIPT COMPLETED")
