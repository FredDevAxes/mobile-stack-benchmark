"""Combine recordings at recording start; normalize fps without changing duration."""

import json
import subprocess
from source_mode import ROOT

records = []
for platform, stacks in [
    ("android", ["flutter", "react-native", "compose"]),
    ("ios", ["flutter", "react-native", "swift"]),
]:
    paths = [ROOT / f"results/visuals/{platform}/{stack}/demo.mp4" for stack in stacks]
    duration = max(
        float(
            subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=nw=1:nk=1",
                    str(path),
                ],
                text=True,
            )
        )
        for path in paths
    )
    filters = []
    height = 842 if platform == "android" else 824
    for i, stack in enumerate(stacks):
        title = {
            "flutter": "Flutter",
            "react-native": "React Native",
            "compose": "Compose",
            "swift": "SwiftUI",
        }[stack]
        filters.append(
            f"[{i}:v]fps=30,scale=360:-2,pad=360:{height}:0:40:white,drawtext=text={title}:x=10:y=8:fontsize=22:fontcolor=black,tpad=stop_mode=clone:stop_duration=30,trim=duration={duration},setpts=PTS-STARTPTS[v{i}]"
        )
    filters.append("[v0][v1][v2]hstack=inputs=3[out]")
    target = ROOT / f"results/visuals/{platform}/comparison.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            *[arg for path in paths for arg in ["-i", str(path)]],
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[out]",
            "-an",
            "-c:v",
            "libx264",
            "-crf",
            "23",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(target),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    records.append(
        {
            "platform": platform,
            "output": str(target.relative_to(ROOT)),
            "durationSeconds": duration,
            "method": "Aligned at recording start, shorter panels hold last frame, normalized to 30 fps, no speed change, no timing ranking",
            "sources": [str(path.relative_to(ROOT)) for path in paths],
        }
    )
(ROOT / "results/visuals/video-method.json").write_text(json.dumps(records, indent=2) + "\n")
print("Two three-app demonstration videos")
