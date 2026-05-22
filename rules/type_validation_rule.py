from rules.required_fields_rule import ValidationRule
from rules.base import RuleResult

TYPE_MAP: dict[str, type] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


class TypeValidationRule(ValidationRule):
    """
    Checks that a field's value is of the expected Python type.
    Accepts type as a string (e.g. "int") or a Python type directly.
    """

    def __init__(self, field: str, expected_type: str | type) -> None:
        self._field_name = field

        if isinstance(expected_type, str):
            if expected_type not in TYPE_MAP:
                raise ValueError(
                    f"Unknown type string '{expected_type}'. "
                    f"Supported: {list(TYPE_MAP.keys())}."
                )
            self._expected_type = TYPE_MAP[expected_type]
            self._type_label = expected_type
        else:
            self._expected_type = expected_type
            self._type_label = expected_type.__name__

    def _field(self) -> str:
        return self._field_name

    def _validate(self, field: str, value, row: dict) -> RuleResult:
        if not isinstance(value, self._expected_type):
            return RuleResult.fail(
                f"Type validation failed: field '{field}' expected {self._type_label} "
                f"but got {type(value).__name__} with value {value!r}."
            )
        return RuleResult.ok()
