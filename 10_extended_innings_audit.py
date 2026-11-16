
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw"
DATA = BASE / "data" / "processed"

df = pd.read_csv(DATA / "match_situation.csv")
matches = pd.read_csv(RAW / "matches.csv")
competitions = pd.read_csv(RAW / "competitions.csv")

# Find innings exceeding 120 legal balls
innings_summary = (
    df.groupby(["match_id", "innings"])
    .agg(
        legal_balls=("is_legal_ball", "sum"),
        total_runs=("total_runs", "sum"),
        wickets=("is_wicket", "sum")
    )
    .reset_index()
)

extended = innings_summary[
    innings_summary["legal_balls"] > 120
].copy()

# Add competition details
extended = (
    extended
    .merge(matches, on="match_id", how="left")
    .merge(competitions, on="comp_id", how="left")
)

print("\nEXTENDED INNINGS SUMMARY")
print("Total affected innings:", len(extended))

print("\nBY MATCH FORMAT")
print(extended["match_format"].value_counts(dropna=False))

print("\nBY COMPETITION")
print(
    extended.groupby(
        ["comp_name", "match_format", "season"]
    ).size().sort_values(ascending=False).to_string()
)

print("\nBY LEGAL BALL COUNT")
print(extended["legal_balls"].value_counts().sort_index())

print("\nSAMPLE AFFECTED INNINGS")
print(
    extended[
        [
            "match_id", "innings", "match_date",
            "comp_name", "match_format", "season",
            "legal_balls", "total_runs", "wickets", "result"
        ]
    ].head(25).to_string(index=False)
)

# Save full audit
extended.to_csv(
    DATA / "extended_innings_audit.csv",
    index=False
)

print("\nSaved: data/processed/extended_innings_audit.csv")
