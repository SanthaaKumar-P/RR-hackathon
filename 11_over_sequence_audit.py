
import pandas as pd
from pathlib import Path

# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw"
DATA = BASE / "data" / "processed"

print("=" * 70)
print("SUPERR SELECTOR - FINAL EXTRAS CLASSIFICATION AUDIT")
print("=" * 70)

# ============================================================
# 1. LOAD RAW DATA
# ============================================================

raw = pd.read_csv(RAW / "ball_by_ball.csv")

print("\nRAW DATA LOADED")
print("Total rows:", len(raw))

raw["extras_clean"] = (
    raw["extras_type"]
    .fillna("NULL")
    .astype(str)
    .str.strip()
    .str.lower()
)

# ============================================================
# 2. GLOBAL EXTRAS DISTRIBUTION
# ============================================================

print("\n1. GLOBAL EXTRAS DISTRIBUTION")

extras_summary = (
    raw.groupby("extras_clean")
    .agg(
        deliveries=("match_id", "size"),
        runs_column=("runs", "sum"),
        extras1=("extras1_runs", "sum"),
        extras2=("extras_2_runs", "sum")
    )
    .sort_values("deliveries", ascending=False)
)

print(extras_summary.to_string())

# ============================================================
# 3. INSPECT OTHER AND OVERSTEP
# ============================================================

print("\n2. DETAILS OF OTHER AND OVERSTEP")

special = raw[
    raw["extras_clean"].isin(["other", "overstep"])
].copy()

columns = [
    "match_id",
    "innings",
    "overid",
    "over_ball_num",
    "innings_ball_num",
    "runs",
    "extras_type",
    "extras1_runs",
    "extras_2_runs",
    "is_wicket",
    "dismissal_type"
]

print("Total special deliveries:", len(special))

if len(special) > 0:
    print(special[columns].head(50).to_string(index=False))
else:
    print("No other/overstep deliveries found.")

# ============================================================
# 4. LOAD PROCESSED MATCH SITUATION DATA
# ============================================================

df = pd.read_csv(DATA / "match_situation.csv")

print("\n3. PROCESSED DATA CHECK")
print("Total processed deliveries:", len(df))

# ============================================================
# 5. INSPECT KNOWN MATCH 13513
# ============================================================

print("\n4. MATCH 13513 - LEGAL BALLS PER OVER")

sample = df[
    (df["match_id"] == 13513) &
    (df["innings"] == 1)
].copy()

over_summary = (
    sample.groupby("overid")
    .agg(
        delivery_rows=("match_id", "size"),
        legal_balls=("is_legal_ball", "sum"),
        illegal_balls=("is_legal_ball", lambda x: (~x).sum()),
        first_cumulative=("legal_balls_bowled", "min"),
        last_cumulative=("legal_balls_bowled", "max")
    )
    .reset_index()
)

print(over_summary.to_string(index=False))

# ============================================================
# 6. FIND ALL AFFECTED INNINGS
# ============================================================

print("\n5. OVERS WITH MORE THAN 6 CLASSIFIED LEGAL BALLS")

innings_summary = (
    df.groupby(["match_id", "innings"])
    .agg(
        legal_balls=("is_legal_ball", "sum")
    )
    .reset_index()
)

affected = innings_summary[
    innings_summary["legal_balls"] > 120
][["match_id", "innings"]]

affected_deliveries = df.merge(
    affected,
    on=["match_id", "innings"],
    how="inner"
)

all_overs = (
    affected_deliveries.groupby(
        ["match_id", "innings", "overid"]
    )
    .agg(
        legal_balls=("is_legal_ball", "sum"),
        delivery_rows=("match_id", "size")
    )
    .reset_index()
)

more_than_six = all_overs[
    all_overs["legal_balls"] > 6
]

print("Affected innings:", len(affected))
print("Overs with more than 6 legal balls:", len(more_than_six))
print("Overs with fewer than 6 legal balls:",
      len(all_overs[all_overs["legal_balls"] < 6]))

print("\nFIRST 30 UNUSUAL OVERS")
print(more_than_six.head(30).to_string(index=False))

# ============================================================
# 7. EXTRAS TYPES IN UNUSUAL OVERS
# ============================================================

print("\n6. EXTRAS TYPES IN UNUSUAL OVERS")

over_keys = more_than_six[
    ["match_id", "innings", "overid"]
]

unusual = affected_deliveries.merge(
    over_keys,
    on=["match_id", "innings", "overid"],
    how="inner"
)

print(
    unusual["extras_type"]
    .fillna("NULL")
    .value_counts()
    .to_string()
)

# ============================================================
# 8. INSPECT THREE SAMPLE UNUSUAL OVERS
# ============================================================

print("\n7. SAMPLE UNUSUAL OVERS - DELIVERY DETAILS")

for _, row in more_than_six.head(3).iterrows():

    match_id = row["match_id"]
    innings = row["innings"]
    over = row["overid"]

    print(
        f"\nMatch: {match_id} | "
        f"Innings: {innings} | Over: {over}"
    )

    details = affected_deliveries[
        (affected_deliveries["match_id"] == match_id) &
        (affected_deliveries["innings"] == innings) &
        (affected_deliveries["overid"] == over)
    ]

    detail_columns = [
        "over_ball_num",
        "innings_ball_num",
        "runs",
        "extras_type",
        "extras1_runs",
        "extras_2_runs",
        "total_runs",
        "is_legal_ball",
        "legal_balls_bowled"
    ]

    print(details[detail_columns].to_string(index=False))

# ============================================================
# 9. SAVE AUDIT OUTPUTS
# ============================================================

all_overs.to_csv(
    DATA / "affected_over_sequence_audit.csv",
    index=False
)

special.to_csv(
    DATA / "special_extras_audit.csv",
    index=False
)

print("\n" + "=" * 70)
print("FINAL AUDIT COMPLETED")
print("=" * 70)

print("\nFiles saved:")
print("1. data/processed/affected_over_sequence_audit.csv")
print("2. data/processed/special_extras_audit.csv")
