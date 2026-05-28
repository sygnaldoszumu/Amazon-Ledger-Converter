"""
utilities/config_selector.py
Discovers client config files and prompts the user to pick one.

Usage (interactive, no args):
    python main.py
    → prompts for clients directory, then shows config menu

Usage (clients dir provided):
    python main.py --clients-dir /path/to/clients

Usage (non-interactive / CI):
    python main.py --config /path/to/client/config.yml
"""
import argparse
import sys
from pathlib import Path

_CONFIG_FILENAME = "config.yml"


def _discover_configs(clients_dir: Path) -> list[Path]:
    if not clients_dir.exists():
        return []
    return sorted(clients_dir.rglob(_CONFIG_FILENAME))


# def _prompt_clients_dir() -> Path:
#     while True:
#         raw = input("Enter path to clients directory: ").strip()
#         path = Path(raw).expanduser().resolve()
#         if path.is_dir():
#             return path
#         print(f"  Directory not found: {path}. Please try again.")
def _prompt_clients_dir() -> Path:
    # Try GUI folder picker first
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()          # hide the empty root window
        root.attributes("-topmost", True)
        chosen = filedialog.askdirectory(title="Select clients directory")
        root.destroy()

        if chosen:
            return Path(chosen).resolve()
        # User cancelled the dialog — fall through to manual input
        print("No directory selected, please enter the path manually.")

    except Exception:
        # tkinter not available (e.g. headless server)
        pass

    # Manual fallback
    while True:
        raw = input("Enter path to clients directory: ").strip()
        path = Path(raw).expanduser().resolve()
        if path.is_dir():
            return path
        print(f"  Directory not found: {path}. Please try again.")

def _prompt_user(configs: list[Path]) -> Path:
    print("\nAvailable client configs:")
    print("-" * 40)
    for i, path in enumerate(configs, start=0):
        try:
            label = path.relative_to(Path.cwd())
        except ValueError:
            label = path
        print(f"  [{i}] {label}")
    print("-" * 40)
    while True:
        raw = input(f"Select config [0-{len(configs) - 1}]: ").strip()
        if raw.isdigit():
            choice = int(raw)
            if 0 <= choice < len(configs):
                return configs[choice]
        print(f"  Please enter a number between 0 and {len(configs) - 1}.")


def select_config_from_dir(*directories: Path) -> Path:
    """
    Find all .yml / .yaml files in the given directories.
    Files with the same name are deduplicated (first directory wins).
    Return the single match immediately, or prompt with a numbered menu if there are several.
    Exits with an error if no config files are found.
    """
    seen_names: set[str] = set()
    configs: list[Path] = []
    for directory in directories:
        if not directory.exists():
            continue
        for p in sorted(directory.iterdir()):
            if p.is_file() and p.suffix.lower() in (".yml", ".yaml") and p.name not in seen_names:
                seen_names.add(p.name)
                configs.append(p)
    configs.sort(key=lambda p: p.name)
    if not configs:
        print("ERROR: no .yml/.yaml config files found.", file=sys.stderr)
        sys.exit(1)
    if len(configs) == 1:
        print(f"Using config: {configs[0].name}")
        return configs[0]
    return _prompt_user(configs)


def select_config() -> Path:
    """
    Resolve and return a config Path.

    Resolution order:
      1. --config <path>       direct path, skips everything else
      2. --clients-dir <path>  search this directory for config.yml files
      3. interactive           prompt for clients directory, then show menu
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--clients-dir", type=Path, default=None)
    args, _ = parser.parse_known_args()

    # 1. Direct config path
    if args.config is not None:
        if not args.config.exists():
            print(f"ERROR: config file not found: {args.config}", file=sys.stderr)
            sys.exit(1)
        print(f"Using config: {args.config}")
        return args.config

    # 2. Clients dir from CLI or interactive prompt
    clients_dir = args.clients_dir or _prompt_clients_dir()

    configs = _discover_configs(clients_dir)
    if not configs:
        print(
            f"ERROR: no {_CONFIG_FILENAME!r} files found under {clients_dir}.",
            file=sys.stderr,
        )
        sys.exit(1)

    if len(configs) == 1:
        print(f"Using config: {configs[0]}")
        return configs[0]

    return _prompt_user(configs)
