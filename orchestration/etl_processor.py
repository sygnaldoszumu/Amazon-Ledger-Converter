import pandas as pd
from orchestration.router import Router
from output.output_collector import OutputCollector
from pipeline.pipeline import PipelineResult
from rules.ignore_if_rule import IgnoreIfRule


class ETLProcessor:
    def __init__(self, router: Router, collector: OutputCollector) -> None:
        self._router = router
        self._collector = collector

    def process(self, df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        for _, raw_row in df.iterrows():
            row = raw_row.to_dict()
            pipeline = self._router.route(row)
            result: PipelineResult = pipeline.execute(row)
            # print(repr(row.get("TAX_REPORTING_SCHEME")), result.passed, result.failed_rule_type)

            if result.passed:
                self._collector.add(result.output_destination, result.transformed_row)
            elif result.failed_rule_type == IgnoreIfRule.__name__:
                self._collector.add("other", row)
            else:
                self._collector.add_failed(
                    original_row=row,
                    failure_reason=result.failure_reason,
                    failed_rule_type=result.failed_rule_type,
                )

        return self._collector.finalise()
