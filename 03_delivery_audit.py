
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

# Load selected matches and delivery data
matches = pd.read_csv(PROCESSED / "target_matches.csv")
balls = pd.read_csv(RAW / "ball_by_ball.csv")

# Retain only selected IPL and T20I matches
selected_ids = set(matches["match_id"])
df = balls[balls["match_id"].isin(selected_ids)].copy()

print("=" * 65)
print("SUPERR SELECTOR - DELIVERY AUDIT")
print("=" * 65)

print("\n1. SELECTED DELIVERY RECORDS")
print("Total deliveries:", len(df))
print("Unique matches:", df["match_id"].nunique())

# Innings distribution
print("\n2. INNINGS DISTRIBUTION")
print(df.groupby("innings").agg(
    deliveries=("match_id", "size"),
    matches=("match_id", "nunique")
))

# Extras analysis
print("\n3. EXTRAS TYPES")
print(df["extras_type"].value_counts(dropna=False).to_string())

print("\n4. EXTRAS VALUE DISTRIBUTION")
print(df[["extras1_runs", "extras_2_runs"]].describe())

# Inspect deliveries containing extras
print("\n5. SAMPLE EXTRAS DELIVERIES")

extra_rows = df[
    (df["extras1_runs"].fillna(0) != 0)
    | (df["extras_2_runs"].fillna(0) != 0)
    | df["extras_type"].notna()
]

columns = [
    "match_id", "innings", "overid",
    "over_ball_num", "runs", "extras_type",
    "extras1_runs", "extras_2_runs",
    "is_wicket", "dismissal_type"
]

print(extra_rows[columns].head(15).to_string(index=False))

# Wicket analysis
print("\n6. WICKET DISTRIBUTION")
print(df["is_wicket"].value_counts(dropna=False))

print("\n7. DISMISSAL TYPES")
print(df.loc[df["is_wicket"] == True, "dismissal_type"]
      .value_counts(dropna=False).to_string())

# Overs and ball numbering
print("\n8. DELIVERY NUMBERING")

for col in ["overid", "over_ball_num", "innings_ball_num"]:
    print(f"\n{col}:")
    print(df[col].describe())

# Runs distribution
print("\n9. RUNS DISTRIBUTION")
print(df["runs"].value_counts().sort_index().to_string())

print("\n10. SAMPLE WICKET DELIVERIES")
wickets = df[df["is_wicket"] == True]
print(wickets[columns].head(15).to_string(index=False))

print("\nDELIVERY AUDIT COMPLETED!")
