from abc import abstractmethod
from rules.base import Rule, RuleResult
from rules import validation_utils


class ValidationRule(Rule):
    """
    Abstract base for all validation rules (Template Method pattern).

    Skeleton:
        1. Extract the field value          — implemented here
        2. Check for invalid values         — implemented here (calls validation_utils)
        3. Apply rule-specific validation   — implemented by each subclass
        4. Return RuleResult                — implemented here
    """

    def execute(self, row: dict) -> RuleResult:
        field = self._field()
        if field not in row:
            return RuleResult.fail(f"Validation failed: field '{field}' not found in row.")

        value = row[field]

        if validation_utils.is_invalid(value):
            return RuleResult.fail(
                f"Validation failed: field '{field}' has invalid value {value!r} "
                f"(None, NaN, or empty string)."
            )

        return self._validate(field, value, row)

    @abstractmethod
    def _field(self) -> str:
        """Return the name of the field this rule operates on."""

    @abstractmethod
    def _validate(self, field: str, value, row: dict) -> RuleResult:
        """Apply rule-specific validation logic. Value is guaranteed non-null/non-empty."""


class RequiredFieldsRule(ValidationRule):
    """
    Confirms that each specified field exists and is not null / empty / NaN.
    Fails fast on the first invalid field found.
    """

    def __init__(self, fields: list[str]) -> None:
        self._fields = fields
        # ValidationRule.execute handles a single field at a time;
        # we override execute here to iterate over all required fields.

    def execute(self, row: dict) -> RuleResult:
        for field in self._fields:
            if field not in row:
                return RuleResult.fail(
                    f"Required field '{field}' is missing from the row."
                )
            value = row[field]
            if validation_utils.is_invalid(value):
                return RuleResult.fail(
                    f"Required field '{field}' has invalid value {value!r} "
                    f"(None, NaN, or empty string)."
                )
        return RuleResult.ok()

    # _field and _validate are not used because execute is overridden,
    # but we must satisfy the abstract contract.
    def _field(self) -> str:  # pragma: no cover
        return ""

    def _validate(self, field: str, value, row: dict) -> RuleResult:  # pragma: no cover
        return RuleResult.ok()
