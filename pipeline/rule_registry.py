from rules.base import Rule
from rules.routing_rule import RoutingRule
from rules.conditional_routing_rule import ConditionalRoutingRule
from rules.required_fields_rule import RequiredFieldsRule
from rules.type_validation_rule import TypeValidationRule
from rules.format_validation_rule import FormatValidationRule
from rules.direct_mapping_rule import DirectMappingRule
from rules.conditional_mapping_rule import ConditionalMappingRule
from config.config_loader import RuleConfig
from rules.ignore_if_rule import IgnoreIfRule
from rules.set_value_rule import SetValueRule
from rules.lookup_rule import LookupRule
from rules.ignore_if_rule import IgnoreIfRule
from rules.compute_rule import ComputeRule

class RuleRegistry:
    _registry: dict[str, type[Rule]] = {
        "routing":              RoutingRule,
        "conditional_routing":  ConditionalRoutingRule,
        "required_fields":      RequiredFieldsRule,
        "type_validation":      TypeValidationRule,
        "format_validation":    FormatValidationRule,
        "direct_mapping":       DirectMappingRule,
        "conditional_mapping":  ConditionalMappingRule,
        "ignore_if": IgnoreIfRule,
        "set_value": SetValueRule,
        "lookup": LookupRule,
        "compute": ComputeRule,
        
    }

    def build(self, rule_config: RuleConfig) -> Rule:
        rule_class = self._registry.get(rule_config.rule_type)
        if rule_class is None:
            raise ValueError(
                f"No rule registered for type '{rule_config.rule_type}'. "
                f"Registered types: {sorted(self._registry.keys())}."
            )
        return rule_class(**rule_config.params)
