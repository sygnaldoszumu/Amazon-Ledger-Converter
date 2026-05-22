from abc import ABC, abstractmethod
from dataclasses import dataclass

##################################################################################
# ├── config/                                                                    #
# │   ├── __init__.py                                                            #
# │   └── config_loader.py                                                       #
# ├── rules/                                                                     #
# │   ├── __init__.py                                                            #
# │   ├── base.py                                                                #
# │   ├── validation_utils.py                                                    #
# │   ├── routing_rule.py                                                        #
# │   ├── required_fields_rule.py                                                #
# │   ├── type_validation_rule.py                                                #
# │   ├── format_validation_rule.py                                              #
# │   ├── direct_mapping_rule.py                                                 #
# │   └── conditional_mapping_rule.py                                            #
# ├── pipeline/                                                                  #
# │   ├── __init__.py                                                            #
# │   ├── pipeline.py                                                            #
# │   ├── pipeline_factory.py                                                    #
# │   └── rule_registry.py                                                       #
# ├── orchestration/                                                             #
# │   ├── __init__.py                                                            #
# │   ├── router.py                                                              #
# │   └── etl_processor.py                                                       #
# ├── output/                                                                    #
# │   ├── __init__.py                                                            #
# │   └── output_collector.py                                                    #
# └── tests/                                                                     #
#     ├── config/     → test_config_loader.py                                    #
#     ├── rules/      → test_base, test_validation_utils, + one per rule         #
#     ├── pipeline/   → test_pipeline, test_pipeline_factory, test_rule_registry #
#     ├── orchestration/ → test_router, test_etl_processor                       #
#     └── output/     → test_output_collector                                    #
##################################################################################

@dataclass(frozen=True)
class RuleResult:
    passed: bool
    reason: str | None = None

    @classmethod
    def ok(cls) -> "RuleResult":
        return cls(passed=True)

    @classmethod
    def fail(cls, reason: str) -> "RuleResult":
        return cls(passed=False, reason=reason)

class Rule(ABC):
    @abstractmethod
    def execute(self, row: dict) -> RuleResult:
        pass
