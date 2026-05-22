from rules.base import Rule, RuleResult


class ConditionalMappingRule(Rule):
    """
    Evaluates a condition on the row and maps the appropriate
    source column to the target column.

    conditions is a list of dicts, evaluated in order:
        [
            {
                "when": {"column": "type", "equals": "sale"},
                "source_column": "order_id",
                "target_column": "invoice_id"
            },
            ...
        ]

    The first matching condition wins (short-circuit).
    Fails if no condition matches and no default is provided.
    """

    def __init__(self, conditions: list[dict], default_source: str | None = None) -> None:
        self._conditions = conditions
        self._default_source = default_source

    def execute(self, row: dict) -> RuleResult:
        for condition in self._conditions:
            when = condition["when"]
            col = when["column"]
            expected = when["equals"]

            if row.get(col) == expected:
                source = condition["source_column"]
                target = condition["target_column"]

                if source not in row:
                    return RuleResult.fail(
                        f"Conditional mapping failed: matched condition but source column "
                        f"'{source}' not found in row."
                    )

                row[target] = row[source]
                return RuleResult.ok()

        if self._default_source is not None:
            target = self._conditions[0]["target_column"]
            if self._default_source not in row:
                return RuleResult.fail(
                    f"Conditional mapping failed: no condition matched and default source "
                    f"column '{self._default_source}' not found in row."
                )
            row[target] = row[self._default_source]
            return RuleResult.ok()

        row_type = row.get("_transaction_type", "unknown")
        return RuleResult.fail(
            f"Conditional mapping failed: no condition matched for transaction type '{row_type}' "
            f"and no default is configured."
        )
