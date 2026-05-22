from config.config_loader import PipelineConfig, RuleConfig
from pipeline.pipeline import Pipeline
from pipeline.rule_registry import RuleRegistry

MAPPING_RULE_TYPES = {
    "direct_mapping",
    "conditional_mapping",
    "set_value",
    "lookup",
    "compute",
}


class PipelineFactory:
    def __init__(self, registry: RuleRegistry | None = None) -> None:
        self._registry = registry or RuleRegistry()

    def _build_rule_with_when(self, rc: RuleConfig) -> tuple:
        when = rc.params.get("when")
        params_without_when = {k: v for k, v in rc.params.items() if k != "when"}
        rule_config_without_when = RuleConfig(rule_type=rc.rule_type, params=params_without_when)
        rule = self._registry.build(rule_config_without_when)
        return (rule, when)

    def _collect_output_columns(self, config: PipelineConfig, tx_type: str) -> set[str]:
        """Collect all target columns explicitly written by mapping rules."""
        columns = set()
        all_rules = list(config.global_rules) + list(config.transaction_types[tx_type].rules)
        for rc in all_rules:
            if rc.rule_type not in MAPPING_RULE_TYPES:
                continue
            params = rc.params
            if "target_column" in params:
                col = params["target_column"]
                if not col.startswith("_"):
                    columns.add(col)
            if rc.rule_type == "conditional_mapping":
                for condition in params.get("conditions", []):
                    col = condition.get("target_column")
                    if col and not col.startswith("_"):
                        columns.add(col)
        return columns

    def build_all(self, config: PipelineConfig) -> dict[str, Pipeline]:
        global_rules = [self._build_rule_with_when(rc) for rc in config.global_rules]

        pipelines = {}
        for tx_type, tx_config in config.transaction_types.items():
            type_rules = [self._build_rule_with_when(rc) for rc in tx_config.rules]
            output_columns = self._collect_output_columns(config, tx_type)
            pipelines[tx_type] = Pipeline(
                rules=global_rules + type_rules,
                output_destination=tx_config.output_destination,
                output_columns=output_columns,
            )

        return pipelines
