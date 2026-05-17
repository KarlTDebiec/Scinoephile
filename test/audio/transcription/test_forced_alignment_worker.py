#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the forced-alignment worker."""

from __future__ import annotations

from types import SimpleNamespace
from typing import cast

import pytest

from scinoephile.audio.transcription import forced_alignment_worker


def test_align_with_whisperx_returns_json_ready_segments(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test the worker can run WhisperX alignment without package models."""
    fake_whisperx = SimpleNamespace(
        align=lambda **_kwargs: {
            "segments": [
                {
                    "start": 0.0,
                    "end": 1.0,
                    "text": "你好",
                    "words": [
                        {
                            "word": "你",
                            "start": 0.0,
                            "end": 0.4,
                            "score": 0.9,
                        }
                    ],
                }
            ]
        },
        load_align_model=lambda **_kwargs: ("model", {"language": "zh"}),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.forced_alignment_worker._get_whisperx_module",
        lambda: fake_whisperx,
    )

    payload = forced_alignment_worker.align_with_whisperx(
        {
            "audio_path": "/tmp/audio.wav",
            "text": "你好",
            "duration_seconds": 1.0,
            "language": "zh",
            "model_name": "custom/aligner",
            "device": "cpu",
        }
    )

    segments = cast(list[dict[str, object]], payload["segments"])
    assert segments[0]["text"] == "你好"
