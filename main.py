import pandas as pd
import shutil
import sys

from pathlib import Path

if getattr(sys, "frozen", False):
    _PROJECT_ROOT = Path(sys.executable).parent
else:
    _PROJECT_ROOT = Path(__file__).parent

from config.config_loader import *
from pipeline.pipeline_factory import *
from pipeline.rule_registry import *
from orchestration.router import *
from orchestration.etl_processor import *
from output.output_collector import *
from output.output_writer import write_outputs_to_xlsx
from ingestion.extraction import *

from utilities.validate_row_counts import *
from utilities.nbp_currency import get_exchange_rate, get_valid_date
from utilities.multiply import multiply
from utilities.sum import sum
from utilities.get_file_contents import get_file_contents

from utilities.config_selector import select_config_from_dir
from utilities.file_prompter import prompt_for_values, prompt_for_files
from datetime import datetime


ComputeRule.register("get_exchange_rate", get_exchange_rate)
ComputeRule.register("get_valid_date", get_valid_date)
ComputeRule.register("multiply", multiply)
ComputeRule.register("sum", sum)
ComputeRule.register("get_file_contents", get_file_contents)

CONFIG_PATH = select_config_from_dir(_PROJECT_ROOT)
config    = ConfigLoader().load(CONFIG_PATH)

all_refs = {
    **prompt_for_values(config.prompted_values),
    **prompt_for_files(config.prompted_files),
}

# Resolve input_file: may be a Path, a $ref string, or absent (default)
raw_input = config.input_file
if isinstance(raw_input, str) and raw_input.startswith("$"):
    input_file = Path(all_refs[raw_input[1:]])
else:
    input_file = raw_input or CONFIG_PATH.parent / "amazon_ledger.csv"

raw_data = read_csv(input_file)
registry  = RuleRegistry()
factory   = PipelineFactory(registry)
pipelines = factory.build_all(config, file_refs=all_refs)
 
router    = Router(pipelines=pipelines, config=config)
collector = OutputCollector()
processor = ETLProcessor(router=router, collector=collector)
 
outputs = processor.process(raw_data)
 
# ---------------------------------------------------------------------------
# Helper: extract mapped columns from config
# ---------------------------------------------------------------------------
 
def get_mapped_columns(config, destination: str) -> list[str]:
    """
    Reads the config for a given destination and returns all columns
    that are explicitly written by direct_mapping or conditional_mapping rules.
    Also includes required_fields since those are the columns we validated.
    """
    tx_config = config.transaction_types.get(destination)
    if tx_config is None:
        return []
 
    columns = []
    for rule in tx_config.rules:
        if rule.rule_type == "required_fields":
            columns.extend(rule.params.get("fields", []))
        elif rule.rule_type == "direct_mapping":
            columns.append(rule.params["target_column"])
        elif rule.rule_type == "conditional_mapping":
            for condition in rule.params.get("conditions", []):
                col = condition.get("target_column")
                if col and col not in columns:
                    columns.append(col)
        elif rule.rule_type == "set_value":
            col = rule.params.get("target_column")
            if col and col not in columns:
                columns.append(col)
        elif rule.rule_type == "lookup":
            col = rule.params.get("target_column")
            if col and col not in columns:
                columns.append(col)
        elif rule.rule_type == "compute":
            col = rule.params.get("target_column")
            if col and col not in columns:
                columns.append(col)        
 
    # preserve order, deduplicate
    seen = set()
    return [c for c in columns if not (c in seen or seen.add(c))]
 
 

TEMPLATE_PATH = _PROJECT_ROOT / "template.xlsx"

OUTPUT_PATH = input_file.parent / "output" / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
OUTPUT_PATH.parent.mkdir(exist_ok=True)


write_outputs_to_xlsx(outputs, config, TEMPLATE_PATH, OUTPUT_PATH)
