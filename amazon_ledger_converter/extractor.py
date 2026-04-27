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

def provide_csv_path(csv_path=None):
    """
    Returns a valid file path to a file that is not empty.
    If csv_path is provided, it validates and returns it.
    Otherwise, prompts the user until a valid file path is provided.
    """
    if csv_path is not None:
        if os.path.isfile(csv_path):
            if os.path.getsize(csv_path) > 0:
                return csv_path
            else:
                print(f"Error: The file '{csv_path}' is empty. Please try again.")
                
        else:
            print(f"Error: The path '{csv_path}' does not point to a real file. Please try again.")

    while True:
        csv_path = input("Please enter the path to the CSV file: ")

        if os.path.isfile(csv_path):
            if os.path.getsize(csv_path) > 0:
                return csv_path
            else:
                print(f"Error: The file '{csv_path}' is empty. Please try again.")
        else:
            print(f"Error: The path '{csv_path}' does not point to a real file. Please try again.")
            

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
