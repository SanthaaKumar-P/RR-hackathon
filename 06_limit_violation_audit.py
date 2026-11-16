
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw"
DATA = BASE / "data" / "processed"

df = pd.read_csv(DATA / "match_situation.csv")
matches = pd.read_csv(RAW / "matches.csv")

print("=" * 70)
print("SUPERR SELECTOR - BALL LIMIT VIOLATION INVESTIGATION")
print("=" * 70)

# 1. Find deliveries exceeding innings limits
violations = df[
    df["legal_balls_bowled"] > df["maximum_legal_balls"]
].copy()

print("\n1. VIOLATION SUMMARY")
print("Violation rows:", len(violations))
print("Affected matches:", violations["match_id"].nunique())

# 2. Identify affected innings
affected = (
    violations.groupby(["match_id", "innings"])
    .agg(
        violation_rows=("legal_balls_bowled", "size"),
        maximum_balls=("maximum_legal_balls", "first"),
        highest_legal_ball=("legal_balls_bowled", "max")
    )
    .reset_index()
)

print("\n2. AFFECTED INNINGS")
print(affected.head(30).to_string(index=False))

# 3. Inspect the actual deliveries
print("\n3. SAMPLE VIOLATION DELIVERIES")

columns = [
    "match_id", "innings", "overid",
    "over_ball_num", "innings_ball_num",
    "extras_type", "extras1_runs",
    "extras_2_runs", "total_runs",
    "is_legal_ball", "legal_balls_bowled",
    "maximum_legal_balls"
]

print(
    violations[columns]
    .head(30)
    .to_string(index=False)
)

# 4. Check whether unrecognized extras exist
print("\n4. EXTRA TYPES IN VIOLATION DELIVERIES")

print(
    violations["extras_type"]
    .value_counts(dropna=False)
    .to_string()
)

# 5. Check all innings with more than 120 legal balls
print("\n5. INNINGS WITH MORE THAN 120 LEGAL BALLS")

innings = (
    df.groupby(["match_id", "innings"])
    .agg(
        legal_balls=("legal_balls_bowled", "max"),
        maximum_balls=("maximum_legal_balls", "first"),
        final_score=("current_score", "max")
    )
    .reset_index()
)

print(
    innings[innings["legal_balls"] > 120]
    .to_string(index=False)
)

# 6. Match metadata
affected_ids = affected["match_id"].unique()

metadata = matches[
    matches["match_id"].isin(affected_ids)
][[
    "match_id", "comp_id", "match_date",
    "stage", "venue_country",
    "first_inn_revised_overs",
    "second_inn_revised_overs",
    "revised_target", "result"
]]

print("\n6. MATCH METADATA")
print(metadata.head(30).to_string(index=False))

# 7. Save investigation results
affected.to_csv(
    DATA / "affected_innings.csv", index=False
)

violations[columns].to_csv(
    DATA / "violation_deliveries.csv", index=False
)

metadata.to_csv(
    DATA / "violation_match_metadata.csv", index=False
)

print("\nINVESTIGATION FILES SAVED!")
