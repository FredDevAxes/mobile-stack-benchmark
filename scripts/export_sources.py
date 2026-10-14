"""Export the exact source projections for inspection without modifying apps."""

import argparse
from source_mode import FILES, ROOT, projected

parser = argparse.ArgumentParser()
parser.add_argument("variant", choices=["S", "A"])
args = parser.parse_args()
for name in FILES + ["apps/swift/CatalogueApp.swift"]:
    if not (ROOT / name).exists():
        continue
    stack = (
        "react-native"
        if name.endswith(".tsx")
        else "flutter"
        if name.endswith(".dart")
        else "compose"
        if name.endswith(".kt")
        else "swift"
    )
    destination = ROOT / f".work/sources/{args.variant}/{name}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(projected((ROOT / name).read_text(), stack, args.variant))
    print(destination.relative_to(ROOT))
