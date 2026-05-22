
# csv_input_validation.py
import json
from pathlib import Path

def load_required_columns(config_path: str | Path) -> set[str]:
    with Path(config_path).open("r", encoding="utf-8") as f:
        config = json.load(f)

    columns = config.get("required_columns")
    if not isinstance(columns, list) or not all(isinstance(c, str) for c in columns):
        raise ValueError("config must contain required_columns as a list of strings")

    return set(columns)


# import pandas as pd

# REQUIRED_COLUMNS = {"date", "description", "amount", "currency"}

# def validate_amazon_ledger(df: pd.DataFrame) -> pd.DataFrame:
#     missing = REQUIRED_COLUMNS - set(df.columns)
#     if missing:
#         raise ValueError(f"Missing columns: {missing}")
#     if df["amount"].isnull().any(axis=0):
#         raise ValueError("amount column contains nulls")
#     return df
