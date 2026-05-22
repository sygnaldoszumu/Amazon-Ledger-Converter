# Add to COLLECT for Linux builds only
import platform

extra_datas = (
    [("amazon-ledger-converter.desktop", ".")]
    if platform.system() == "Linux"
    else []
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas + extra_datas,
    name="amazon-ledger-converter",
)
