
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

PROCESSED.mkdir(parents=True, exist_ok=True)

# Load datasets
competitions = pd.read_csv(RAW / "competitions.csv")
matches = pd.read_csv(RAW / "matches.csv")
balls = pd.read_csv(RAW / "ball_by_ball.csv")

print("=" * 65)
print("SUPERR SELECTOR - COMPETITION AUDIT")
print("=" * 65)

# 1. Competition format distribution
print("\n1. COMPETITION FORMATS")
print(competitions["match_format"].value_counts())

# 2. Identify IPL competitions
ipl = competitions[
    competitions["comp_name"].str.match(
        r"^IPL\s", case=False, na=False
    )
].copy()

# 3. Identify T20I competitions
t20i = competitions[
    competitions["match_format"].str.upper() == "T20I"
].copy()

# 4. Show IPL seasons
print("\n2. IPL COMPETITIONS")
print(ipl[["comp_id", "comp_name", "season"]].to_string(index=False))

print("\nTotal IPL competitions:", len(ipl))

# 5. Show T20I coverage
print("\n3. T20I COMPETITIONS")
print("Total T20I competitions:", len(t20i))

# 6. Identify unrelated T20 competitions
other_t20 = competitions[
    (competitions["match_format"].str.upper() == "T20")
    & (~competitions["comp_name"].str.match(
        r"^IPL\s", case=False, na=False
    ))
]

print("\n4. OTHER T20 COMPETITIONS")
print(other_t20[["comp_name", "season"]].to_string(index=False))

# 7. Connect matches with competition information
enriched = matches.merge(
    competitions,
    on="comp_id",
    how="left",
    validate="many_to_one"
)

# 8. Keep only IPL and T20I matches
target = enriched[
    (enriched["match_format"].str.upper() == "T20I")
    | (enriched["comp_name"].str.match(
        r"^IPL\s", case=False, na=False
    ))
].copy()

# 9. Check ball-by-ball coverage
ball_match_ids = set(balls["match_id"].unique())

target["has_ball_data"] = target["match_id"].isin(
    ball_match_ids
)

available = target[target["has_ball_data"]]
missing = target[~target["has_ball_data"]]

print("\n5. MATCH COVERAGE")
print("All match records:", matches["match_id"].nunique())
print("Target IPL + T20I matches:", target["match_id"].nunique())
print("Matches with ball data:", len(available))
print("Matches without ball data:", len(missing))

# 10. Coverage by competition
print("\n6. COVERAGE BY FORMAT")

print(
    target.groupby("match_format")
    .agg(
        total_matches=("match_id", "nunique"),
        matches_with_ball_data=("has_ball_data", "sum")
    )
)

# 11. Save audit outputs
target.to_csv(PROCESSED / "target_matches.csv", index=False)

missing.to_csv(
    PROCESSED / "matches_missing_ball_data.csv",
    index=False
)

print("\nAUDIT FILES SAVED SUCCESSFULLY!")
print("Location:", PROCESSED)
