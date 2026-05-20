#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media audio cache helpers."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core.media import AudioStream
from scinoephile.media.audio import get_media_audio_cache_path


def test_get_media_audio_cache_path_includes_stream_and_downmix(
    tmp_path: Path,
):
    """Test audio cache paths are separated by stream and downmix semantics.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    media_path = tmp_path / "movie.mkv"
    media_path.write_bytes(b"media")
    cache_dir_path = tmp_path / "cache"
    stereo_stream = AudioStream(
        index=12,
        codec_type="audio",
        codec_name="ac3",
        channels=2,
    )
    surround_stream = AudioStream(
        index=12,
        codec_type="audio",
        codec_name="ac3",
        channels=6,
    )
    other_stream = AudioStream(
        index=13,
        codec_type="audio",
        codec_name="ac3",
        channels=2,
    )

    stereo_path = get_media_audio_cache_path(
        media_path,
        stereo_stream,
        cache_dir_path=cache_dir_path,
    )
    surround_path = get_media_audio_cache_path(
        media_path,
        surround_stream,
        cache_dir_path=cache_dir_path,
    )
    other_path = get_media_audio_cache_path(
        media_path,
        other_stream,
        cache_dir_path=cache_dir_path,
    )

    assert stereo_path.parent.parent == cache_dir_path.resolve()
    assert stereo_path.name == "audio.wav"
    assert stereo_path != surround_path
    assert stereo_path != other_path
