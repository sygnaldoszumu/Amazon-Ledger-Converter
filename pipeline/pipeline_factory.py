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

    def _resolve_refs(self, rc: RuleConfig, refs: dict[str, str]) -> RuleConfig:
        """Replace $ref values in lookup_file and set_value.value with their resolved strings."""
        params = rc.params

        if rc.rule_type == "lookup":
            lookup_file = params.get("lookup_file", "")
            if isinstance(lookup_file, str) and lookup_file.startswith("$"):
                name = lookup_file[1:]
                if name not in refs:
                    raise ValueError(
                        f"Lookup rule references '${name}' but it was not found. "
                        f"Available: {sorted(refs.keys())}."
                    )
                params = {**params, "lookup_file": refs[name]}

        elif rc.rule_type == "set_value":
            value = params.get("value", "")
            if isinstance(value, str) and value.startswith("$"):
                name = value[1:]
                if name not in refs:
                    raise ValueError(
                        f"set_value references '${name}' but it was not found. "
                        f"Available: {sorted(refs.keys())}."
                    )
                params = {**params, "value": refs[name]}

        return rc if params is rc.params else RuleConfig(rule_type=rc.rule_type, params=params)

    def _build_rule_with_when(self, rc: RuleConfig, file_refs: dict[str, str]) -> tuple:
        rc = self._resolve_refs(rc, file_refs)
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

    def build_all(self, config: PipelineConfig, file_refs: dict[str, str] | None = None) -> dict[str, Pipeline]:
        refs = file_refs or {}
        global_rules = [self._build_rule_with_when(rc, refs) for rc in config.global_rules]

        pipelines = {}
        for tx_type, tx_config in config.transaction_types.items():
            type_rules = [self._build_rule_with_when(rc, refs) for rc in tx_config.rules]
            output_columns = self._collect_output_columns(config, tx_type)
            pipelines[tx_type] = Pipeline(
                rules=global_rules + type_rules,
                output_destination=tx_config.output_destination,
                output_columns=output_columns,
            )

        return pipelines
