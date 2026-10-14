"""Count formatted production projections with a declared file list and cloc 2.10."""

from pathlib import Path
import hashlib
import json
import subprocess
import re
from source_mode import ROOT, projected

FILES = {
    "flutter": {
        "ui": ["lib/main.dart"],
        "logic": ["lib/catalogue.dart"],
        "platform": [
            "android/app/src/main/kotlin/dev/devaxes/flutter_pilot/MainActivity.kt",
            "ios/Runner/AppDelegate.swift",
        ],
        "tests": ["test/catalogue_test.dart"],
    },
    "react-native": {
        "ui": ["App.tsx"],
        "logic": ["src/catalogue.ts"],
        "platform": [
            "android/app/src/main/java/com/pilotrn/MainActivity.kt",
            "android/app/src/main/java/com/pilotrn/MainApplication.kt",
            "ios/PilotRN/AppDelegate.swift",
        ],
        "tests": ["__tests__/catalogue.test.ts"],
    },
    "compose": {
        "ui": ["app/src/main/java/dev/devaxes/catalogue/MainActivity.kt"],
        "logic": ["app/src/main/java/dev/devaxes/catalogue/Product.kt"],
        "platform": [],
        "tests": ["app/src/test/java/dev/devaxes/catalogue/CatalogueTest.kt"],
    },
    "swift": {
        "ui": ["CatalogueApp.swift"],
        "logic": ["Sources/CatalogCore/Product.swift"],
        "platform": [],
        "tests": ["Tests/CatalogCoreTests/ProductTests.swift"],
    },
}


def main():
    version = subprocess.check_output(["cloc", "--version"], text=True).strip()
    if version != "2.10":
        raise ValueError("Expected cloc 2.10")
    output = []
    ancillary = []
    for variant in ["S", "A"]:
        mode = "instant" if variant == "S" else "animated"
        for stack, groups in FILES.items():
            extension = {
                "flutter": "dart",
                "react-native": "ts",
                "swift": "swift",
                "compose": "kt",
            }[stack]
            navigation = (
                f"app/src/{mode}/java/dev/devaxes/catalogue/Transition.kt"
                if stack == "compose"
                else f"variants/{mode}.{extension}"
            )
            definitions = {**groups, "navigation": [navigation]}
            exported = ROOT / f".work/loc/{variant}/{stack}"
            exported.mkdir(parents=True, exist_ok=True)
            paths = {}
            (exported / ".editorconfig").write_text(
                "root = true\n[*.kt]\nktlint_standard_package-name = disabled\nktlint_standard_no-wildcard-imports = disabled\nktlint_function_naming_ignore_when_annotated_with = Composable\n"
            )
            for group, relatives in definitions.items():
                for relative in relatives:
                    source = ROOT / "apps" / stack / relative
                    destination = exported / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    text = source.read_text()
                    if group == "ui":
                        text = projected(text, stack, variant)
                    destination.write_text(text)
                    paths[destination] = (group, str(source.relative_to(ROOT)))
            if stack == "flutter":
                subprocess.run(
                    ["dart", "format", str(exported)], check=True, stdout=subprocess.DEVNULL
                )
            elif stack == "react-native":
                subprocess.run(
                    [
                        str(ROOT / "apps/react-native/node_modules/.bin/prettier"),
                        "--config",
                        str(ROOT / "apps/react-native/.prettierrc.js"),
                        "--write",
                        *[str(path) for path in paths if path.suffix in {".ts", ".tsx", ".js"}],
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                )
            elif stack == "compose":
                subprocess.run(
                    [
                        "java",
                        "-jar",
                        str(ROOT / ".work/ktlint.jar"),
                        "--format",
                        str(exported / "**/*.kt"),
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                )
            else:
                subprocess.run(
                    [
                        "xcrun",
                        "swift-format",
                        "format",
                        "-i",
                        "--configuration",
                        str(ROOT / "apps/swift/.swift-format"),
                        *map(str, paths),
                    ],
                    check=True,
                )
            native_swift = [str(path) for path in paths if path.suffix == ".swift"]
            native_kotlin = [str(path) for path in paths if path.suffix == ".kt"]
            if native_swift and stack != "swift":
                subprocess.run(
                    [
                        "xcrun",
                        "swift-format",
                        "format",
                        "-i",
                        "--configuration",
                        str(ROOT / "apps/swift/.swift-format"),
                        *native_swift,
                    ],
                    check=True,
                )
            if native_kotlin and stack not in {"compose"}:
                subprocess.run(
                    ["java", "-jar", str(ROOT / ".work/ktlint.jar"), "--format", *native_kotlin],
                    check=True,
                    stdout=subprocess.DEVNULL,
                )
            data = json.loads(
                subprocess.check_output(
                    ["cloc", "--json", "--by-file", "--skip-uniqueness", *map(str, paths)],
                    text=True,
                )
            )
            totals = {key: 0 for key in definitions}
            files = []
            for path, (category, original) in paths.items():
                measured = data.get(
                    str(path),
                    {"code": 0, "comment": 0, "blank": 0, "language": "not recognized by cloc"},
                )
                totals[category] += measured["code"]
                files.append(
                    {
                        "path": original,
                        "category": category,
                        "language": measured["language"],
                        "code": measured["code"],
                        "comment": measured["comment"],
                        "blank": measured["blank"],
                        "formattedProjectionSHA256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    }
                )
            ui_path = next(path for path, (category, _) in paths.items() if category == "ui")
            ui = ui_path.read_text()
            ranges = {
                "flutter": [("  Future<void> load()", "  Future<void> open(")],
                "react-native": [
                    ("  const write =", "  const complete ="),
                    ("  const toggle =", "  const open ="),
                ],
                "swift": [("    init()", "    private func open(")],
                "compose": [
                    ("        val products =", "        setContent {"),
                    ("            var favorites by", "            var draft by"),
                    ("            val toggle:", "            val data ="),
                ],
            }[stack]
            fragments = []
            for start, end in ranges:
                left = ui.index(start)
                right = ui.index(end, left)
                fragments.append(ui[left:right])
            extracted = exported / ("persistence-fragments" + ui_path.suffix)
            extracted.write_text("\n".join(fragments))
            fragment_count = json.loads(
                subprocess.check_output(["cloc", "--json", str(extracted)], text=True)
            )["SUM"]["code"]
            totals["ui"] -= fragment_count
            totals["logic"] += fragment_count
            next(file for file in files if file["category"] == "ui")["split"] = {
                "uiAndNavigation": totals["ui"],
                "loadingPersistenceAndLifecycle": fragment_count,
                "ranges": ranges,
            }
            output.append(
                {
                    "stack": stack,
                    "variant": variant,
                    "categories": totals,
                    "applicationTotal": sum(
                        value for key, value in totals.items() if key != "tests"
                    ),
                    "files": files,
                }
            )
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    for stack, groups in FILES.items():
        root = ROOT / "apps" / stack
        main_file = root / groups["ui"][0]
        source = main_file.read_text()
        blocks = re.findall(
            r"(?:\{/\* CAPTURE_BEGIN \*/\}|// CAPTURE_BEGIN)\n(.*?)(?:\{/\* CAPTURE_END \*/\}|// CAPTURE_END)",
            source,
            re.S,
        )
        if stack == "swift":
            blocks = re.findall(r"#if CAPTURE\n(.*?)#endif", source, re.S)
        suffix = main_file.suffix
        capture = ROOT / f".work/loc/instrumentation/{stack}{suffix}"
        capture.parent.mkdir(parents=True, exist_ok=True)
        capture.write_text("\n".join(blocks))
        instrumentation = [str(capture)]
        if stack == "swift":
            instrumentation.append(str(root / "Capture.swift"))
        configuration = [
            str(ROOT / name)
            for name in tracked
            if name.startswith(f"apps/{stack}/")
            and (
                Path(name).suffix in {".gradle", ".kts", ".xml", ".plist", ".xcconfig", ".pbxproj"}
                or Path(name).name
                in {
                    "pubspec.yaml",
                    "analysis_options.yaml",
                    "Package.swift",
                    "Podfile",
                    "Gemfile",
                    "package.json",
                    "tsconfig.json",
                    ".eslintrc.js",
                    ".prettierrc.js",
                    "metro.config.js",
                    "babel.config.js",
                    "jest.config.js",
                    "app.json",
                    "index.js",
                }
            )
        ]
        for category, paths in [
            ("instrumentation", instrumentation),
            ("configuration", configuration),
        ]:
            data = json.loads(
                subprocess.check_output(
                    ["cloc", "--json", "--by-file", "--skip-uniqueness", *paths], text=True
                )
            )
            ancillary.append(
                {
                    "stack": stack,
                    "category": category,
                    "code": data.get("SUM", {}).get("code", 0),
                    "files": [
                        {
                            "path": str(Path(path).relative_to(ROOT)),
                            **data.get(path, {"code": 0, "language": "unrecognized"}),
                        }
                        for path in paths
                    ],
                }
            )
    tooling = [
        str(ROOT / name)
        for name in tracked
        if name.startswith("scripts/")
        or name.startswith("verification/")
        or name.startswith(".github/workflows/")
    ]
    data = json.loads(
        subprocess.check_output(
            ["cloc", "--json", "--by-file", "--skip-uniqueness", *tooling], text=True
        )
    )
    ancillary.append(
        {
            "stack": "shared",
            "category": "orchestration/measurement/verification",
            "code": data["SUM"]["code"],
            "files": [str(Path(path).relative_to(ROOT)) for path in tooling],
        }
    )
    target = ROOT / "results/code.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "tool": "cloc 2.10",
                "sourceRevision": subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
                ).strip(),
                "entries": output,
                "ancillary": ancillary,
                "exclusions": [
                    "dependencies",
                    "build outputs",
                    "generated asset copies and registration",
                    "dataset/artwork",
                    "lockfiles",
                    "inspection controls",
                    "root measurement/orchestration scripts",
                ],
                "scope": "Production UI/navigation, model plus extracted data-loading/persistence/lifecycle handlers, and retained native bootstrap. File split ranges are explicit; UI event binding remains UI. Tests, instrumentation and configuration are separate.",
            },
            indent=2,
        )
        + "\n"
    )
    print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
