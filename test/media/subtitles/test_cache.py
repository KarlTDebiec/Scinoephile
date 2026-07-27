#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle stream caching."""

from __future__ import annotations

from pathlib import Path
from time import time
from unittest.mock import Mock, patch

import ffmpeg
from PIL import Image
from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from scinoephile.media.subtitles.cache import SubtitleCache
from test.helpers.files import set_mtime
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
    cache = SubtitleCache(tmp_path / "cache")

    assert cache.cache_dir_path == (tmp_path / "cache" / "media" / "subtitles")

    first = cache.get_path(
        infile_path,
        SubtitleStream(index=2, language="zho", codec_name="subrip"),
    )
    second = cache.get_path(
        infile_path,
        SubtitleStream(index=3, language="zho", codec_name="subrip"),
    )
    same_stream_with_script = cache.get_path(
        infile_path,
        SubtitleStream(index=2, language="zho-Hant", codec_name="subrip"),
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
    cache = SubtitleCache(tmp_path / "cache")
    cache_subtitle_stream(infile_path, stream, tmp_path / "cache", b"")

    with patch("scinoephile.media.subtitles.cache.ffmpeg.input") as ffmpeg_input:
        cache.cache(infile_path, [stream])

    ffmpeg_input.assert_not_called()


def test_cache_subtitle_streams_marks_existing_stream_used(tmp_path: Path):
    """Test a subtitle stream cache hit refreshes its pruning timestamp."""
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache = SubtitleCache(tmp_path / "cache")
    stream_path = cache_subtitle_stream(
        infile_path,
        stream,
        tmp_path / "cache",
        b"cached",
    )
    old_timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(stream_path, old_timestamp)

    with patch("scinoephile.media.subtitles.cache.ffmpeg.input") as ffmpeg_input:
        cache.cache(infile_path, [stream])

    ffmpeg_input.assert_not_called()
    assert stream_path.stat().st_mtime > old_timestamp


def test_cache_subtitle_streams_overwrites_existing_stream(tmp_path: Path):
    """Test cache overwrite re-extracts and replaces a matching subtitle stream."""
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache = SubtitleCache(tmp_path / "cache", overwrite=True)
    stream_path = cache.get_path(infile_path, stream)
    cache_subtitle_stream(
        infile_path,
        stream,
        tmp_path / "cache",
        b"stale",
    )
    input_stream = _RecordingFfmpegInput()
    merged_streams: list[_RecordingMergedFfmpegStream] = []

    def merge_outputs(*outputs: Path) -> _RecordingMergedFfmpegStream:
        """Create a recording merged ffmpeg stream for staged outputs."""
        merged_stream = _RecordingMergedFfmpegStream(list(outputs))
        merged_streams.append(merged_stream)
        return merged_stream

    with (
        patch(
            "scinoephile.media.subtitles.cache.ffmpeg.input",
            return_value=input_stream,
        ),
        patch(
            "scinoephile.media.subtitles.cache.ffmpeg.merge_outputs",
            side_effect=merge_outputs,
        ),
    ):
        cache.cache(infile_path, [stream])
        cache.cache(infile_path, [stream])

    assert len(merged_streams) == 1
    assert merged_streams[0].run_count == 1
    assert stream_path.read_bytes() == b"cached"


def test_cache_subtitles_wraps_ffmpeg_extraction_errors(tmp_path: Path):
    """Test subtitle caching surfaces ffmpeg failures as ScinoephileError.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache = SubtitleCache(tmp_path / "cache")
    input_stream = Mock()

    def write_partial_output(outfile_path: str, **_: object) -> Mock:
        """Write a partial ffmpeg output before extraction fails."""
        Path(outfile_path).write_bytes(b"partial")
        return Mock()

    input_stream.output.side_effect = write_partial_output
    merged_stream = Mock()
    merged_stream.run.side_effect = ffmpeg.Error("ffmpeg", b"", b"failed")
    stream_path = cache.get_path(infile_path, stream)

    with (
        patch(
            "scinoephile.media.subtitles.cache.ffmpeg.input",
            return_value=input_stream,
        ),
        patch(
            "scinoephile.media.subtitles.cache.ffmpeg.merge_outputs",
            return_value=merged_stream,
        ),
        raises(ScinoephileError, match="Could not cache subtitle streams"),
    ):
        cache.cache(infile_path, [stream])

    assert not stream_path.exists()
    assert list(stream_path.parent.glob(f".{stream_path.name}-*")) == []


def test_cache_subtitles_builds_image_cache_for_sup_stream(tmp_path: Path):
    """Test subtitle caching renders cached SUP subtitle images.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="hdmv_pgs_subtitle")
    cache = SubtitleCache(tmp_path / "cache")
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
        cache.cache(infile_path, [stream])

    image_dir_path = get_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_root_path=tmp_path / "cache",
    )
    assert (image_dir_path / "index.html").exists()


def test_cache_subtitles_marks_existing_image_series_used(tmp_path: Path):
    """Test an image-series cache hit refreshes its pruning timestamp."""
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="hdmv_pgs_subtitle")
    cache = SubtitleCache(tmp_path / "cache")
    cache_subtitle_stream(infile_path, stream, tmp_path / "cache", b"cached")
    image_dir_path = get_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_root_path=tmp_path / "cache",
    )
    image_dir_path.mkdir()
    index_path = image_dir_path / "index.html"
    index_path.write_text("index", encoding="utf-8")
    old_timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(index_path, old_timestamp)

    with patch("scinoephile.media.subtitles.cache.ImageSeries.load") as load:
        cache.cache(infile_path, [stream])

    load.assert_not_called()
    assert index_path.stat().st_mtime > old_timestamp


def test_cache_subtitles_can_skip_image_cache_for_sup_stream(tmp_path: Path):
    """Test subtitle caching can skip rendering cached SUP subtitle images.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="hdmv_pgs_subtitle")
    cache = SubtitleCache(tmp_path / "cache")
    cache_subtitle_stream(infile_path, stream, tmp_path / "cache", b"not a real sup")

    with patch(
        "scinoephile.media.subtitles.cache.ImageSeries.load",
        side_effect=ValueError("SUP segment data is truncated."),
    ) as load:
        cache.cache(infile_path, [stream], render_images=False)

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
    cache = SubtitleCache(tmp_path / "cache")
    input_stream = _RecordingFfmpegInput()
    merged_streams: list[_RecordingMergedFfmpegStream] = []

    def merge_outputs(*outputs: Path) -> _RecordingMergedFfmpegStream:
        """Record merged ffmpeg outputs."""
        merged_stream = _RecordingMergedFfmpegStream(list(outputs))
        merged_streams.append(merged_stream)
        return merged_stream

    with (
        patch(
            "scinoephile.media.subtitles.cache.ffmpeg.input",
            return_value=input_stream,
        ),
        patch(
            "scinoephile.media.subtitles.cache.ffmpeg.merge_outputs",
            side_effect=merge_outputs,
        ),
    ):
        cache.cache(infile_path, streams)

    first_stream_path = cache.get_path(infile_path, streams[0])
    second_stream_path = cache.get_path(infile_path, streams[1])
    assert {
        (Path(path).name, mapping, codec)
        for path, mapping, codec in input_stream.output_calls
    } == {
        (first_stream_path.name, "0:2", "subrip"),
        (second_stream_path.name, "0:3", "subrip"),
    }
    assert {Path(path).parent.parent for path, _, _ in input_stream.output_calls} == {
        first_stream_path.parent,
        second_stream_path.parent,
    }
    assert len(merged_streams) == 1
    assert len(merged_streams[0].outputs) == 2
    assert merged_streams[0].run_count == 1
    assert first_stream_path.read_bytes() == b"cached"
    assert second_stream_path.read_bytes() == b"cached"
    assert all(not Path(path).exists() for path, _, _ in input_stream.output_calls)


class _RecordingFfmpegInput:
    """Recording fake for an ffmpeg input stream."""

    def __init__(self):
        """Initialize."""
        self.output_calls: list[tuple[str, str, str]] = []

    def output(self, outfile_path: str, **kwargs: object) -> Path:
        """Record an ffmpeg output stream.

        Arguments:
            outfile_path: output file path
            kwargs: ffmpeg output keyword arguments
        Returns:
            fake output stream
        """
        self.output_calls.append((outfile_path, str(kwargs["map"]), str(kwargs["c:s"])))
        return Path(outfile_path)


class _RecordingMergedFfmpegStream:
    """Recording fake for merged ffmpeg output streams."""

    def __init__(self, outputs: list[Path]):
        """Initialize.

        Arguments:
            outputs: ffmpeg output streams to merge
        """
        self.outputs = outputs
        self.run_count = 0

    def run(self, **kwargs: object):
        """Record ffmpeg execution.

        Arguments:
            kwargs: ffmpeg run keyword arguments
        """
        _ = kwargs
        self.run_count += 1
        for output in self.outputs:
            output.write_bytes(b"cached")
