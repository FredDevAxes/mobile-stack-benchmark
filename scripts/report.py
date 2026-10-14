"""Render tables and figures from retained evidence; no synthetic benchmark values."""

from pathlib import Path
import json
import statistics
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from source_mode import ROOT

NAMES = {
    "flutter": "Flutter",
    "react-native": "React Native",
    "compose": "Compose",
    "swift": "SwiftUI",
}
COLORS = {"flutter": "#327cb7", "react-native": "#73479a", "compose": "#26785d", "swift": "#b55b25"}


def load(name):
    return json.loads((ROOT / "results" / name).read_text())


def main():
    builds, code = load("builds.json"), load("code.json")
    out = ROOT / "results/figures"
    out.mkdir(parents=True, exist_ok=True)
    revisions = {row["stack"]: row["build"]["source"]["revision"] for row in builds["records"]}
    assert all(
        row["build"]["source"]["revision"] == revisions[row["stack"]]
        and not row["build"]["source"]["dirty"]
        for row in builds["records"]
    ), "Mixed within-stack revisions or dirty artifact sources"
    text = [
        "# Results — virtual-device milestone",
        "",
        "Milestone: `v0.1.0-virtual-devices`. Clean application source revisions are retained per stack in [builds.json](builds.json); each stack uses the same revision for all S/A artifacts and checks.",
        "",
        "This is one offline catalogue with 200 fictional products and 20 shared original illustrations. It measures these implementations and build settings. It does not identify a universally best mobile stack.",
        "",
        "## Build sizes",
        "",
        "Android numbers are complete arm64-v8a Release APK file bytes. iOS numbers are unsigned device arm64 Release `.app` logical regular-file bytes; duplicate symlink targets and external symbols are excluded. MiB means 1,048,576 bytes. No store download, installed footprint, AAB or IPA is measured.",
        "",
    ]
    for platform, stacks in [
        ("android", ["flutter", "react-native", "compose"]),
        ("ios", ["flutter", "react-native", "swift"]),
    ]:
        text += [
            f"### {platform.upper()}",
            "",
            "| Stack | S bytes | A bytes | A − S bytes | S MiB | A MiB |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
        sizes = []
        for stack in stacks:
            pair = {
                r["variant"]: r["bytes"]
                for r in builds["records"]
                if r["platform"] == platform and r["stack"] == stack
            }
            s, a = pair["S"], pair["A"]
            sizes.append((stack, s, a))
            text += [
                f"| {NAMES[stack]} | {s:,} | {a:,} | {a - s:+,} | {s / 1048576:.3f} | {a / 1048576:.3f} |"
            ]
        fig, ax = plt.subplots(figsize=(8, 3.6), layout="constrained")
        for index, (stack, s, a) in enumerate(sizes):
            ax.barh(index - 0.16, s / 1048576, height=0.3, color=COLORS[stack], alpha=0.45)
            ax.barh(index + 0.16, a / 1048576, height=0.3, color=COLORS[stack])
            ax.text(
                a / 1048576 + 0.15, index + 0.16, f"{a / 1048576:.2f}", va="center", fontsize=10
            )
        ax.set_yticks(range(3), [NAMES[s] for s in stacks])
        ax.invert_yaxis()
        ax.set_xlabel("MiB · light = instant S · dark = animated A")
        ax.set_title(
            "Android · complete arm64 APK"
            if platform == "android"
            else "iOS · unsigned arm64 device app bundle"
        )
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="x", alpha=0.15)
        ax.set_axisbelow(True)
        fig.savefig(out / f"{platform}-sizes.png", dpi=180)
        plt.close(fig)
        text += ["", f"![{platform} build sizes](figures/{platform}-sizes.png)", ""]
    text += [
        "Evidence: [all artifact identities, commands, settings and per-file source hashes](builds.json). All Android builds shrink/minify release code and resources; Flutter also tree-shakes Dart/icons. Flutter uses a split APK to exclude foreign-ABI plugin libraries. RN bundles Hermes bytecode and uses its release defaults; SwiftUI uses `swiftc -O` and `strip -S` against system frameworks. These ecosystem settings are disclosed rather than assumed identical.",
        "",
        "The A − S difference includes compiler optimization and packaging effects. A small or negative delta does not mean the animation has no runtime cost. Framework libraries used by the catalogue remain in S.",
        "",
        "## Formatted maintained source",
        "",
        "| Stack | Variant | UI/navigation | Model, loading, persistence/lifecycle | Navigation module | Platform bootstrap | Application total | Tests |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in code["entries"]:
        c = row["categories"]
        text += [
            f"| {NAMES[row['stack']]} | {row['variant']} | {c['ui']} | {c['logic']} | {c['navigation']} | {c['platform']} | {row['applicationTotal']} | {c['tests']} |"
        ]
    text += ["", "| Coverage | S lines | A lines | A − S |", "| --- | ---: | ---: | ---: |"]
    for label, stacks in [
        ("Flutter, Android + iOS", ["flutter"]),
        ("React Native, Android + iOS", ["react-native"]),
        ("Native, Compose + SwiftUI", ["compose", "swift"]),
    ]:
        pair = {
            v: sum(
                r["applicationTotal"]
                for r in code["entries"]
                if r["stack"] in stacks and r["variant"] == v
            )
            for v in ["S", "A"]
        }
        text += [f"| {label} | {pair['S']} | {pair['A']} | {pair['A'] - pair['S']:+} |"]
    text += [
        "",
        "Shared Flutter/RN screens are counted once. Native coverage is the sum of Kotlin and Swift. cloc 2.10 counts nonblank noncomment lines after language-specific formatting. The file manifest, extracted handler ranges, hashes, separate tests, inspection controls, configuration and shared tooling are in [code.json](code.json). Lifecycle code in the extracted persistence handlers is included; UI bindings stay with UI. Configuration files unrecognized by cloc are explicitly listed with zero recognized lines, not counted as application source.",
        "",
        "These counts describe the maintained implementation, including adapted bootstrap files. They do not measure quality, delivery effort, maintainability or developer productivity. Work was implemented sequentially with AI assistance; no reliable time diary was collected.",
        "",
        "## Functional and visual verification",
        "",
        "The installed S/A variants run the same catalogue search, empty-state, favorites/persistence and return-to-list flow. Separate scroll flows exercise a lower item and retain the list position. Repeated card input and button back are exercised on iOS; Android additionally exercises system back. Inspection builds expose the five fixed timeline stages and the actual reduced-motion flag; those controls are excluded from size artifacts and diagnostics.",
        "",
        "See [per-target verification records](verification/), [all retained driver attempts, including failures](trials.json), [geometry checks](geometry.json), [environment](environment.json) and [protocol](../docs/protocol.md). Driver execution time is not application latency. The repeated-input driver cannot prove the exact timestamp of an input within a 400 ms transition; the input guards and queued-back implementation remain available for review.",
        "",
        "Historical failed attempts include incorrect inaccessible title selectors, clipped tap targets and an unexplained Flutter scroll/capture failure that passed on retry. They are retained rather than treated as zero or silently discarded. Latest milestone pass reports are separate from earlier dirty-source exploratory attempts.",
        "",
    ]
    accepted = load("acceptance.json")
    text += [
        "| Target | S functional | A functional | Five timeline stages | Reduced motion | Runtime mode |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for platform, stacks in [
        ("android", ["flutter", "react-native", "compose"]),
        ("ios", ["flutter", "react-native", "swift"]),
    ]:
        for stack in stacks:
            mode = "Debug" if platform == "ios" and stack == "flutter" else "Release/optimized"
            text += [
                f"| {NAMES[stack]} · {platform.upper()} | PASS | PASS | PASS | PASS | {mode} |"
            ]
    text += [
        "",
        f"[Acceptance gate](acceptance.json): {accepted['functionalAndVisualFlowsPassed']} successful flows and 30 deterministic stages. Maximum geometry/corner/landmark error: {accepted['geometryMaximumErrorLogical']:.3f} logical units against the 2-unit tolerance. An original amber landmark verifies centered uniform cover crop. Text antialiasing and actual animation speed are outside this pixel check.",
        "",
        "List before/after screenshot pairs and cropped pixel differences are retained in [scroll.json](scroll.json). These are same-device comparisons, not cross-platform text matching.",
        "",
        "[Fresh public-clone reproduction](reproduction.json) executed locked dependency installation, all project linters/tests and a SwiftUI S build. The complete 18-output build matrix was executed on the reference working tree; hosted [CI](ci.json) independently compiles all supported targets. Those scopes are kept separate.",
        "",
    ]
    for platform in ["android", "ios"]:
        text += [
            f"![{platform} timeline](figures/{platform}-timeline.png)",
            "",
            f"[Three-app {platform} demonstration](visuals/{platform}/comparison.mp4). Individual source recordings remain in each stack directory. Demonstration recordings are normalized to 30 fps, aligned at recording start, without a speed change; gesture/dump delays differ, so the panels are not a synchronized performance experiment.",
            "",
        ]
    diagnostic = ROOT / "results/diagnostics/android/samples.json"
    text += ["## Runtime diagnostics", ""]
    if diagnostic.exists():
        memory = load("diagnostics/android/samples.json")
        text += [
            "Android guest-process TOTAL PSS from `dumpsys meminfo`, KiB. Each series runs the first cycle separately, 5 warmups and 30 recorded cycles, with one second stable rest and alternating order. The table summarizes the three after-series snapshots, not a 30-frame distribution. Host emulator/GPU allocations and physical-device memory are outside coverage.",
            "",
            "| Stack | Variant | Series | Median after KiB | Min–max after KiB | Median before KiB |",
            "| --- | --- | ---: | ---: | --- | ---: |",
        ]
        for stack in ["flutter", "react-native", "compose"]:
            for variant in ["S", "A"]:
                rows = [
                    r for r in memory["records"] if r["stack"] == stack and r["variant"] == variant
                ]
                if not rows:
                    continue
                after = [r["pssAfterKiB"] for r in rows]
                before = [r["pssBeforeKiB"] for r in rows]
                text += [
                    f"| {NAMES[stack]} | {variant} | {len(rows)} | {statistics.median(after):,.0f} | {min(after):,}–{max(after):,} | {statistics.median(before):,.0f} |"
                ]
        text += [
            "",
            "Per-series snapshots:",
            "",
            "| Stack | Variant | Series | Before KiB | After KiB | After − before KiB |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
        for row in memory["records"]:
            text += [
                f"| {NAMES[row['stack']]} | {row['variant']} | {row['series']} | {row['pssBeforeKiB']:,} | {row['pssAfterKiB']:,} | {row['pssAfterKiB'] - row['pssBeforeKiB']:+,} |"
            ]
        text += [
            "",
            "[Samples and raw meminfo/gfxinfo traces](diagnostics/android/). Three snapshots per variant do not establish significance or a memory leak. Android gfxinfo has different render coverage across stacks, so no common frame-time/jank ranking is published.",
            "",
        ]
    text += [
        "| Metric | Status and reason |",
        "| --- | --- |",
        "| Input-to-first-change latency | Unavailable: no validated common timestamp source |",
        "| Frame times / jank | Unavailable as a common comparison: Flutter render coverage differs from native HWUI |",
        "| Observed animation duration | Not measured; 400 ms is the programmed contract |",
        "| iOS process memory / CPU | Not ranked: Flutter simulator Debug differs from RN/SwiftUI Release, and host RSS is not iPhone memory |",
        "| D1 scroll performance | Functional scroll retention verified; performance sequence not validated |",
        "| D2 usable startup | Unavailable: process launch and usable catalogue markers not jointly validated |",
        "",
        "## Limits and dependencies",
        "",
        "The devices are virtual, with one reference size per platform, default text size and light portrait rendering. System fonts differ, and safe-area origins are measured separately. Twenty reused illustrations do not represent 200 unique photographs, network loading, a complex business app, accessibility certification or store distribution. Device iOS bundles compile but were not installed on physical phones; no distribution signing or IPA export is claimed.",
        "",
        "Pinned versions and locks are in [toolchain.json](../toolchain.json), pubspec.lock, package-lock.json, Podfile.lock, Gemfile.lock, Gradle locks/wrapper hashes and requirements.lock. Flutter native dependency declarations come from its pinned SDK/plugins; the Gradle engine plugin is not independently reimplemented. Hosted runner OS images can change. Reproduction means the documented checks/builds work with declared inputs, not guaranteed byte-for-byte signing, compiler or archive timestamps.",
        "",
        "The retained [RN npm audit](dependency-audit.json) reports 53 inherited tooling advisories (5 moderate, 48 high), from the locked dependency tree, principally braces/sprintf-js chains. Compatible updates were applied; the suggested framework downgrade was not accepted. This lab is not a production security certification. Preserve upstream licenses and review advisories before reuse. No credentials or private signing material are tracked.",
        "",
        "[Exploratory Node 25.6 size records](history/node25-exploratory-builds.json) are retained separately. A generated Xcode path overrode the declared Node version; the final cohort was rebuilt with Node 24.13 selected and recorded. The final Flutter cohort additionally fixes the distinct iOS Reduce Motion flag discovered by the OS probe. The other six app projections are unchanged. The final table uses only clean sources and the declared Node runtime.",
        "",
        "The narrower conclusion is that this catalogue can be inspected across four implementations with source-isolated animation variants. Use the actual within-platform size deltas and maintained-source counts; do not turn them into a global score or a claim about every project.",
        "",
    ]
    (ROOT / "results/REPORT.md").write_text("\n".join(text))
    font = (
        ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 20)
        if Path("/System/Library/Fonts/Supplemental/Arial.ttf").exists()
        else ImageFont.load_default()
    )
    for platform, stacks in [
        ("android", ["flutter", "react-native", "compose"]),
        ("ios", ["flutter", "react-native", "swift"]),
    ]:
        cellw, cellh = 230, 550
        canvas = Image.new("RGB", (cellw * 5, cellh * 3), "#ffffff")
        draw = ImageDraw.Draw(canvas)
        for row, stack in enumerate(stacks):
            for col, time in enumerate([0, 25, 50, 75, 100]):
                path = ROOT / f"results/visuals/{platform}/{stack}/time-{time:03d}.png"
                screenshot = Image.open(path).convert("RGB")
                screenshot.thumbnail((cellw - 12, cellh - 48))
                draw.text(
                    (col * cellw + 8, row * cellh + 8),
                    f"{NAMES[stack]} · {time}%",
                    font=font,
                    fill="#263d34",
                )
                canvas.paste(
                    screenshot, (col * cellw + (cellw - screenshot.width) // 2, row * cellh + 42)
                )
        canvas.save(out / f"{platform}-timeline.png")
    print("results/REPORT.md and four evidence figures")


if __name__ == "__main__":
    main()
