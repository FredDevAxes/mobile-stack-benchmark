"""Measure opaque image bounds/corner samples in deterministic screenshots."""

import argparse
import json
import numpy as np
from PIL import Image
from source_mode import ROOT


def curve(time):
    lo, hi = 0.0, 1.0
    for _ in range(50):
        t = (lo + hi) / 2
        x = 3 * (1 - t) ** 2 * t * 0.4 + 3 * (1 - t) * t * t * 0.2 + t**3
        if x < time:
            lo = t
        else:
            hi = t
    t = (lo + hi) / 2
    return 3 * (1 - t) * t * t + t**3


def main(partial=False):
    palette = np.unique(
        np.asarray(Image.open(ROOT / "shared/images/gear-01.png").convert("RGB")).reshape(-1, 3),
        axis=0,
    )
    reference = np.asarray(Image.open(ROOT / "shared/images/gear-01.png").convert("RGB"))
    landmark_color = next(
        color for color in palette if color[0] > 200 and color[1] > 140 and color[2] < 130
    )
    ry, rx = np.where(np.all(reference == landmark_color, axis=2))
    landmark_source = [
        int(rx.min()),
        int(ry.min()),
        int(rx.max() - rx.min() + 1),
        int(ry.max() - ry.min() + 1),
    ]
    records = []
    for platform, stacks, scale, cap in [
        ("android", ["flutter", "react-native", "compose"], 420 / 160, 400),
        ("ios", ["flutter", "react-native", "swift"], 3, 450),
    ]:
        for stack in stacks:
            frames = []
            for time in [0, 25, 50, 75, 100]:
                path = ROOT / f"results/visuals/{platform}/{stack}/time-{time:03d}.png"
                if partial and not path.exists():
                    break
                image = np.asarray(Image.open(path).convert("RGB"))
                region = image[: round(cap * scale)]
                mask = np.zeros(region.shape[:2], dtype=bool)
                for color in palette:
                    mask |= np.all(region == color, axis=2)
                y, x = np.where(mask)
                if not len(x):
                    raise ValueError(f"No source colors in {path}")
                rect = [
                    float(x.min() / scale),
                    float(y.min() / scale),
                    float((x.max() - x.min() + 1) / scale),
                    float((y.max() - y.min() + 1) / scale),
                ]
                ly, lx = np.where(np.all(region == landmark_color, axis=2))
                if not len(lx):
                    raise ValueError(f"Source landmark missing in {path}")
                landmark = [
                    float(lx.min() / scale),
                    float(ly.min() / scale),
                    float((lx.max() - lx.min() + 1) / scale),
                    float((ly.max() - ly.min() + 1) / scale),
                ]
                frames.append((time, rect, mask, path, image.shape[1] / scale, landmark))
            if len(frames) != 5:
                continue
            origin = frames[-1][1][1] - 52
            width = frames[-1][4]
            for time, rect, mask, path, _, landmark in frames:
                p = curve(time / 100)
                expected = [16 * (1 - p), origin + 136 - 84 * p, width - 32 + 32 * p, 180 + 100 * p]
                delta = [a - b for a, b in zip(rect, expected)]
                radius = 16 * (1 - p)
                corner = []
                if radius >= 2:
                    for fraction in [0.25, 0.5]:
                        dy = radius * fraction
                        row = round((expected[1] + dy) * scale)
                        left = np.where(mask[row])[0]
                        wanted = (
                            expected[0] + radius - (radius * radius - (radius - dy) ** 2) ** 0.5
                        )
                        corner.append(float(left.min() / scale - wanted))
                zoom = max(expected[2] / 640, expected[3] / 400)
                expected_landmark = [
                    expected[0] + (expected[2] - 640 * zoom) / 2 + landmark_source[0] * zoom,
                    expected[1] + (expected[3] - 400 * zoom) / 2 + landmark_source[1] * zoom,
                    landmark_source[2] * zoom,
                    landmark_source[3] * zoom,
                ]
                landmark_delta = [a - b for a, b in zip(landmark, expected_landmark)]
                error = max(abs(v) for v in [*delta, *corner, *landmark_delta])
                records.append(
                    {
                        "stack": stack,
                        "platform": platform,
                        "timePercent": time,
                        "easedProgress": p,
                        "measuredBoundsLogical": rect,
                        "expectedBoundsLogical": expected,
                        "boundsErrorLogical": delta,
                        "cornerErrorLogical": corner,
                        "measuredLandmarkLogical": landmark,
                        "expectedCenteredCoverLandmarkLogical": expected_landmark,
                        "landmarkErrorLogical": landmark_delta,
                        "maxAbsoluteErrorLogical": error,
                        "withinTolerance": error <= 2,
                        "capture": str(path.relative_to(ROOT)),
                        "scale": scale,
                        "contentOriginY": origin,
                    }
                )
    result = {
        "method": "Exact source-palette color segmentation of opaque foreground image, restricted above second card. Safe-area origin inferred from stable detail image. Independent Bézier solver; corner samples at 25/50% of expected radius; an original amber rectangle checks centered cover crop and uniform scaling. Does not test text antialiasing or real-time speed.",
        "toleranceLogicalUnits": 2,
        "records": records,
    }
    (ROOT / "results/geometry.json").write_text(json.dumps(result, indent=2) + "\n")
    failed = [r for r in records if not r["withinTolerance"]]
    print(f"{len(records)} frame checks, {len(failed)} outside tolerance")
    for r in failed:
        print(
            r["platform"],
            r["stack"],
            r["timePercent"],
            r["boundsErrorLogical"],
            r["cornerErrorLogical"],
        )
    if failed:
        raise SystemExit(1)
    if not partial and len(records) != 30:
        raise ValueError("Expected six targets × five stages")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--partial", action="store_true")
    main(parser.parse_args().partial)
