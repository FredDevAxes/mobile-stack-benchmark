"""Build supported targets serially; inspection builds are always separate."""

import argparse
import subprocess
import sys

TARGETS = {
    "flutter": ["android", "simulator", "device"],
    "react-native": ["android", "simulator", "device"],
    "compose": ["android"],
    "swift": ["simulator", "device"],
}
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inspection", action="store_true")
    args = parser.parse_args()
    for stack, targets in TARGETS.items():
        for variant in ["A"] if args.inspection else ["S", "A"]:
            for platform in targets:
                if args.inspection and platform == "device":
                    continue
                print(
                    f"BUILD {stack} {platform} {variant} inspection={args.inspection}", flush=True
                )
                subprocess.run(
                    [
                        sys.executable,
                        "scripts/lab.py",
                        "build",
                        "--stack",
                        stack,
                        "--platform",
                        platform,
                        "--variant",
                        variant,
                        *(["--capture"] if args.inspection else []),
                    ],
                    check=True,
                )
