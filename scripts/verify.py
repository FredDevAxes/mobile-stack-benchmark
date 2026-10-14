"""Install an archived artifact and run a common local Maestro flow."""

from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import plistlib
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
IDS = {
    "compose": "dev.devaxes.catalogue",
    "react-native": "com.pilotrn",
    "flutter": "dev.devaxes.flutter_pilot",
}


def fingerprint(path):
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    digest = hashlib.sha256()
    for file in sorted(path.rglob("*")):
        if file.is_file():
            digest.update(str(file.relative_to(path)).encode())
            digest.update(hashlib.sha256(file.read_bytes()).digest())
    return digest.hexdigest()


def main(args):
    inspection = args.flow in ["progress", "reduced-motion"]
    base = ROOT / f".work/{'inspection' if inspection else 'artifacts'}/{args.stack}/{args.variant}"
    if args.platform == "android":
        artifact = base / "android.apk"
        subprocess.run(["adb", "-s", args.device, "install", "-r", str(artifact)], check=True)
        app_id = IDS[args.stack]
    else:
        artifact = base / "simulator.app"
        app_id = plistlib.loads((artifact / "Info.plist").read_bytes())["CFBundleIdentifier"]
        subprocess.run(["xcrun", "simctl", "install", args.device, str(artifact)], check=True)
    key = f"{args.stack}-{args.platform}-{args.variant}-{args.flow}"
    local = ROOT / f".work/verification/{key}"
    local.mkdir(parents=True, exist_ok=True)
    command = [
        str(ROOT / ".work/tools/maestro/bin/maestro"),
        "--device",
        args.device,
        "test",
        "--test-output-dir",
        str(local / "run"),
        "-e",
        f"APP_ID={app_id}",
        "-e",
        "OUTPUT=frames",
        "--format",
        "junit",
        "--output",
        str(local / "report.xml"),
        str(ROOT / f"verification/{args.flow}.yaml"),
    ]
    env = {
        **os.environ,
        "MAESTRO_CLI_NO_ANALYTICS": "1",
        "MAESTRO_CLI_ANALYSIS_NOTIFICATION_DISABLED": "true",
    }
    with (local / "run.log").open("w") as output:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT)
    evidence = ROOT / "results/verification"
    evidence.mkdir(parents=True, exist_ok=True)
    build_metadata = json.loads(
        (base / ("android.json" if args.platform == "android" else "simulator.json")).read_text()
    )
    if fingerprint(artifact) != build_metadata["artifactSHA256"]:
        raise ValueError("Artifact differs from build provenance")
    record = {
        "executedAtUTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "stack": args.stack,
        "platform": args.platform,
        "variant": args.variant,
        "flow": args.flow,
        "inspectionBuild": inspection,
        "exitCode": result.returncode,
        "sourceRevision": build_metadata["source"]["revision"],
        "sourceDirty": build_metadata["source"]["dirty"],
        "flowRevision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "artifactSHA256": fingerprint(artifact),
        "logSHA256": fingerprint(local / "run.log"),
        "appId": app_id,
        "maestro": "2.11.0",
    }
    if (local / "report.xml").exists():
        report = ET.parse(local / "report.xml")
        for suite in report.iter("testsuite"):
            suite.attrib.pop("device", None)
        for element in report.iter():
            if "file" in element.attrib:
                element.attrib["file"] = element.attrib["file"].replace(str(ROOT) + "/", "")
            if element.text:
                element.text = element.text.replace(str(ROOT) + "/", "")
        report.write(evidence / f"{key}.xml", encoding="utf-8", xml_declaration=True)
        record["report"] = f"results/verification/{key}.xml"
    if result.returncode == 0 and args.flow in ["demo", "progress"]:
        destination = ROOT / f"results/visuals/{args.platform}/{args.stack}"
        destination.mkdir(parents=True, exist_ok=True)
        for file in (local / "run").rglob("*"):
            if file.suffix in [".png", ".mp4", ".webm"] and (
                "takeScreenshot" in file.parts or "startRecording" in file.parts
            ):
                shutil.copy2(file, destination / file.name)
    (evidence / f"{key}.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"{key}: {'PASS' if result.returncode == 0 else 'FAIL'}")
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stack", choices=["flutter", "react-native", "compose", "swift"], required=True
    )
    parser.add_argument("--platform", choices=["android", "ios"], required=True)
    parser.add_argument("--variant", choices=["S", "A"], required=True)
    parser.add_argument("--device", required=True)
    parser.add_argument(
        "--flow",
        choices=["catalogue", "demo", "progress", "reduced-motion", "android-back", "scroll"],
        default="catalogue",
    )
    main(parser.parse_args())
