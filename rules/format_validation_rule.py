import re
from rules.required_fields_rule import ValidationRule
from rules.base import RuleResult


class FormatValidationRule(ValidationRule):
    """
    Checks a field against a regex pattern or an allowed value set.
    Provide exactly one of: pattern or allowed_values.
    """

    def __init__(
        self,
        field: str,
        pattern: str | None = None,
        allowed_values: list | None = None,
    ) -> None:
        if pattern is None and allowed_values is None:
            raise ValueError(
                f"FormatValidationRule for '{field}' requires either 'pattern' or 'allowed_values'."
            )
        if pattern is not None and allowed_values is not None:
            raise ValueError(
                f"FormatValidationRule for '{field}' accepts 'pattern' or 'allowed_values', not both."
            )

        self._field_name = field
        self._pattern = re.compile(pattern) if pattern is not None else None
        self._allowed_values = set(allowed_values) if allowed_values is not None else None

    def _field(self) -> str:
        return self._field_name

    def _validate(self, field: str, value, row: dict) -> RuleResult:
        if self._pattern is not None:
            if not isinstance(value, str):
                return RuleResult.fail(
                    f"Format validation failed: field '{field}' must be a string for regex "
                    f"matching but got {type(value).__name__}."
                )
            if not self._pattern.fullmatch(value):
                return RuleResult.fail(
                    f"Format validation failed: field '{field}' value {value!r} "
                    f"does not match pattern '{self._pattern.pattern}'."
                )

        if self._allowed_values is not None:
            if value not in self._allowed_values:
                return RuleResult.fail(
                    f"Format validation failed: field '{field}' value {value!r} "
                    f"is not in allowed values {sorted(str(v) for v in self._allowed_values)}."
                )

        return RuleResult.ok()
