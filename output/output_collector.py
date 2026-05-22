import pandas as pd


class OutputCollector:
    """
    Accumulates transformed rows into named buckets.
    Materialises each bucket into a DataFrame when finalise() is called.
    The manual_review bucket includes the original row plus
    failure_reason and failed_rule_type columns.
    """

    MANUAL_REVIEW = "manual_review"

    def __init__(self) -> None:
        self._buckets: dict[str, list[dict]] = {}

    def add(self, destination: str, row: dict) -> None:
        self._buckets.setdefault(destination, []).append(row)

    def add_failed(self, original_row: dict, failure_reason: str, failed_rule_type: str) -> None:
        review_row = {
            **original_row,
            "failure_reason": failure_reason,
            "failed_rule_type": failed_rule_type,
        }
        self.add(self.MANUAL_REVIEW, review_row)

    def finalise(self) -> dict[str, pd.DataFrame]:
        return {
            destination: pd.DataFrame(rows)
            for destination, rows in self._buckets.items()
        }
