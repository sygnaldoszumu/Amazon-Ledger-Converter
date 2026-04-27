# tests/test_extractor.py
from amazon_ledger_converter.extractor import *
from pathlib import Path
import pandas as pd


def test_exttract_csv_reads_basic_csv(tmp_path: Path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "date,name,amount\n"
        "2024-01-01,Alice,10.50\n"
        "2024-01-02,Bob,20.00\n",
        encoding="utf-8",
    )

    result = exttract_csv(
        csv_file,
        dtype={"name": "string", "amount": "float"},
        parse_dates=["date"],
    )

    expected = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "name": pd.Series(["Alice", "Bob"], dtype="string"),
            "amount": [10.50, 20.00],
        }
    )

    pd.testing.assert_frame_equal(result, expected)


def test_exttract_csv_supports_usecols(tmp_path: Path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "date,name,amount\n"
        "2024-01-01,Alice,10.50\n",
        encoding="utf-8",
    )

    result = exttract_csv(csv_file, usecols=["name", "amount"])

    expected = pd.DataFrame(
        {
            "name": ["Alice"],
            "amount": [10.50],
        }
    )

    pd.testing.assert_frame_equal(result, expected)
    
