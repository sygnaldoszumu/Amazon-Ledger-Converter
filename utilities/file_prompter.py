from pathlib import Path

_last_dir: str | None = None


def _pick_file(title: str) -> str | None:
    """Open a GUI file picker. Returns the chosen path or None if cancelled."""
    global _last_dir
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        chosen = filedialog.askopenfilename(
            title=title,
            initialdir=_last_dir,
            filetypes=[
                ("CSV / Excel files", "*.csv *.xlsx *.xls"),
                ("All files", "*.*"),
            ],
        )
        root.destroy()
        if chosen:
            _last_dir = str(Path(chosen).parent)
            return str(Path(chosen).resolve())
        return None
    except Exception:
        return None


def _prompt_one(name: str, description: str) -> str:
    header = f"{description} : {name}" description else f"Please select {name} file"
    print(f"\n{header}")
    path = _pick_file(header)
    if path:
        print(f"  → {path}")
        return path

    print("  No file selected, please enter the path manually.")
    while True:
        raw = input("  Path: ").strip()
        p = Path(raw).expanduser().resolve()
        if p.exists():
            return str(p)
        print(f"    File not found: {p}. Please try again.")


def prompt_for_values(prompted_values) -> dict[str, str]:
    """
    Ask the user to type a value for each entry in prompted_values.
    Returns {name: value_str}.
    """
    if not prompted_values:
        return {}

    print("\nPlease enter the required values:")
    result: dict[str, str] = {}
    for entry in prompted_values:
        label = entry.description or entry.name
        while True:
            value = input(f"  {label}: ").strip()
            if value:
                result[entry.name] = value
                break
            print("    Value cannot be empty. Please try again.")
    return result


def prompt_for_files(prompted_files) -> dict[str, str]:
    """
    Ask the user to provide a path for each entry in prompted_files.
    Returns {name: absolute_path_str}.
    """
    if not prompted_files:
        return {}

    result: dict[str, str] = {}
    for entry in prompted_files:
        result[entry.name] = _prompt_one(entry.name, entry.description)
    return result
