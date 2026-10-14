"""Build the minimal SwiftUI app with Apple's compiler and explicit variants."""

from pathlib import Path
import argparse
import os
import plistlib
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main(variant, device, capture=False):
    mode = {"S": "instant", "A": "animated"}[variant]
    sdk = "iphoneos" if device else "iphonesimulator"
    app = ROOT / f".work/swift/{variant}/{sdk}/Catalogue.app"
    app.mkdir(parents=True, exist_ok=True)
    sdkpath = subprocess.check_output(["xcrun", "--sdk", sdk, "--show-sdk-path"], text=True).strip()
    sources = [
        ROOT / "apps/swift/Sources/CatalogCore/Product.swift",
        ROOT / "apps/swift/CatalogueApp.swift",
        ROOT / f"apps/swift/variants/{mode}.swift",
    ]
    if capture:
        sources.append(ROOT / "apps/swift/Capture.swift")
    target = "arm64-apple-ios18.0" + ("" if device else "-simulator")
    cmd = [
        "xcrun",
        "swiftc",
        *map(str, sources),
        "-parse-as-library",
        "-sdk",
        sdkpath,
        "-target",
        target,
        "-O",
        "-o",
        str(app / "Catalogue"),
    ]
    if capture:
        cmd += ["-D", "CAPTURE"]
    subprocess.run(cmd, check=True, env={**os.environ, "SDKROOT": sdkpath})
    subprocess.run(["strip", "-S", str(app / "Catalogue")], check=True)
    shutil.copy2(ROOT / "shared/products.json", app / "products.json")
    shutil.copytree(ROOT / "shared/images", app / "images", dirs_exist_ok=True)
    plist = {
        "CFBundleIdentifier": "dev.devaxes.catalogue.swift",
        "CFBundleName": "Trail catalogue",
        "CFBundleExecutable": "Catalogue",
        "CFBundlePackageType": "APPL",
        "CFBundleVersion": "1",
        "CFBundleShortVersionString": "0.1",
        "MinimumOSVersion": "18.0",
        "LSRequiresIPhoneOS": True,
        "UILaunchScreen": {},
        "UIDeviceFamily": [1],
        "UISupportedInterfaceOrientations": ["UIInterfaceOrientationPortrait"],
    }
    (app / "Info.plist").write_bytes(plistlib.dumps(plist))
    if not device:
        subprocess.run(["codesign", "--force", "--sign", "-", str(app)], check=True)
    print(app.relative_to(ROOT))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("variant", choices=["S", "A"])
    parser.add_argument("--device", action="store_true")
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    main(args.variant, args.device, args.capture)
