from dataclasses import dataclass
from rules.base import Rule, RuleResult
from rules.validation_utils import matches, is_invalid


@dataclass(frozen=True)
class PipelineResult:
    passed: bool
    output_destination: str | None = None
    transformed_row: dict | None = None
    failure_reason: str | None = None
    failed_rule_type: str | None = None

    @classmethod
    def ok(cls, output_destination: str, transformed_row: dict) -> "PipelineResult":
        return cls(passed=True, output_destination=output_destination, transformed_row=transformed_row)

    @classmethod
    def fail(cls, reason: str, failed_rule_type: str) -> "PipelineResult":
        return cls(passed=False, failure_reason=reason, failed_rule_type=failed_rule_type)


class Pipeline:
    """
    Runs an ordered list of rules against a row.
    Fail-fast: stops at the first failed rule.
    After each rule, checks explicitly mapped output columns for empty values.
    After all rules, does a final check that every output column was set.
    Returns only mapped output columns in transformed_row.
    Internal columns (prefixed with _) are excluded from all checks.
    """

    def __init__(
        self,
        rules: list[tuple[Rule, any]],
        output_destination: str,
        output_columns: set[str] | None = None,
    ) -> None:
        self._rules = rules
        self._output_destination = output_destination
        self._output_columns = output_columns or set()

    def _check_output_columns(self, row: dict, rule_name: str) -> PipelineResult | None:
        for key in self._output_columns:
            if key.startswith("_"):
                continue
            if key in row and is_invalid(row[key]):
                return PipelineResult.fail(
                    reason=f"Rule '{rule_name}' produced empty value for '{key}'.",
                    failed_rule_type=rule_name,
                )
        return None

    def execute(self, row: dict) -> PipelineResult:
        for rule, when_condition in self._rules:
            if when_condition is not None and not matches(when_condition, row):
                continue

            result: RuleResult = rule.execute(row)

            if not result.passed:
                return PipelineResult.fail(
                    reason=result.reason,
                    failed_rule_type=type(rule).__name__,
                )

            failure = self._check_output_columns(row, type(rule).__name__)
            if failure:
                return failure

        # final check — ensure every output column was set by some rule
        for key in self._output_columns:
            if key.startswith("_"):
                continue
            if key not in row or is_invalid(row.get(key)):
                return PipelineResult.fail(
                    reason=f"Output column '{key}' is empty or was never set.",
                    failed_rule_type="Pipeline",
                )

        return PipelineResult.ok(
            output_destination=self._output_destination,
            transformed_row={k: v for k, v in row.items() if k in self._output_columns},
        )
