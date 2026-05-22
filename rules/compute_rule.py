from typing import Callable
from rules.base import Rule, RuleResult


class ComputeRule(Rule):
    """
    Calls a registered Python function and writes the result to a target column.

    Arguments are declared via `inputs` — an ordered list of column lookups
    and/or literal values, which maps directly to the function's positional
    parameter order:

        inputs:
          - column: Currency               # resolved from the row at runtime
          - raw: PLN                       # passed as the literal string "PLN"
          - column: TRANSACTION_COMPLETE_DATE

    Legacy shorthand (all column-sourced, no literals) is still accepted:

        input_columns:
          - Currency
          - TRANSACTION_COMPLETE_DATE

    `input_columns` and `inputs` are mutually exclusive.

    If the function raises or returns None the row goes to manual_review.
    """

    _registry: dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, func: Callable) -> None:
        cls._registry[name] = func

    @classmethod
    def registered(cls) -> list[str]:
        return sorted(cls._registry.keys())

    def __init__(
        self,
        func: str,
        target_column: str,
        inputs: list[dict] | None = None,
        input_columns: list[str] | None = None,
    ) -> None:
        if inputs is not None and input_columns is not None:
            raise ValueError(
                "ComputeRule: specify either 'inputs' or 'input_columns', not both."
            )
        if inputs is None and input_columns is None:
            raise ValueError(
                "ComputeRule: one of 'inputs' or 'input_columns' is required."
            )

        # Normalise to the unified internal format:
        # [{"column": "X"} | {"raw": <value>}, ...]
        if inputs is not None:
            self._inputs = inputs
        else:
            self._inputs = [{"column": col} for col in input_columns]

        self._target_column = target_column
        self._func_name = func

        if func not in self._registry:
            raise ValueError(
                f"ComputeRule: function '{func}' is not registered. "
                f"Registered functions: {self.registered()}. "
                f"Call ComputeRule.register('{func}', your_function) before building pipelines."
            )
        self._func = self._registry[func]

    def execute(self, row: dict) -> RuleResult:
        args = []
        for entry in self._inputs:
            if "column" in entry:
                col = entry["column"]
                val = row.get(col)
                if val is None:
                    return RuleResult.fail(
                        f"Compute '{self._func_name}' failed: "
                        f"input column '{col}' is missing or null."
                    )
                args.append(val)
            elif "raw" in entry:
                args.append(entry["raw"])
            else:
                return RuleResult.fail(
                    f"Compute '{self._func_name}' failed: "
                    f"unrecognised input entry {entry!r} — use 'column' or 'raw'."
                )

        try:
            result = self._func(*args)
        except Exception as e:
            return RuleResult.fail(
                f"Compute '{self._func_name}' failed: "
                f"raised {type(e).__name__}: {e}"
            )

        if result is None:
            return RuleResult.fail(
                f"Compute '{self._func_name}' returned None. "
                f"Resolved args: {args}."
            )

        row[self._target_column] = result
        return RuleResult.ok()
