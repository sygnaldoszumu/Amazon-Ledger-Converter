import pandas as pd

from amazon_ledger_converter.extration import read_csv, CSVFormat


def test_read_csv_passes_expected_arguments(monkeypatch):
    calls = {}

    def fake_read_csv(path, **kwargs):
        calls["path"] = path
        calls["kwargs"] = kwargs
        return pd.DataFrame()

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    read_csv(
        "fake/path.csv",
        CSVFormat(separator=";", encoding="latin-1", extra={"usecols": ["name"]}),
    )

    assert calls == {
        "path": "fake/path.csv",
        "kwargs": {
            "sep": ";",
            "encoding": "latin-1",
            "usecols": ["name"],
        },
    }
