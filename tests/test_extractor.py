# tests/test_extractor.py
from amazon_ledger_converter.extractor import *
from pathlib import Path
import pandas as pd
import tempfile


def test_provide_csv_with_valid_path():
    """Vali fiel path is provided and returned"""
    with tempfile.NamedTemporaryFile(suffix=".csv") as temp_csv:
        result = provide_csv_path(temp_csv.name)
    assert result == temp_csv.name

def test_provide_csv_path_invalid_path_prints_error(monkeypatch, capsys, tmp_path):
    """Initial file path is invalid.
        Repeat until valid.
    """
    valid_csv = tmp_path / "valid.csv"
    valid_csv.write_text("a,b\n1,2\n")

    monkeypatch.setattr("builtins.input", lambda _: str(valid_csv))

    result = provide_csv_path("invalid.csv")

    captured = capsys.readouterr()

    assert result == str(valid_csv)
    assert "Error: The path 'invalid.csv' does not point to a real file. Please try again." in captured.out
    
def test_provide_csv_path_retries_until_valid(monkeypatch, tmp_path, capsys):
    csv_file = tmp_path / "valid.csv"
    csv_file.write_text("name,age\nAlice,30\n")

    inputs = iter([
        "missing.csv",
        str(csv_file),
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    result = provide_csv_path()

    assert result == str(csv_file)

    captured = capsys.readouterr()
    assert "does not point to a real file" in captured.out
    assert "missing.csv" in captured.out


def test_provide_csv_path_rejects_directory(monkeypatch, tmp_path, capsys):
    inputs = iter([
        str(tmp_path),
        str(tmp_path / "file.csv"),
    ])

    valid_file = tmp_path / "file.csv"
    valid_file.write_text("x,y\n1,2\n")

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    result = provide_csv_path()

    assert result == str(valid_file)

    captured = capsys.readouterr()
    assert "does not point to a real file" in captured.out

def test_empty_file_prompts_again(monkeypatch, capsys, tmp_path):
    empty_csv = tmp_path / "empty.csv"
    empty_csv.touch()

    valid_csv = tmp_path / "valid.csv"
    valid_csv.write_text("a,b\n1,2\n")

    monkeypatch.setattr("builtins.input", lambda _: str(valid_csv))

    result = provide_csv_path(str(empty_csv))

    captured = capsys.readouterr()

    assert result == str(valid_csv)
    assert "Error: The path" in captured.out
    assert "empty.csv" in captured.out
    
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
    
