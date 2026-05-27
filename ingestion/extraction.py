import pandas as pd
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class CSVFormat:
    separator: str = ","
    encoding: str = "utf-8"
    extra: dict = field(default_factory=dict)

def read_csv(path, fmt: CSVFormat | None = None) -> pd.DataFrame:
    if Path(path).suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(path, sheet_name=0, dtype=str)
    fmt = fmt or CSVFormat()
    return pd.read_csv(path, sep=fmt.separator, encoding=fmt.encoding, **fmt.extra)
