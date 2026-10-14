"""Run serial functional/visual checks on one dedicated virtual device."""

import argparse
import datetime
import json
import subprocess
import sys
from source_mode import ROOT


def main(platform, device):
    stacks = ["flutter", "react-native", "compose" if platform == "android" else "swift"]
    settings = []

    def motion(enabled):
        if platform == "android":
            for key in [
                "animator_duration_scale",
                "transition_animation_scale",
                "window_animation_scale",
            ]:
                subprocess.run(
                    [
                        "adb",
                        "-s",
                        device,
                        "shell",
                        "settings",
                        "put",
                        "global",
                        key,
                        "0" if enabled else "1",
                    ],
                    check=True,
                )
        else:
            subprocess.run(
                [
                    "xcrun",
                    "simctl",
                    "spawn",
                    device,
                    "defaults",
                    "write",
                    "com.apple.Accessibility",
                    "ReduceMotionEnabled",
                    "-bool",
                    "true" if enabled else "false",
                ],
                check=True,
            )
        settings.append(
            {
                "atUTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "reducedMotion": enabled,
            }
        )

    try:
        motion(False)
        for stack in stacks:
            for variant in ["S", "A"]:
                for flow in [
                    "catalogue",
                    "scroll",
                    *(["android-back"] if platform == "android" else []),
                ]:
                    print(f"CHECK {stack} {platform} {variant} {flow}", flush=True)
                    subprocess.run(
                        [
                            sys.executable,
                            "scripts/verify.py",
                            "--stack",
                            stack,
                            "--platform",
                            platform,
                            "--variant",
                            variant,
                            "--device",
                            device,
                            "--flow",
                            flow,
                        ],
                        check=True,
                    )
            for flow in ["demo", "progress"]:
                subprocess.run(
                    [
                        sys.executable,
                        "scripts/verify.py",
                        "--stack",
                        stack,
                        "--platform",
                        platform,
                        "--variant",
                        "A",
                        "--device",
                        device,
                        "--flow",
                        flow,
                    ],
                    check=True,
                )
        motion(True)
        for stack in stacks:
            subprocess.run(
                [
                    sys.executable,
                    "scripts/verify.py",
                    "--stack",
                    stack,
                    "--platform",
                    platform,
                    "--variant",
                    "A",
                    "--device",
                    device,
                    "--flow",
                    "reduced-motion",
                ],
                check=True,
            )
    finally:
        motion(False)
        destination = ROOT / f"results/verification/{platform}-settings.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(
                {
                    "scope": "Dedicated lab virtual device; reference text scale/default light portrait; settings restored to animated at completion",
                    "changes": settings,
                },
                indent=2,
            )
            + "\n"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=["android", "ios"], required=True)
    parser.add_argument("--device", required=True)
    args = parser.parse_args()
    main(args.platform, args.device)
