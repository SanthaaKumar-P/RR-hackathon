
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw"

matches = pd.read_csv(RAW / "matches.csv")
competitions = pd.read_csv(RAW / "competitions.csv")
balls = pd.read_csv(RAW / "ball_by_ball.csv")

match_id = 13513

match = matches[matches["match_id"] == match_id].merge(
    competitions,
    on="comp_id",
    how="left"
)

print("\nMATCH DETAILS")
print(match.to_string(index=False))

print("\nINNINGS SUMMARY FROM RAW DATA")

balls["total_runs"] = (
    balls["runs"].fillna(0)
    + balls["extras1_runs"].fillna(0)
    + balls["extras_2_runs"].fillna(0)
)

summary = balls[balls["match_id"] == match_id].groupby("innings").agg(
    total_deliveries=("match_id", "size"),
    total_runs=("total_runs", "sum"),
    wickets=("is_wicket", "sum"),
    last_over=("overid", "max"),
    last_ball=("over_ball_num", "max")
)

print(summary.to_string())

print("\nCOMPETITION DISTRIBUTION")
print(
    competitions[
        competitions["comp_id"].isin(match["comp_id"])
    ].to_string(index=False)
)
