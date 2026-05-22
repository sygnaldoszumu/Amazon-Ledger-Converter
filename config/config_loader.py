import yaml
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Typed config value objects
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class RuleConfig:
    rule_type: str
    params: dict

    def __repr__(self):
        return f"RuleConfig(rule_type={self.rule_type!r}, params={self.params})"


@dataclass(frozen=True)
class TransactionTypeConfig:
    output_destination: str
    rules: tuple[RuleConfig, ...]


@dataclass(frozen=True)
class PipelineConfig:
    global_rules: tuple[RuleConfig, ...]
    transaction_types: dict[str, TransactionTypeConfig]
    config_dir: Path = field(default_factory=Path)   # ← new: absolute dir of the config file


# ---------------------------------------------------------------------------
# Validation helpers  (unchanged)
# ---------------------------------------------------------------------------
REQUIRED_TOP_LEVEL_KEYS = {"transaction_types"}
REQUIRED_TRANSACTION_TYPE_KEYS = {"output_destination", "rules"}
VALID_RULE_TYPES = {
    "routing", "conditional_routing", "required_fields", "type_validation",
    "format_validation", "direct_mapping", "conditional_mapping",
    "ignore_if", "set_value", "lookup", "compute",
}


def _validate_rule(rule: dict, context: str) -> None:
    if not isinstance(rule, dict):
        raise ConfigValidationError(f"{context}: each rule must be a dict, got {type(rule).__name__}.")
    if "type" not in rule:
        raise ConfigValidationError(f"{context}: rule is missing required key 'type'. Rule: {rule}.")
    if rule["type"] not in VALID_RULE_TYPES:
        raise ConfigValidationError(
            f"{context}: unknown rule type '{rule['type']}'. "
            f"Valid types: {sorted(VALID_RULE_TYPES)}."
        )


def _validate_transaction_type(name: str, block: dict) -> None:
    if not isinstance(block, dict):
        raise ConfigValidationError(f"Transaction type '{name}' must be a dict, got {type(block).__name__}.")
    missing = REQUIRED_TRANSACTION_TYPE_KEYS - block.keys()
    if missing:
        raise ConfigValidationError(f"Transaction type '{name}' is missing required keys: {sorted(missing)}.")
    if not isinstance(block["output_destination"], str) or not block["output_destination"].strip():
        raise ConfigValidationError(f"Transaction type '{name}': 'output_destination' must be a non-empty string.")
    if not isinstance(block["rules"], list):
        raise ConfigValidationError(f"Transaction type '{name}': 'rules' must be a list.")
    for i, rule in enumerate(block["rules"]):
        _validate_rule(rule, context=f"Transaction type '{name}', rule[{i}]")


def _validate_raw_config(raw: dict) -> None:
    if not isinstance(raw, dict):
        raise ConfigValidationError(f"Config root must be a YAML mapping, got {type(raw).__name__}.")
    missing = REQUIRED_TOP_LEVEL_KEYS - raw.keys()
    if missing:
        raise ConfigValidationError(f"Config is missing required top-level keys: {sorted(missing)}.")
    if not isinstance(raw["transaction_types"], dict) or not raw["transaction_types"]:
        raise ConfigValidationError("'transaction_types' must be a non-empty mapping.")
    for name, block in raw["transaction_types"].items():
        _validate_transaction_type(name, block)
    global_rules = raw.get("global_rules", [])
    if not isinstance(global_rules, list):
        raise ConfigValidationError("'global_rules' must be a list.")
    for i, rule in enumerate(global_rules):
        _validate_rule(rule, context=f"global_rules[{i}]")


# ---------------------------------------------------------------------------
# Path resolution helper
# ---------------------------------------------------------------------------

def _resolve_path(value: str, config_dir: Path) -> str:
    """
    If *value* is a relative path string, resolve it against *config_dir*
    and return the absolute path as a string.  Absolute paths are returned
    unchanged.
    """
    p = Path(value)
    if p.is_absolute():
        return value
    return str((config_dir / p).resolve())


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _parse_rule(rule: dict, config_dir: Path) -> RuleConfig:
    rule_type = rule["type"]
    params = {k: v for k, v in rule.items() if k != "type"}

    # --- resolve lookup_file relative to the config directory ---------------
    if rule_type == "lookup" and "lookup_file" in params:
        params["lookup_file"] = _resolve_path(params["lookup_file"], config_dir)

    # --- resolve file-path raw inputs in compute rules ----------------------
    # A `raw` entry whose value points to an existing file (or looks like a
    # relative path to one) is resolved so the function receives an absolute path.
    if rule_type == "compute" and "inputs" in params:
        resolved_inputs = []
        for entry in params["inputs"]:
            if "raw" in entry and isinstance(entry["raw"], str):
                candidate = config_dir / entry["raw"]
                if candidate.exists():
                    entry = {**entry, "raw": str(candidate.resolve())}
            resolved_inputs.append(entry)
        params["inputs"] = resolved_inputs

    return RuleConfig(rule_type=rule_type, params=params)


def _parse_transaction_type(name: str, block: dict, config_dir: Path) -> TransactionTypeConfig:
    return TransactionTypeConfig(
        output_destination=block["output_destination"],
        rules=tuple(_parse_rule(r, config_dir) for r in block["rules"]),
    )


def _parse_config(raw: dict, config_dir: Path) -> PipelineConfig:
    return PipelineConfig(
        global_rules=tuple(_parse_rule(r, config_dir) for r in raw.get("global_rules", [])),
        transaction_types={
            name: _parse_transaction_type(name, block, config_dir)
            for name, block in raw["transaction_types"].items()
        },
        config_dir=config_dir,
    )


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

class ConfigValidationError(Exception):
    pass


class ConfigLoader:
    """
    Loads and validates the pipeline YAML config from a file path.
    All relative file paths inside the config (lookup_file, raw file inputs)
    are resolved relative to the config file's directory.
    Returns a fully typed, immutable PipelineConfig.
    """

    def load(self, path: str | Path) -> PipelineConfig:
        path = Path(path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        if not path.is_file():
            raise ValueError(f"Config path is not a file: {path}")

        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            raise ConfigValidationError(f"Config file contains invalid YAML: {e}") from e

        _validate_raw_config(raw)
        return _parse_config(raw, config_dir=path.parent)   # ← pass the directory
