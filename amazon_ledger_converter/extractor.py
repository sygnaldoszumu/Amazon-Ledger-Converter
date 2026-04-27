"""
extractor.py
---------
Module for extracting CSV data into Pandas DataFrames for ETL pipelines.
"""
import logging
from pathlib import Path
import os
import pandas as pd

logger = logging.getLogger(__name__)
# logging.info("Program started")
# logging.warning("Something may be wrong")
# logging.error("Something failed")

def exttract_csv(
    filepath: str | Path,
    *,
    dtype: dict | None = None,
    parse_dates: list[str] | None = None,
    usecols: list[str] | None = None,
    encoding: str = "utf-8",
    sep: str = ",",
) -> pd.DataFrame:
    """
    Load a single CSV file into a DataFrame.
    
    Args:
        filepath:     Path to the CSV file.
        dtype:        Column dtype overrides, e.g. {"id": str, "amount": float}.
        parse_dates:  Column names to parse as datetime.
        usecols:      Subset of columns to load (None = all columns).
        encoding:     File encoding (default: utf-8).
        sep:          Delimiter character (default: comma).

    Returns:
        pd.DataFrame

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError:        If the file is empty.
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    logger.info("Loading CSV: %s", filepath)

    df = pd.read_csv(
        filepath,
        dtype=dtype,
        parse_dates=parse_dates,
        usecols=usecols,
        encoding=encoding,
        sep=sep,
    )

    if df.empty:
        raise ValueError(f"File is empty: {filepath}")

    logger.info("Loaded %d rows × %d columns from %s", *df.shape, filepath.name)
    return df
