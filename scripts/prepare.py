"""Select physically separate navigation implementations before building."""

from pathlib import Path
import argparse
import shutil
from assets import main as assets

ROOT = Path(__file__).resolve().parents[1]


def main(variant):
    assets()
    mode = {"S": "instant", "A": "animated"}[variant]
    for stack, extension, destination in [
        ("react-native", "ts", "src/transition.ts"),
        ("flutter", "dart", "lib/transition.dart"),
    ]:
        source = ROOT / f"apps/{stack}/variants/{mode}.{extension}"
        if source.exists():
            shutil.copy2(source, ROOT / f"apps/{stack}/{destination}")
    print(
        f"Prepared {variant}; animation-only modules are {'included' if variant == 'A' else 'excluded'}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("variant", choices=["S", "A"])
    main(parser.parse_args().variant)
