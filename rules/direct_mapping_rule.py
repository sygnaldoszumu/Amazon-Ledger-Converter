from rules.base import Rule, RuleResult


class DirectMappingRule(Rule):
    """
    Copies source_column → target_column unconditionally.
    Fails if source_column is missing from the row.
    """

    def __init__(self, source_column: str, target_column: str) -> None:
        self._source_column = source_column
        self._target_column = target_column

    def execute(self, row: dict) -> RuleResult:
        if self._source_column not in row:
            return RuleResult.fail(
                f"Direct mapping failed: source column '{self._source_column}' not found in row."
            )

        row[self._target_column] = row[self._source_column]
        return RuleResult.ok()
