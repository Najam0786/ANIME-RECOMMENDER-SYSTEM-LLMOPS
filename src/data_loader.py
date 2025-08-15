import pandas as pd
from typing import Dict, Set
from utils.custom_exception import CustomException
from utils.logger import get_logger

logger = get_logger(__name__)

class AnimeDataLoader:
    """
    Robust data loader for anime datasets with comprehensive validation and processing.
    Handles:
    - Column name normalization and validation
    - Data quality checks
    - Text field combination
    - Safe file operations
    """

    # Class-level constants
    REQUIRED_COLUMNS: Set[str] = {'name', 'genres', 'synopsis'}
    COMMON_TYPO_MAPPING: Dict[str, str] = {
        'synopsys': 'synopsis',
        'sypnopsis': 'synopsis',
        'genre': 'genres',
        'title': 'name'
    }

    def __init__(self, original_csv: str, processed_csv: str):
        """
        Args:
            original_csv: Path to source CSV file
            processed_csv: Path to save processed data
        """
        self.original_csv = original_csv
        self.processed_csv = processed_csv

    def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names and fix common typos."""
        # Basic cleaning
        df.columns = (
            df.columns
            .str.strip()
            .str.replace('\ufeff', '', regex=False)
            .str.replace(r"\s+", "_", regex=True)
            .str.lower()
        )

        # Fix common typos
        for typo, correct in self.COMMON_TYPO_MAPPING.items():
            if typo in df.columns:
                df.rename(columns={typo: correct}, inplace=True)
                logger.info(f"Renamed column '{typo}' to '{correct}'")

        return df

    def _validate_data(self, df: pd.DataFrame) -> None:
        """Ensure data meets quality requirements."""
        # Check required columns
        missing = self.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            logger.error(f"Missing required columns: {missing}")
            raise ValueError(f"Missing required columns: {missing}")

        # Check for empty data
        if df.empty:
            raise ValueError("Input CSV file is empty")

        # Check for nulls in critical columns
        for col in self.REQUIRED_COLUMNS:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                logger.warning(f"Column '{col}' has {null_count} null values")

    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Combine relevant fields into a single text column."""
        try:
            df["combined_info"] = (
                "Title: " + df["name"].str.strip() + " | " +
                "Overview: " + df["synopsis"].str.strip() + " | " +
                "Genres: " + df["genres"].str.strip()
            )
            logger.info(f"Created combined_info column with {len(df)} entries")
            return df[["combined_info"]]
        except KeyError as e:
            raise CustomException("Missing required column for processing", e,
                                {"available_columns": df.columns.tolist()})
        except Exception as e:
            raise CustomException("Error combining text fields", e)

    def load_and_process(self) -> str:
        """Orchestrate the complete data loading and processing pipeline."""
        try:
            # Load data
            logger.info(f"Loading data from {self.original_csv}")
            df = pd.read_csv(
                self.original_csv,
                encoding='utf-8',
                on_bad_lines='warn',  # Changed from 'skip' to 'warn' to be more explicit
                dtype={'name': 'str', 'genres': 'str', 'synopsis': 'str'}
            )
            logger.info(f"Initial data shape: {df.shape}")

            # Clean and validate
            df = self._clean_column_names(df)
            logger.debug(f"Cleaned columns: {df.columns.tolist()}")
            self._validate_data(df)

            # Process and save
            processed_df = self._process_data(df)
            processed_df.to_csv(self.processed_csv, index=False, encoding='utf-8')
            logger.info(f"Successfully saved processed data to {self.processed_csv}")

            return self.processed_csv

        except pd.errors.EmptyDataError:
            raise CustomException("Input CSV file is empty")
        except FileNotFoundError:
            raise CustomException("Input CSV file not found")
        except Exception as e:
            raise CustomException("Failed to process anime data", e)
