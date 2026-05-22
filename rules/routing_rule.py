from rules.base import Rule, RuleResult


class RoutingRule(Rule):
    """
    Reads the routing column and sets the resolved transaction
    type onto the row under the key '_transaction_type'.
    Fails if the column is missing or the value is not in known_types.
    """

    def __init__(self, type_column: str, known_types: list[str]) -> None:
        self._type_column = type_column
        self._known_types = set(known_types)

    def execute(self, row: dict) -> RuleResult:
        if self._type_column not in row:
            return RuleResult.fail(
                f"Routing failed: column '{self._type_column}' not found in row."
            )

        value = row[self._type_column]

        if not isinstance(value, str) or value.strip() == "":
            return RuleResult.fail(
                f"Routing failed: column '{self._type_column}' has invalid value '{value}'."
            )

        if value not in self._known_types:
            return RuleResult.fail(
                f"Routing failed: transaction type '{value}' is not recognized. "
                f"Known types: {sorted(self._known_types)}."
            )

        row["_transaction_type"] = value
        return RuleResult.ok()
