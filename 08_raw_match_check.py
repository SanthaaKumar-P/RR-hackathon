
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw"

df = pd.read_csv(RAW / "ball_by_ball.csv")

sample = df[
    (df["match_id"] == 13513) &
    (df["innings"] == 1) &
    (df["overid"] >= 19)
].copy()

columns = [
    "match_id", "innings", "overid",
    "over_ball_num", "innings_ball_num",
    "striker_name", "bowler_name",
    "runs", "extras_type",
    "extras1_runs", "extras_2_runs",
    "is_wicket"
]

print("\nRAW SOURCE - OVERS 19 AND 20")
print(sample[columns].to_string(index=False))

print("\nRAW DELIVERY COUNTS")
print(
    sample.groupby("overid").agg(
        rows=("match_id", "size"),
        max_ball_number=("over_ball_num", "max"),
        max_innings_ball=("innings_ball_num", "max")
    )
)
