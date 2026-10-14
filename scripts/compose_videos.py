"""Combine recordings at recording start; normalize fps without changing duration."""

from pathlib import Path
import json
import subprocess
from source_mode import ROOT
from PIL import Image, ImageDraw, ImageFont

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
    title_paths = []
    title_folder = ROOT / ".work/video-titles"
    title_folder.mkdir(parents=True, exist_ok=True)
    font_path = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
    font = (
        ImageFont.truetype(str(font_path), 22)
        if font_path.exists()
        else ImageFont.load_default(size=22)
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
        header = Image.new("RGB", (360, 40), "white")
        ImageDraw.Draw(header).text((10, 8), title, font=font, fill="black")
        title_path = title_folder / f"{stack}.png"
        header.save(title_path)
        title_paths.append(title_path)
        filters.append(
            f"[{i}:v]fps=30,scale=360:-2,pad=360:{height}:0:40:white,tpad=stop_mode=clone:stop_duration=30,trim=duration={duration},setpts=PTS-STARTPTS[base{i}];[base{i}][{i + 3}:v]overlay=0:0:shortest=1[v{i}]"
        )
    filters.append("[v0][v1][v2]hstack=inputs=3[out]")
    target = ROOT / f"results/visuals/{platform}/comparison.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            *[arg for path in paths for arg in ["-i", str(path)]],
            *[
                arg
                for path in title_paths
                for arg in ["-loop", "1", "-framerate", "30", "-i", str(path)]
            ],
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
            "labels": "Pillow-rendered title bars outside app pixels; does not require optional FFmpeg drawtext",
        }
    )
(ROOT / "results/visuals/video-method.json").write_text(json.dumps(records, indent=2) + "\n")
print("Two three-app demonstration videos")
