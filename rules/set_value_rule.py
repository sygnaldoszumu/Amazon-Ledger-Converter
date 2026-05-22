from rules.base import Rule, RuleResult


class SetValueRule(Rule):
    """
    Sets a target column to a fixed hardcoded value.
    Conditional execution is handled by the Pipeline via the 'when' key —
    this rule always sets the value when it runs.
    """

    def __init__(self, target_column: str, value) -> None:
        self._target_column = target_column
        self._value = value

    def execute(self, row: dict) -> RuleResult:
        row[self._target_column] = self._value
        return RuleResult.ok()
