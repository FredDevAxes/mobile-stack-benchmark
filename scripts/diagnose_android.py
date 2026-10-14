"""Exploratory guest-process PSS; this is not a physical-phone performance test."""

from pathlib import Path
import argparse
import datetime
import json
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from verify import IDS, fingerprint

ROOT = Path(__file__).resolve().parents[1]


def main(device):
    output = ROOT / "results/diagnostics/android"
    output.mkdir(parents=True, exist_ok=True)
    adb = ["adb", "-s", device]

    def shell(*args):
        return subprocess.check_output([*adb, "shell", *args], text=True)

    def hierarchy():
        shell("uiautomator", "dump", "/sdcard/benchmark-window.xml")
        return ET.fromstring(shell("cat", "/sdcard/benchmark-window.xml"))

    def visible(tree, label):
        return any(
            label in node.attrib.get("text", "") or label in node.attrib.get("content-desc", "")
            for node in tree.iter("node")
        )

    records = []
    stacks = ["flutter", "react-native", "compose"]
    for series in range(3):
        order = stacks[series:] + stacks[:series]
        for stack in order:
            for variant in ["S", "A"] if series % 2 == 0 else ["A", "S"]:
                package = IDS[stack]
                artifact = ROOT / f".work/artifacts/{stack}/{variant}/android.apk"
                metadata = json.loads(artifact.with_name("android.json").read_text())
                if fingerprint(artifact) != metadata["artifactSHA256"]:
                    raise ValueError("Artifact identity mismatch")
                subprocess.run(
                    [*adb, "install", "-r", str(artifact)], check=True, stdout=subprocess.DEVNULL
                )
                for other in IDS.values():
                    shell("am", "force-stop", other)
                shell("pm", "clear", package)
                shell("am", "start", "-n", package + "/.MainActivity")
                time.sleep(3)
                tree = hierarchy()
                candidates = [
                    node
                    for node in tree.iter("node")
                    if node.attrib.get("content-desc", "") == "Open p001"
                ]
                if not candidates:
                    raise RuntimeError("First decoded image is not accessible")
                numbers = list(map(int, re.findall(r"\d+", candidates[0].attrib["bounds"])))
                x, y = (numbers[0] + numbers[2]) // 2, (numbers[1] + numbers[3]) // 2

                def cycle():
                    shell("input", "tap", str(x), str(y))
                    time.sleep(1.4 if variant == "A" else 1.0)
                    shell("input", "keyevent", "4")
                    time.sleep(1.4 if variant == "A" else 1.0)

                key = f"{stack}-{variant}-series-{series + 1}"
                # First transition is deliberately separate from warm-up.
                cycle()
                if not visible(hierarchy(), "Trail catalogue"):
                    raise RuntimeError("First return failed")
                (output / f"{key}-first-meminfo.txt").write_text(
                    shell("dumpsys", "meminfo", package)
                )
                (output / f"{key}-first-gfxinfo.txt").write_text(
                    shell("dumpsys", "gfxinfo", package, "framestats")
                )
                for _ in range(5):
                    cycle()
                key = f"{stack}-{variant}-series-{series + 1}"

                def memory(label):
                    text = shell("dumpsys", "meminfo", package)
                    (output / f"{key}-{label}-meminfo.txt").write_text(text)
                    match = re.search(r"TOTAL PSS:\s*(\d+)", text)
                    if not match:
                        raise RuntimeError("PSS unavailable; inspect retained raw output")
                    return int(match.group(1))

                before = memory("before")
                shell("dumpsys", "gfxinfo", package, "reset")
                for _ in range(30):
                    cycle()
                after = memory("after")
                graph = shell("dumpsys", "gfxinfo", package, "framestats")
                (output / f"{key}-gfxinfo.txt").write_text(graph)
                stable = visible(hierarchy(), "Trail catalogue")
                records.append(
                    {
                        "stack": stack,
                        "variant": variant,
                        "series": series + 1,
                        "order": order,
                        "firstTransitionCycles": 1,
                        "warmupCycles": 5,
                        "recordedCycles": 30,
                        "stableRestSeconds": 1,
                        "programmedAnimationSeconds": 0.4 if variant == "A" else 0,
                        "pilotWaitSeconds": 1.4 if variant == "A" else 1.0,
                        "pssBeforeKiB": before,
                        "pssAfterKiB": after,
                        "finalCatalogueVisible": stable,
                        "artifactSHA256": metadata["artifactSHA256"],
                        "sourceRevision": metadata["source"]["revision"],
                        "rawPrefix": "results/diagnostics/android/" + key,
                    }
                )
                (output / "samples.json").write_text(
                    json.dumps(
                        {
                            "executedAtUTC": datetime.datetime.now(
                                datetime.timezone.utc
                            ).isoformat(),
                            "metric": "Android guest-process TOTAL PSS in KiB; excludes host emulator and unaccounted host GPU allocations",
                            "environment": "One arm64 API 35 AVD; all apps Release; no video or debugger; only the target benchmark process active",
                            "frameTiming": "gfxinfo retained to inspect coverage; not interpreted as a common Flutter/native frame metric",
                            "records": records,
                        },
                        indent=2,
                    )
                    + "\n"
                )
                print(key + f": PSS {before} → {after} KiB; final catalogue {stable}", flush=True)
                if not stable:
                    raise RuntimeError("App state failed; retain this observation")
    for package in IDS.values():
        shell("am", "force-stop", package)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", required=True)
    main(parser.parse_args().device)
