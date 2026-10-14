"""Validate the complete evidence cohort before identifying a verified milestone."""

from pathlib import Path
import json

from verify import fingerprint

r = Path(__file__).resolve().parents[1]

rows = []
build_records = json.loads((r / "results/builds.json").read_text())["records"]
revisions = {b["stack"]: b["build"]["source"]["revision"] for b in build_records}
assert all(b["build"]["source"]["revision"] == revisions[b["stack"]] for b in build_records)
expected_node = "v" + json.loads((r / "toolchain.json").read_text())["node"]
for platform, stacks in [
    ("android", ["flutter", "react-native", "compose"]),
    ("ios", ["flutter", "react-native", "swift"]),
]:
    for stack in stacks:
        for variant in ["S", "A"]:
            for flow in [
                "catalogue",
                "scroll",
                "android-back" if platform == "android" else "navigation-guard",
                *(["demo", "progress", "reduced-motion"] if variant == "A" else []),
            ]:
                p = r / f"results/verification/{stack}-{platform}-{variant}-{flow}.json"
                d = json.loads(p.read_text())
                assert d["exitCode"] == 0, (p, d["exitCode"])
                assert not d["sourceDirty"] and not d.get("flowDirty", True), p
                assert d["sourceRevision"] == revisions[stack], p
                for visual in d.get("visuals", []):
                    assert fingerprint(r / visual["path"]) == visual["sha256"], visual
                mode = "inspection" if flow in ["progress", "reduced-motion"] else "artifacts"
                b = r / f".work/{mode}/{stack}/{variant}"
                artifact = b / ("android.apk" if platform == "android" else "simulator.app")
                metadata = json.loads(
                    (
                        b / ("android.json" if platform == "android" else "simulator.json")
                    ).read_text()
                )
                assert d["artifactSHA256"] == fingerprint(artifact) == metadata["artifactSHA256"], p
                assert (
                    metadata["source"]["revision"] == revisions[stack]
                    and not metadata["source"]["dirty"]
                ), p
                if stack == "react-native":
                    assert metadata["nodeUsed"] == expected_node, p
                rows.append(
                    {
                        "stack": stack,
                        "platform": platform,
                        "variant": variant,
                        "flow": flow,
                        "record": str(p.relative_to(r)),
                        "status": "PASS",
                    }
                )
assert len(rows) == 54, len(rows)
geo = json.loads((r / "results/geometry.json").read_text())
assert len(geo["records"]) == 30 and all(v["withinTolerance"] for v in geo["records"])
scroll = json.loads((r / "results/scroll.json").read_text())
assert len(scroll["records"]) == 12
builds = json.loads((r / "results/builds.json").read_text())
assert len(builds["records"]) == 12
for b in builds["records"]:
    assert (
        b["build"]["source"]["revision"] == revisions[b["stack"]]
        and not b["build"]["source"]["dirty"]
    )
    assert b["architectures"] == (["arm64-v8a"] if b["platform"] == "android" else ["arm64"])
    if b["stack"] == "react-native":
        assert b["build"]["nodeUsed"] == expected_node
diagnostic = r / "results/diagnostics/android/samples.json"
if diagnostic.exists():
    samples = json.loads(diagnostic.read_text())["records"]
    assert len(samples) == 18
    assert len({(v["stack"], v["variant"], v["series"]) for v in samples}) == 18
    for sample in samples:
        assert (
            sample["sourceRevision"] == revisions[sample["stack"]]
            and sample["finalCatalogueVisible"]
        )
        artifact = r / f".work/artifacts/{sample['stack']}/{sample['variant']}/android.apk"
        assert sample["artifactSHA256"] == fingerprint(artifact)
(r / "results/acceptance.json").write_text(
    json.dumps(
        {
            "applicationSourceRevisions": revisions,
            "functionalAndVisualFlowsPassed": len(rows),
            "deterministicStagesWithinTolerance": 30,
            "geometryMaximumErrorLogical": max(
                v["maxAbsoluteErrorLogical"] for v in geo["records"]
            ),
            "listRetentionScreenshotPairs": 12,
            "comparableReleaseArtifacts": 12,
            "flowRecords": rows,
            "limits": [
                "No physical-device or store-distribution verification",
                "Driver cannot guarantee exact within-transition input timestamp",
                "Pixel geometry checks do not certify text metrics or accessibility",
            ],
        },
        indent=2,
    )
    + "\n"
)
print("Acceptance: 54 flows, 30 geometry stages, 12 scroll pairs, 12 comparable Release artifacts")
