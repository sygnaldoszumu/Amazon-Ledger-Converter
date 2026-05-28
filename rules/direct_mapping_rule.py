from rules.base import Rule, RuleResult

_MISSING = object()


class DirectMappingRule(Rule):
    """
    Copies source_column → target_column.
    If the source value is empty/None, uses fallback_column or fallback_value (in that order).
    Fails if source_column is missing from the row.
    """

    def __init__(
        self,
        source_column: str,
        target_column: str,
        fallback_column: str | None = None,
        fallback_value=_MISSING,
    ) -> None:
        self._source_column = source_column
        self._target_column = target_column
        self._fallback_column = fallback_column
        self._fallback_value = fallback_value

    def execute(self, row: dict) -> RuleResult:
        if self._source_column not in row:
            return RuleResult.fail(
                f"Direct mapping failed: source column '{self._source_column}' not found in row."
            )

        value = row[self._source_column]

        if value in (None, ""):
            if self._fallback_column is not None:
                if self._fallback_column not in row:
                    return RuleResult.fail(
                        f"Direct mapping failed: fallback column '{self._fallback_column}' not found in row."
                    )
                value = row[self._fallback_column]
            elif self._fallback_value is not _MISSING:
                value = self._fallback_value

        row[self._target_column] = value
        return RuleResult.ok()
