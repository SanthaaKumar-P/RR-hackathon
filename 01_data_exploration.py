
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")

print("=" * 60)
print("SUPERR SELECTOR - DATASET EXPLORATION")
print("=" * 60)

for file in sorted(DATA_DIR.glob("*.csv")):
    df = pd.read_csv(file, low_memory=False)

    print(f"\nDATASET: {file.name}")
    print("-" * 50)
    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])
    print("Column names:", df.columns.tolist())
    print("Duplicate rows:", df.duplicated().sum())
    print("Missing values:")
    print(df.isnull().sum()[df.isnull().sum() > 0])
    print("\nSample records:")
    print(df.head(3).to_string(index=False))

print("\nDATA EXPLORATION COMPLETED!")
