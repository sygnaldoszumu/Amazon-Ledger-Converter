from rules.base import Rule, RuleResult


class IgnoreIfRule(Rule):
    """
    If the specified field equals the specified value, the row is
    silently skipped — it goes to 'other', not manual_review.

    Strips whitespace from both the row value and the configured
    value before comparing, to handle dirty CSV data.
    """

    def __init__(self, field: str, equals: str) -> None:
        self._field = field
        self._equals = equals.strip()

    def execute(self, row: dict) -> RuleResult:
        value = row.get(self._field)
        if isinstance(value, str) and value.strip() == self._equals:
            return RuleResult.fail(
                reason=f"Row ignored: {self._field} = '{value.strip()}'."
            )
        return RuleResult.ok()
