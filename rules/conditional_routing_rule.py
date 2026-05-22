from rules.base import Rule, RuleResult


class ConditionalRoutingRule(Rule):
    ANY = "ANY"

    def __init__(self, conditions: list[dict]) -> None:
        self._conditions = conditions

    def _matches_one(self, when: dict, row: dict) -> bool:
        col = when["column"]
        row_value = row.get(col)
        if "equals" in when:
            expected = when["equals"]
            return expected == self.ANY or row_value == expected
        if "not_equals" in when:
            return row_value != when["not_equals"]
        return False

    def _matches(self, when, row: dict) -> bool:
        if isinstance(when, list):
            return all(self._matches_one(w, row) for w in when)
        return self._matches_one(when, row)

    def execute(self, row: dict) -> RuleResult:
        for condition in self._conditions:
            if self._matches(condition["when"], row):
                destination = condition["destination"]
                row["_transaction_type"] = destination
                return RuleResult.ok()

        return RuleResult.fail(
            f"Conditional routing failed: no condition matched for row."
        )
