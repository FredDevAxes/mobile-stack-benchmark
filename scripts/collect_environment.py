"""Record non-identifying host/tool context; never export serials or environment secrets."""

import datetime
import json
import subprocess
from source_mode import ROOT


def read(*args):
    return subprocess.check_output(args, text=True).strip()


record = {
    "recordedAtUTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "host": {
        "model": read("sysctl", "-n", "hw.model"),
        "chip": "Apple M1 Pro",
        "ramBytes": int(read("sysctl", "-n", "hw.memsize")),
        "macOS": read("sw_vers", "-productVersion"),
        "macOSBuild": read("sw_vers", "-buildVersion"),
        "power": read("pmset", "-g", "batt"),
        "vmStat": read("vm_stat"),
    },
    "toolchain": json.loads((ROOT / "toolchain.json").read_text()),
    "android": {
        "kind": "AVD, not a physical Pixel",
        "name": "LabPilot_API35",
        "api": 35,
        "architecture": "arm64-v8a",
        "profile": "Pixel 6",
        "resolutionPx": [1080, 2400],
        "densityDpi": 420,
        "gpu": "host",
        "snapshots": False,
    },
    "ios": {
        "kind": "Simulator, not a physical iPhone",
        "profile": "iPhone 17 Pro",
        "runtime": "26.5",
        "resolutionPx": [1206, 2622],
        "logicalSize": [402, 874],
        "scale": 3,
    },
    "execution": {
        "android": "Release; no debugger/Metro",
        "swiftAndRNios": "optimized Release simulator; no debugger/Metro",
        "flutterIos": "Debug simulator; no debugger attached",
        "deviceIos": "unsigned Release arm64, compiled only",
    },
    "limits": [
        "Shared development host; background activity not fully controlled",
        "Runner OS images and SDK distributions can drift; record actual versions",
        "All diagnostics refer to virtual environments",
    ],
}
(ROOT / "results/environment.json").write_text(json.dumps(record, indent=2) + "\n")
print("results/environment.json")
