# amazon_ledger_converter.spec
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
    ],
    hiddenimports=[
        "openpyxl",    # often missed by PyInstaller's static analysis
        "pandas",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,      # onedir: faster startup, easier to debug
    name="amazon-ledger-converter",
    console=True,               # keep console — the prompt needs it
    strip=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="amazon-ledger-converter",
)
