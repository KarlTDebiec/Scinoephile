#!/usr/bin/env python3
"""Create sample video for audio tests."""

from __future__ import annotations

import subprocess
from pathlib import Path


def create_sample_video(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-f",
            "lavfi",
            "-i",
            "testsrc=size=320x240:duration=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=1000:duration=2",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-y",
            str(path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


if __name__ == "__main__":
    create_sample_video(Path("sample.mp4"))
