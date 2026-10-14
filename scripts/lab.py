"""Root commands; platform tools remain responsible for actual checks."""

from pathlib import Path
import argparse
import hashlib
import shutil
import subprocess
from source_mode import sources
from build_record import source_state, save
from prepare import main as prepare

ROOT = Path(__file__).resolve().parents[1]


def run(cmd, directory=ROOT):
    subprocess.run(cmd, cwd=directory, check=True)


def lint(stack):
    if stack == "flutter":
        run(
            ["dart", "format", "--output=none", "--set-exit-if-changed", "lib", "test", "variants"],
            ROOT / "apps/flutter",
        )
        run(["flutter", "analyze"], ROOT / "apps/flutter")
    elif stack == "react-native":
        for cmd in [
            ["npm", "run", "lint", "--", "--max-warnings=0"],
            ["npm", "run", "typecheck"],
            ["npm", "run", "format"],
        ]:
            run(cmd, ROOT / "apps/react-native")
    elif stack == "compose":
        jar = ROOT / ".work/ktlint.jar"
        assert (
            hashlib.sha256(jar.read_bytes()).hexdigest()
            == "5f3de4ee4014137b05c72ed68eb46fe686aeb11fbdef27faf77f55d51c1b2536"
        )
        run(
            [
                "java",
                "-jar",
                str(jar),
                "apps/compose/**/*.kt",
                "apps/compose/**/*.kts",
                "!**/build/**",
            ]
        )
        run(
            [
                "./gradlew",
                "--no-daemon",
                "--max-workers=2",
                ":app:lintInstantRelease",
                ":app:lintAnimatedRelease",
            ],
            ROOT / "apps/compose",
        )
    elif stack == "swift":
        run(["xcrun", "swift-format", "lint", "--strict", "-r", "apps/swift"])


def test(stack):
    if stack == "flutter":
        run(["flutter", "test"], ROOT / "apps/flutter")
    elif stack == "react-native":
        run(["npm", "test", "--", "--runInBand"], ROOT / "apps/react-native")
    elif stack == "compose":
        run(
            [
                "./gradlew",
                "--no-daemon",
                "--max-workers=2",
                ":app:testInstantDebugUnitTest",
                ":app:testAnimatedDebugUnitTest",
            ],
            ROOT / "apps/compose",
        )
    elif stack == "swift":
        run(["swift", "test", "--package-path", "apps/swift"])


def build(stack, platform, variant, capture=False):
    destination = ROOT / f".work/{'inspection' if capture else 'artifacts'}/{stack}/{variant}"
    destination.mkdir(parents=True, exist_ok=True)
    if stack == "compose":
        assert platform == "android"
        flavor = "Instant" if variant == "S" else "Animated"
        run(
            ["./gradlew", "--no-daemon", "--max-workers=2", f":app:assemble{flavor}Release"],
            ROOT / "apps/compose",
        )
        source = (
            ROOT
            / f"apps/compose/app/build/outputs/apk/{flavor.lower()}/release/app-{flavor.lower()}-release.apk"
        )
        shutil.copy2(source, destination / "android.apk")
    elif stack == "swift":
        run(
            [
                "python3",
                "scripts/build_swift.py",
                variant,
                *(["--capture"] if capture else []),
                *(["--device"] if platform == "device" else []),
            ]
        )
        source = (
            ROOT
            / f".work/swift/{variant}/{'iphoneos' if platform == 'device' else 'iphonesimulator'}/Catalogue.app"
        )
        shutil.copytree(source, destination / f"{platform}.app", dirs_exist_ok=True)
    elif stack == "flutter":
        if platform == "android":
            run(
                ["flutter", "build", "apk", "--release", "--target-platform", "android-arm64"],
                ROOT / "apps/flutter",
            )
            shutil.copy2(
                ROOT / "apps/flutter/build/app/outputs/flutter-apk/app-release.apk",
                destination / "android.apk",
            )
        else:
            run(
                [
                    "flutter",
                    "build",
                    "ios",
                    "--no-codesign",
                    *(["--simulator", "--debug"] if platform == "simulator" else ["--release"]),
                ],
                ROOT / "apps/flutter",
            )
            shutil.copytree(
                ROOT
                / f"apps/flutter/build/ios/{'iphonesimulator' if platform == 'simulator' else 'iphoneos'}/Runner.app",
                destination / f"{platform}.app",
                dirs_exist_ok=True,
            )
    elif stack == "react-native":
        if platform == "android":
            run(
                [
                    "./gradlew",
                    "--no-daemon",
                    "--max-workers=2",
                    ":app:assembleRelease",
                    "-PreactNativeArchitectures=arm64-v8a",
                ],
                ROOT / "apps/react-native/android",
            )
            shutil.copy2(
                ROOT / "apps/react-native/android/app/build/outputs/apk/release/app-release.apk",
                destination / "android.apk",
            )
        else:
            sdk = "iphonesimulator" if platform == "simulator" else "iphoneos"
            run(
                [
                    "xcodebuild",
                    "-workspace",
                    "PilotRN.xcworkspace",
                    "-scheme",
                    "PilotRN",
                    "-configuration",
                    "Release",
                    "-sdk",
                    sdk,
                    "-destination",
                    "generic/platform=" + ("iOS Simulator" if platform == "simulator" else "iOS"),
                    "-derivedDataPath",
                    str(ROOT / f".work/rn/{sdk}"),
                    "-jobs",
                    "1",
                    "ARCHS=arm64",
                    "ONLY_ACTIVE_ARCH=YES",
                    "CODE_SIGNING_ALLOWED=NO",
                    "build",
                ],
                ROOT / "apps/react-native/ios",
            )
            shutil.copytree(
                ROOT / f".work/rn/{sdk}/Build/Products/Release-{sdk}/PilotRN.app",
                destination / f"{platform}.app",
                dirs_exist_ok=True,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["lint", "test", "build"])
    parser.add_argument(
        "--stack", choices=["all", "flutter", "react-native", "compose", "swift"], default="all"
    )
    parser.add_argument("--variant", choices=["S", "A"], default="A")
    parser.add_argument("--platform", choices=["android", "simulator", "device"], default="android")
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    if args.command == "build" and args.stack == "all":
        parser.error("Build one stack and target at a time")
    if args.command == "build" and (
        (args.stack == "swift" and args.platform == "android")
        or (args.stack == "compose" and args.platform != "android")
    ):
        parser.error("Unsupported stack/platform pair")
    for stack in (
        ["flutter", "react-native", "compose", "swift"] if args.stack == "all" else [args.stack]
    ):
        if args.command == "build":
            state = source_state()
            with sources(args.capture, args.variant):
                prepare(args.variant)
                build(stack, args.platform, args.variant, args.capture)
            save(args, state)
        else:
            with sources(args.variant == "A", args.variant):
                prepare(args.variant)
                if args.command == "lint":
                    lint(stack)
                else:
                    test(stack)
