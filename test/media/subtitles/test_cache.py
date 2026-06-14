#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle stream caching."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import ffmpeg
import pytest
from PIL import Image

from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from scinoephile.media.subtitles.cache import (
    cache_subtitles,
    get_subtitle_cache_path,
)
from test.helpers.media_subtitles import (
    cache_subtitle_stream,
    get_image_subtitle_dir_path,
)


def test_get_cached_subtitle_stream_path_changes_by_stream(tmp_path: Path):
    """Test subtitle stream cache paths include stream identity.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")

    first = get_subtitle_cache_path(
        infile_path,
        SubtitleStream(index=2, language="zho", codec_name="subrip"),
        cache_dir_path=tmp_path / "cache",
    )
    second = get_subtitle_cache_path(
        infile_path,
        SubtitleStream(index=3, language="zho", codec_name="subrip"),
        cache_dir_path=tmp_path / "cache",
    )
    same_stream_with_script = get_subtitle_cache_path(
        infile_path,
        SubtitleStream(index=2, language="zho-Hant", codec_name="subrip"),
        cache_dir_path=tmp_path / "cache",
    )

    assert first != second
    assert first == same_stream_with_script
    assert first.suffix == ".srt"
    assert second.suffix == ".srt"


def test_cache_subtitle_streams_uses_existing_stream(tmp_path: Path):
    """Test existing cached subtitle streams are reused.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache_subtitle_stream(infile_path, stream, tmp_path / "cache", b"")

    with patch("scinoephile.media.subtitles.cache.ffmpeg.input") as ffmpeg_input:
        cache_subtitles(
            infile_path,
            [stream],
            cache_dir_path=tmp_path / "cache",
        )

    ffmpeg_input.assert_not_called()


def test_cache_subtitles_wraps_ffmpeg_extraction_errors(tmp_path: Path):
    """Test subtitle caching surfaces ffmpeg failures as ScinoephileError.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    input_stream = Mock()
    input_stream.output.return_value = Mock()
    merged_stream = Mock()
    merged_stream.run.side_effect = ffmpeg.Error("ffmpeg", b"", b"failed")

    with (
        patch(
            "scinoephile.media.subtitles.cache.ffmpeg.input",
            return_value=input_stream,
        ),
        patch(
            "scinoephile.media.subtitles.cache.ffmpeg.merge_outputs",
            return_value=merged_stream,
        ),
        pytest.raises(ScinoephileError, match="Could not cache subtitle streams"),
    ):
        cache_subtitles(
            infile_path,
            [stream],
            cache_dir_path=tmp_path / "cache",
        )


def test_cache_subtitles_builds_image_cache_for_sup_stream(tmp_path: Path):
    """Test subtitle caching renders cached SUP subtitle images.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="hdmv_pgs_subtitle")
    cache_subtitle_stream(infile_path, stream, tmp_path / "cache", b"not a real sup")
    image_series = ImageSeries(
        events=[
            ImageSubtitle(
                start=1000,
                end=2000,
                img=Image.new("RGBA", (10, 8), (255, 255, 255, 0)),
            ),
        ]
    )

    with patch(
        "scinoephile.media.subtitles.cache.ImageSeries.load",
        return_value=image_series,
    ):
        cache_subtitles(
            infile_path,
            [stream],
            cache_dir_path=tmp_path / "cache",
        )

    image_dir_path = get_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    assert (image_dir_path / "index.html").exists()


def test_cache_subtitles_can_skip_image_cache_for_sup_stream(tmp_path: Path):
    """Test subtitle caching can skip rendering cached SUP subtitle images.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="hdmv_pgs_subtitle")
    cache_subtitle_stream(infile_path, stream, tmp_path / "cache", b"not a real sup")

    with patch(
        "scinoephile.media.subtitles.cache.ImageSeries.load",
        side_effect=ValueError("SUP segment data is truncated."),
    ) as load:
        cache_subtitles(
            infile_path,
            [stream],
            cache_dir_path=tmp_path / "cache",
            render_images=False,
        )

    load.assert_not_called()


def test_cache_subtitle_streams_extracts_missing_streams(tmp_path: Path):
    """Test subtitle stream cache extracts missing streams with ffmpeg.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    streams = [
        SubtitleStream(index=2, language="eng", codec_name="subrip"),
        SubtitleStream(index=3, language="zho", codec_name="subrip"),
    ]

    with (
        patch("scinoephile.media.subtitles.cache.ffmpeg.input") as ffmpeg_input,
        patch(
            "scinoephile.media.subtitles.cache.ffmpeg.merge_outputs"
        ) as merge_outputs,
    ):
        cache_subtitles(
            infile_path,
            streams,
            cache_dir_path=tmp_path / "cache",
        )

    first_stream_path = get_subtitle_cache_path(
        infile_path,
        streams[0],
        cache_dir_path=tmp_path / "cache",
    )
    second_stream_path = get_subtitle_cache_path(
        infile_path,
        streams[1],
        cache_dir_path=tmp_path / "cache",
    )
    output = ffmpeg_input.return_value.output
    assert output.call_count == 2
    assert {
        (call.args[0], call.kwargs["map"], call.kwargs["c:s"])
        for call in output.call_args_list
    } == {
        (str(first_stream_path), "0:2", "subrip"),
        (str(second_stream_path), "0:3", "subrip"),
    }
    merge_outputs.assert_called_once()
    merge_outputs.return_value.run.assert_called_once()
    assert first_stream_path.parent.exists()
    assert second_stream_path.parent.exists()
