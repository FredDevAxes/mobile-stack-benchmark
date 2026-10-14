"""Compare retained list pixels before/after detail on each target and variant."""

import json
import numpy as np
from PIL import Image
from source_mode import ROOT

records = []
for platform, stacks in [
    ("android", ["flutter", "react-native", "compose"]),
    ("ios", ["flutter", "react-native", "swift"]),
]:
    for stack in stacks:
        for variant in ["S", "A"]:
            base = ROOT / f"results/visuals/{platform}/{stack}/{variant}"
            a = np.asarray(Image.open(base / "scroll-before.png").convert("RGB"))
            b = np.asarray(Image.open(base / "scroll-after.png").convert("RGB"))
            if a.shape != b.shape:
                raise ValueError("Mismatched screenshot dimensions")
            h = a.shape[0]
            before = a[round(h * 0.25) : round(h * 0.95)]
            after = b[round(h * 0.25) : round(h * 0.95)]
            difference = np.any(before != after, axis=2)
            changed = float(np.mean(difference))
            ys, xs = np.where(difference)
            bounds = (
                [
                    int(xs.min()),
                    int(ys.min() + round(h * 0.25)),
                    int(xs.max()),
                    int(ys.max() + round(h * 0.25)),
                ]
                if len(xs)
                else None
            )
            # The card reference reserves a 16-unit right margin for the scrollbar.
            scale = 2.625 if platform == "android" else 3
            content_changed = float(np.mean(difference[:, : -round(16 * scale)]))
            if float(np.mean(before)) < 20 or float(np.mean(after)) < 20:
                raise ValueError("Blank capture is not retention evidence")
            records.append(
                {
                    "platform": platform,
                    "stack": stack,
                    "variant": variant,
                    "listCropVerticalFraction": [0.25, 0.95],
                    "differingPixelFraction": changed,
                    "exactPixelsRetained": changed == 0,
                    "differingPixelBoundsPx": bounds,
                    "rightMarginExcludedLogicalUnits": 16,
                    "contentDifferingPixelFraction": content_changed,
                    "contentPixelsRetained": content_changed == 0,
                    "files": [
                        str((base / name).relative_to(ROOT))
                        for name in ["scroll-before.png", "scroll-after.png"]
                    ],
                }
            )
(ROOT / "results/scroll.json").write_text(
    json.dumps(
        {
            "method": "Pixel difference of same-device screenshots cropped to 25–95% of screen height, excludes clock/header/home indicator. Also record the differing pixel bounds and content difference excluding the outer 16 logical units reserved by the card margin; this isolates the system scrollbar without masking card content. Differences are observations, not automatically app failures. Functional unique-detail and return selectors are checked separately.",
            "records": records,
        },
        indent=2,
    )
    + "\n"
)
print("12 retained list comparisons")
