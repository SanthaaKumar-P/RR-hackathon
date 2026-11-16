import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field

def find_base_dir() -> Path:
    env_root = os.getenv("PROJECT_ROOT")
    if env_root:
        p = Path(env_root).resolve()
        if (p / "outputs").exists():
            return p
    p_file = Path(__file__).resolve().parent.parent.parent.parent
    if (p_file / "outputs").exists():
        return p_file
    p_cwd = Path.cwd().resolve()
    if (p_cwd / "outputs").exists():
        return p_cwd
    if (p_cwd.parent / "outputs").exists():
        return p_cwd.parent
    return p_file

class Settings(BaseModel):
    PROJECT_NAME: str = "SupeRR Selector – Cricket Intelligence API"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "FastAPI analytical backend providing real-time cricket pressure intelligence, player rankings, and match analytics."
    API_V1_STR: str = "/api/v1"
    
    # Project Root Resolution
    BASE_DIR: Path = Field(default_factory=find_base_dir)
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "*"
    ]

    @property
    def DATA_RAW_DIR(self) -> Path:
        return self.BASE_DIR / "data" / "raw"

    @property
    def DATA_PROCESSED_DIR(self) -> Path:
        return self.BASE_DIR / "data" / "processed"

    @property
    def OUTPUTS_DIR(self) -> Path:
        return self.BASE_DIR / "outputs"

    # Core Output Datasets (Source of truth for rankings)
    @property
    def FINAL_BATTER_RANKINGS_FILE(self) -> Path:
        return self.OUTPUTS_DIR / "final_batter_rankings.csv"

    @property
    def FINAL_BOWLER_RANKINGS_FILE(self) -> Path:
        return self.OUTPUTS_DIR / "final_bowler_rankings.csv"

    @property
    def TOP10_BATTERS_FILE(self) -> Path:
        return self.OUTPUTS_DIR / "top10_batters_by_format.csv"

    @property
    def TOP10_BOWLERS_FILE(self) -> Path:
        return self.OUTPUTS_DIR / "top10_bowlers_by_format.csv"

    @property
    def RANKING_SENSITIVITY_FILE(self) -> Path:
        return self.OUTPUTS_DIR / "ranking_sensitivity_analysis.csv"

    @property
    def BOWLER_ACCOUNTING_SENSITIVITY_FILE(self) -> Path:
        return self.OUTPUTS_DIR / "bowler_accounting_sensitivity.csv"

    @property
    def METHODOLOGY_FILE(self) -> Path:
        return self.OUTPUTS_DIR / "ranking_methodology.txt"

    # Core Processed Datasets
    @property
    def TARGET_MATCHES_FILE(self) -> Path:
        return self.DATA_PROCESSED_DIR / "target_matches.csv"

    @property
    def PRESSURE_CLASSIFIED_FILE(self) -> Path:
        return self.DATA_PROCESSED_DIR / "pressure_classified.csv"

    @property
    def INNINGS_SUMMARY_FILE(self) -> Path:
        return self.DATA_PROCESSED_DIR / "innings_summary.csv"

    @property
    def INNINGS_VALIDATION_FILE(self) -> Path:
        return self.DATA_PROCESSED_DIR / "innings_validation.csv"

    @property
    def BATTER_PERFORMANCE_FILE(self) -> Path:
        return self.DATA_PROCESSED_DIR / "batter_performance.csv"

    @property
    def BOWLER_PERFORMANCE_FILE(self) -> Path:
        return self.DATA_PROCESSED_DIR / "bowler_performance.csv"

    @property
    def COMPETITION_BATTER_FILE(self) -> Path:
        return self.DATA_PROCESSED_DIR / "competition_batter_performance.csv"

    @property
    def COMPETITION_BOWLER_FILE(self) -> Path:
        return self.DATA_PROCESSED_DIR / "competition_bowler_performance.csv"

    # Audit Datasets
    @property
    def AFFECTED_INNINGS_FILE(self) -> Path:
        return self.DATA_PROCESSED_DIR / "affected_innings.csv"

    @property
    def MATCHES_MISSING_BALL_DATA_FILE(self) -> Path:
        return self.DATA_PROCESSED_DIR / "matches_missing_ball_data.csv"

    @property
    def VIOLATION_DELIVERIES_FILE(self) -> Path:
        return self.DATA_PROCESSED_DIR / "violation_deliveries.csv"

    @property
    def EXTENDED_INNINGS_FILE(self) -> Path:
        return self.DATA_PROCESSED_DIR / "extended_innings_audit.csv"

settings = Settings()
