from pipeline.pipeline import Pipeline
from config.config_loader import PipelineConfig


class Router:
    ANY = "ANY"
    IGNORE_DESTINATIONS = {"ignore"}

    def __init__(self, pipelines: dict[str, Pipeline], config: PipelineConfig) -> None:
        self._pipelines = pipelines
        self._conditions = self._extract_conditions(config)
        self._fallback = Pipeline(rules=[], output_destination="other")

    def _extract_conditions(self, config: PipelineConfig) -> list[dict]:
        for rule in config.global_rules:
            if rule.rule_type == "conditional_routing":
                return rule.params["conditions"]
        return []

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

    def route(self, row: dict) -> Pipeline:
        for condition in self._conditions:
            if self._matches(condition["when"], row):
                destination = condition["destination"]
                if destination in self.IGNORE_DESTINATIONS:
                    return Pipeline(rules=[], output_destination="other")
                return self._pipelines.get(destination, self._fallback)

        return self._fallback
