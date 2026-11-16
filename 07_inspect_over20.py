
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "processed"

df = pd.read_csv(DATA / "match_situation.csv")

match_id = 13513
innings = 1

sample = df[
    (df["match_id"] == match_id) &
    (df["innings"] == innings) &
    (df["overid"] >= 19)
].copy()

columns = [
    "match_id",
    "innings",
    "overid",
    "over_ball_num",
    "innings_ball_num",
    "striker_name",
    "bowler_name",
    "runs",
    "extras_type",
    "extras1_runs",
    "extras_2_runs",
    "total_runs",
    "is_legal_ball",
    "legal_balls_bowled",
    "is_wicket"
]

print("\nDELIVERIES IN OVERS 19 AND 20")
print(sample[columns].to_string(index=False))

print("\nDELIVERY COUNTS BY OVER")
print(
    sample.groupby("overid").agg(
        delivery_rows=("match_id", "size"),
        legal_balls=("is_legal_ball", "sum"),
        last_ball_number=("over_ball_num", "max"),
        last_innings_ball=("innings_ball_num", "max")
    )
)
