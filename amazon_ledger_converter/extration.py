import pandas as pd
from dataclasses import dataclass, field

@dataclass
class CSVFormat:
    separator: str = ","
    encoding: str = "utf-8"
    extra: dict = field(default_factory=dict)

def read_csv(path: str, fmt: CSVFormat = CSVFormat()) -> pd.DataFrame:
    return pd.read_csv(path, sep=fmt.separator, encoding=fmt.encoding, **fmt.extra)
