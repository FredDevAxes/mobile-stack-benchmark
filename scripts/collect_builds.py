"""Collect the twelve comparable arm64 Release artifacts, never simulator sizes."""

from pathlib import Path
import datetime
import json
import plistlib
import subprocess
import zipfile
from verify import fingerprint

ROOT = Path(__file__).resolve().parents[1]


def main():
    records = []
    for stack in ["flutter", "react-native", "compose", "swift"]:
        for variant in ["S", "A"]:
            platform = "android" if stack == "compose" else "device" if stack == "swift" else None
            for target in [platform] if platform else ["android", "device"]:
                base = ROOT / f".work/artifacts/{stack}/{variant}"
                artifact = base / ("android.apk" if target == "android" else "device.app")
                metadata = json.loads((base / (target + ".json")).read_text())
                if metadata["artifactSHA256"] != fingerprint(artifact):
                    raise ValueError("Artifact no longer matches build record")
                record = {
                    "stack": stack,
                    "variant": variant,
                    "platform": "android" if target == "android" else "ios",
                    "artifactKind": "arm64 Release APK"
                    if target == "android"
                    else "unsigned arm64 Release app bundle",
                    "build": metadata,
                }
                if target == "android":
                    with zipfile.ZipFile(artifact) as archive:
                        architectures = sorted(
                            {
                                name.split("/")[1]
                                for name in archive.namelist()
                                if name.startswith("lib/") and name.endswith(".so")
                            }
                        )
                        if architectures != ["arm64-v8a"]:
                            raise ValueError(str(architectures))
                        record.update(
                            bytes=artifact.stat().st_size,
                            architectures=architectures,
                            resourcesUncompressedBytes=sum(
                                info.file_size
                                for info in archive.infolist()
                                if info.filename.startswith("assets/")
                            ),
                            nativeLibrariesUncompressedBytes=sum(
                                info.file_size
                                for info in archive.infolist()
                                if info.filename.endswith(".so")
                            ),
                        )
                else:
                    regular = [
                        path
                        for path in artifact.rglob("*")
                        if path.is_file() and not path.is_symlink()
                    ]
                    binary = (
                        artifact
                        / plistlib.loads((artifact / "Info.plist").read_bytes())[
                            "CFBundleExecutable"
                        ]
                    )
                    architecture = subprocess.check_output(
                        ["lipo", "-archs", str(binary)], text=True
                    ).strip()
                    if architecture != "arm64":
                        raise ValueError(architecture)
                    record.update(
                        bytes=sum(path.stat().st_size for path in regular),
                        architectures=[architecture],
                        logicalRegularFiles=len(regular),
                        symbolicLinkBytes=sum(
                            path.lstat().st_size
                            for path in artifact.rglob("*")
                            if path.is_symlink()
                        ),
                        frameworksBytes=sum(
                            path.stat().st_size
                            for path in regular
                            if "Frameworks" in path.relative_to(artifact).parts
                        ),
                    )
                records.append(record)
    target = ROOT / "results/builds.json"
    target.write_text(
        json.dumps(
            {
                "collectedAtUTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "definitions": {
                    "android": "Complete APK file bytes; arm64-v8a only; local development signing",
                    "ios": "Sum of logical regular-file bytes, excluding duplicate symlink targets; unsigned device arm64; external symbols excluded",
                },
                "records": records,
            },
            indent=2,
        )
        + "\n"
    )
    print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
