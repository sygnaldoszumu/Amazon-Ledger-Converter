import pandas as pd
from pathlib import Path
from rules.base import Rule, RuleResult


class LookupRule(Rule):
    """
    Looks up a value from an external CSV file based on one or more
    key columns in the row.

    Single key:
        key_columns: UNIQUE_ACCOUNT_IDENTIFIER

    Composite key (e.g. currency + date → exchange rate):
        key_columns:
          - TRANSACTION_CURRENCY_CODE
          - TRANSACTION_COMPLETE_DATE

    The composite key is built by joining the values with '|' internally.
    The lookup CSV must have a matching composite key column, or separate
    columns that are joined the same way via lookup_key_columns.

    Config params:
        key_columns           — str or list of str: columns in the row to build the key from
        lookup_file           — path to the CSV file
        lookup_key_columns    — str or list of str: columns in the CSV to match against
        lookup_value_column   — column in the CSV containing the value to map
        target_column         — column to write the looked-up value into on the row
        default               — optional fallback if key not found;
                                if omitted, missing keys send the row to manual_review
        separator             — separator used to join composite keys (default: |)
    """

    DEFAULT_SEP = "|"

    def __init__(
        self,
        key_columns,
        lookup_file: str,
        lookup_key_columns,
        lookup_value_column: str,
        target_column: str,
        default=None,
        separator: str = DEFAULT_SEP,
    ) -> None:
        self._key_columns = [key_columns] if isinstance(key_columns, str) else key_columns
        self._lookup_key_columns = [lookup_key_columns] if isinstance(lookup_key_columns, str) else lookup_key_columns
        self._target_column = target_column
        self._default = default
        self._has_default = default is not None
        self._sep = separator
        self._lookup = self._load(lookup_file, lookup_value_column)

    def _build_key(self, values: list) -> str:
        return self._sep.join(str(v).strip() for v in values)

    def _load(self, path: str, value_col: str) -> dict:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"LookupRule: lookup file not found: {p}")

        if p.suffix.lower() in (".xlsx", ".xls"):
            df = pd.read_excel(p, sheet_name=0, dtype=str)
        else:
            df = pd.read_csv(p, dtype=str)

        df.columns = df.columns.str.strip()

        for col in self._lookup_key_columns:
            if col not in df.columns:
                raise KeyError(
                    f"LookupRule: key column '{col}' not found in lookup file.\n"
                    f"Available columns: {df.columns.tolist()}"
                )
            df[col] = df[col].str.strip()

        if value_col not in df.columns:
            raise KeyError(
                f"LookupRule: value column '{value_col}' not found in lookup file.\n"
                f"Available columns: {df.columns.tolist()}"
            )
        df[value_col] = df[value_col].str.strip()

        composite_key = df[self._lookup_key_columns].apply(
            lambda row: self._build_key(row.tolist()), axis=1
        )
        return dict(zip(composite_key, df[value_col]))

    def execute(self, row: dict) -> RuleResult:
        values = []
        for col in self._key_columns:
            val = row.get(col)
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return RuleResult.fail(
                    f"Lookup failed: key column '{col}' is missing or null."
                )
            values.append(val)

        key = self._build_key(values)
        value = self._lookup.get(key)

        if value is None:
            if self._has_default:
                row[self._target_column] = self._default
                return RuleResult.ok()
            return RuleResult.fail(
                f"Lookup failed: no match found for key '{key}' in lookup file."
            )

        row[self._target_column] = value
        return RuleResult.ok()
