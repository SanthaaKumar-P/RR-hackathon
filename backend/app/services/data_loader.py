import logging
import threading
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd
from app.core.config import settings

logger = logging.getLogger("superr_selector.data_loader")

class DataLoader:
    _instance: Optional["DataLoader"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "DataLoader":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DataLoader, cls).__new__(cls)
                cls._instance._cache = {}
                cls._instance._is_loaded = False
            return cls._instance

    def _read_csv_safe(self, path: Path, **kwargs) -> pd.DataFrame:
        if not path.exists():
            error_msg = f"Data file not found: {path.resolve()}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        try:
            df = pd.read_csv(path, **kwargs)
            logger.info(f"Loaded {path.name}: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"Error loading {path.resolve()}: {str(e)}")
            raise e

    def load_all_datasets(self) -> None:
        """Preloads datasets into memory cache safely."""
        with self._lock:
            if self._is_loaded:
                return

            logger.info("Initializing centralized in-memory dataset cache...")

            # Source of truth: Final rankings and sensitivity analysis
            self._cache["final_batter_rankings"] = self._read_csv_safe(settings.FINAL_BATTER_RANKINGS_FILE)
            self._cache["final_bowler_rankings"] = self._read_csv_safe(settings.FINAL_BOWLER_RANKINGS_FILE)
            self._cache["top10_batters"] = self._read_csv_safe(settings.TOP10_BATTERS_FILE)
            self._cache["top10_bowlers"] = self._read_csv_safe(settings.TOP10_BOWLERS_FILE)
            self._cache["ranking_sensitivity"] = self._read_csv_safe(settings.RANKING_SENSITIVITY_FILE)
            self._cache["bowler_accounting_sensitivity"] = self._read_csv_safe(settings.BOWLER_ACCOUNTING_SENSITIVITY_FILE)

            # Match & situation datasets
            self._cache["target_matches"] = self._read_csv_safe(settings.TARGET_MATCHES_FILE)
            self._cache["innings_summary"] = self._read_csv_safe(settings.INNINGS_SUMMARY_FILE)

            # Competition and overall performance data
            if settings.COMPETITION_BATTER_FILE.exists():
                self._cache["competition_batter"] = self._read_csv_safe(settings.COMPETITION_BATTER_FILE)
            if settings.COMPETITION_BOWLER_FILE.exists():
                self._cache["competition_bowler"] = self._read_csv_safe(settings.COMPETITION_BOWLER_FILE)
            if settings.BATTER_PERFORMANCE_FILE.exists():
                self._cache["batter_performance"] = self._read_csv_safe(settings.BATTER_PERFORMANCE_FILE)
            if settings.BOWLER_PERFORMANCE_FILE.exists():
                self._cache["bowler_performance"] = self._read_csv_safe(settings.BOWLER_PERFORMANCE_FILE)

            # Pressure classified dataset (Large CSV, cached once)
            self._cache["pressure_classified"] = self._read_csv_safe(settings.PRESSURE_CLASSIFIED_FILE)

            # Methodology text
            if settings.METHODOLOGY_FILE.exists():
                self._cache["methodology_text"] = settings.METHODOLOGY_FILE.read_text(encoding="utf-8")
            else:
                self._cache["methodology_text"] = ""

            # Audit files
            for key, path in [
                ("affected_innings", settings.AFFECTED_INNINGS_FILE),
                ("matches_missing_ball_data", settings.MATCHES_MISSING_BALL_DATA_FILE),
                ("violation_deliveries", settings.VIOLATION_DELIVERIES_FILE),
                ("extended_innings", settings.EXTENDED_INNINGS_FILE),
                ("innings_validation", settings.INNINGS_VALIDATION_FILE)
            ]:
                if path.exists():
                    self._cache[key] = self._read_csv_safe(path)

            self._is_loaded = True
            logger.info("All datasets successfully loaded into memory cache.")

    def get_final_batter_rankings(self) -> pd.DataFrame:
        if "final_batter_rankings" not in self._cache:
            self._cache["final_batter_rankings"] = self._read_csv_safe(settings.FINAL_BATTER_RANKINGS_FILE)
        return self._cache["final_batter_rankings"].copy()

    def get_final_bowler_rankings(self) -> pd.DataFrame:
        if "final_bowler_rankings" not in self._cache:
            self._cache["final_bowler_rankings"] = self._read_csv_safe(settings.FINAL_BOWLER_RANKINGS_FILE)
        return self._cache["final_bowler_rankings"].copy()

    def get_top10_batters(self) -> pd.DataFrame:
        if "top10_batters" not in self._cache:
            self._cache["top10_batters"] = self._read_csv_safe(settings.TOP10_BATTERS_FILE)
        return self._cache["top10_batters"].copy()

    def get_top10_bowlers(self) -> pd.DataFrame:
        if "top10_bowlers" not in self._cache:
            self._cache["top10_bowlers"] = self._read_csv_safe(settings.TOP10_BOWLERS_FILE)
        return self._cache["top10_bowlers"].copy()

    def get_ranking_sensitivity(self) -> pd.DataFrame:
        if "ranking_sensitivity" not in self._cache:
            self._cache["ranking_sensitivity"] = self._read_csv_safe(settings.RANKING_SENSITIVITY_FILE)
        return self._cache["ranking_sensitivity"].copy()

    def get_bowler_accounting_sensitivity(self) -> pd.DataFrame:
        if "bowler_accounting_sensitivity" not in self._cache:
            self._cache["bowler_accounting_sensitivity"] = self._read_csv_safe(settings.BOWLER_ACCOUNTING_SENSITIVITY_FILE)
        return self._cache["bowler_accounting_sensitivity"].copy()

    def get_target_matches(self) -> pd.DataFrame:
        if "target_matches" not in self._cache:
            self._cache["target_matches"] = self._read_csv_safe(settings.TARGET_MATCHES_FILE)
        return self._cache["target_matches"].copy()

    def get_pressure_classified(self) -> pd.DataFrame:
        if "pressure_classified" not in self._cache:
            self._cache["pressure_classified"] = self._read_csv_safe(settings.PRESSURE_CLASSIFIED_FILE)
        return self._cache["pressure_classified"].copy()

    def get_innings_summary(self) -> pd.DataFrame:
        if "innings_summary" not in self._cache:
            self._cache["innings_summary"] = self._read_csv_safe(settings.INNINGS_SUMMARY_FILE)
        return self._cache["innings_summary"].copy()

    def get_competition_batter(self) -> Optional[pd.DataFrame]:
        return self._cache.get("competition_batter", None)

    def get_competition_bowler(self) -> Optional[pd.DataFrame]:
        return self._cache.get("competition_bowler", None)

    def get_batter_performance(self) -> Optional[pd.DataFrame]:
        return self._cache.get("batter_performance", None)

    def get_bowler_performance(self) -> Optional[pd.DataFrame]:
        return self._cache.get("bowler_performance", None)

    def get_methodology_text(self) -> str:
        return self._cache.get("methodology_text", "")

    def get_audit_dataset(self, key: str) -> Optional[pd.DataFrame]:
        return self._cache.get(key, None)

data_loader = DataLoader()
