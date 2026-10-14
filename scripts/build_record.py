"""Record source state before projection and artifact identity after compilation."""

from pathlib import Path
import datetime
import hashlib
import json
import platform
import subprocess
from verify import fingerprint

ROOT = Path(__file__).resolve().parents[1]


def source_state():
    paths = (
        subprocess.check_output(
            [
                "git",
                "ls-files",
                "-z",
                "apps",
                "shared",
                "scripts/assets.py",
                "scripts/prepare.py",
                "scripts/source_mode.py",
                "scripts/lab.py",
                "scripts/build_swift.py",
                "toolchain.json",
            ],
            cwd=ROOT,
        )
        .decode()
        .split("\0")
    )
    manifest = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in paths if name
    }
    return {
        "revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "dirty": bool(
            subprocess.check_output(
                [
                    "git",
                    "status",
                    "--porcelain",
                    "--",
                    "apps",
                    "shared",
                    "scripts",
                    "toolchain.json",
                ],
                cwd=ROOT,
            )
        ),
        "files": manifest,
    }


def save(args, state):
    base = (
        ROOT / f".work/{'inspection' if args.capture else 'artifacts'}/{args.stack}/{args.variant}"
    )
    artifact = base / ("android.apk" if args.platform == "android" else args.platform + ".app")
    record = {
        "builtAtUTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "stack": args.stack,
        "variant": args.variant,
        "platform": args.platform,
        "inspectionBuild": args.capture,
        "source": state,
        "orchestratorPython": platform.python_version(),
        "nodeUsed": subprocess.check_output(["node", "--version"], text=True).strip()
        if args.stack == "react-native"
        else None,
        "artifactSHA256": fingerprint(artifact),
        "reproductionCommand": [
            "python3",
            "scripts/lab.py",
            "build",
            "--stack",
            args.stack,
            "--platform",
            args.platform,
            "--variant",
            args.variant,
            *(["--capture"] if args.capture else []),
        ],
    }
    (base / (args.platform + ".json")).write_text(json.dumps(record, indent=2) + "\n")
