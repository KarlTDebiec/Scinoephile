#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle stream script analysis."""

from __future__ import annotations

from pathlib import Path
from typing import cast
from unittest.mock import patch

from PIL import Image

from scinoephile.core.media import SubtitleStream
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from scinoephile.lang.zho.subtitle_streams import analyze_zho_subtitle_stream_script
from scinoephile.media.subtitles.cache import (
    _get_cached_image_subtitle_dir_path,
    cache_subtitles,
    get_subtitle_cache_path,
    is_valid_image_subtitle_cache,
)
from scinoephile.media.subtitles.stats import get_subtitle_stream_stats


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
    _cache_subtitle_stream(infile_path, stream, tmp_path / "cache", b"")

    with patch("scinoephile.media.subtitles.cache.ffmpeg.input") as ffmpeg_input:
        cache_subtitles(
            infile_path,
            [stream],
            cache_dir_path=tmp_path / "cache",
        )

    ffmpeg_input.assert_not_called()


def test_analyze_text_subtitle_stream_uses_cached_stream(tmp_path: Path):
    """Test text subtitle stream analysis reads cached extracted subtitles.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    _cache_subtitle_stream(
        infile_path,
        stream,
        tmp_path / "cache",
        "1\n00:00:00,000 --> 00:00:01,000\n简体中文汉字\n",
    )

    with patch("scinoephile.media.subtitles.cache.ffmpeg.input") as ffmpeg_input:
        analysis = analyze_zho_subtitle_stream_script(
            infile_path,
            stream,
            cache_dir_path=tmp_path / "cache",
        )

    ffmpeg_input.assert_not_called()
    assert analysis.script == "zho-Hans"


def test_get_text_subtitle_stream_stats_from_cached_stream(tmp_path: Path):
    """Test text subtitle stream stats read cached extracted subtitles.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    _cache_subtitle_stream(
        infile_path,
        stream,
        tmp_path / "cache",
        (
            "1\n00:00:02,500 --> 00:00:04,000\n第一行\n\n"
            "2\n00:01:02,000 --> 00:01:05,250\n第二行\n"
        ),
    )

    with patch("scinoephile.media.subtitles.cache.ffmpeg.input") as ffmpeg_input:
        stats = get_subtitle_stream_stats(
            infile_path,
            stream,
            cache_dir_path=tmp_path / "cache",
        )

    ffmpeg_input.assert_not_called()
    assert stats.event_count == 2
    assert stats.first_start_ms == 2500
    assert stats.last_end_ms == 65250


def test_image_subtitle_cache_without_index_is_invalid(tmp_path: Path):
    """Test image subtitle caches without HTML index are invalid.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    image_dir_path = tmp_path / "image-series"
    image_dir_path.mkdir()

    assert not is_valid_image_subtitle_cache(image_dir_path)


def test_get_image_subtitle_stream_stats_from_cached_images(tmp_path: Path):
    """Test image subtitle stats read cached rendered images.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="hdmv_pgs_subtitle")
    _cache_image_subtitles(
        infile_path,
        stream,
        tmp_path / "cache",
        event_count=7,
        first_start_ms=2500,
        last_end_ms=65_250,
    )

    stats = get_subtitle_stream_stats(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )

    assert stats.event_count == 7
    assert stats.first_start_ms == 2500
    assert stats.last_end_ms == 65250


def test_get_image_subtitle_stream_stats_builds_image_cache(tmp_path: Path):
    """Test image subtitle stats build rendered image cache.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="hdmv_pgs_subtitle")
    _cache_subtitle_stream(infile_path, stream, tmp_path / "cache", b"not a real sup")
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
        stats = get_subtitle_stream_stats(
            infile_path,
            stream,
            cache_dir_path=tmp_path / "cache",
        )

    image_dir_path = _get_cached_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    assert stats.event_count == 1
    assert (image_dir_path / "index.html").exists()


def test_analyze_image_subtitle_stream_uses_cached_sampled_pngs(
    tmp_path: Path,
    monkeypatch,
):
    """Test image subtitle analysis OCRs sampled cached PNGs.

    Arguments:
        tmp_path: temporary directory provided by pytest
        monkeypatch: pytest monkeypatch fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="hdmv_pgs_subtitle")
    _cache_image_subtitles(
        infile_path,
        stream,
        tmp_path / "cache",
        event_count=7,
    )
    ocr_sizes: list[list[tuple[int, int]]] = []

    def fake_ocr_image_series_with_paddle(
        sampled_series: ImageSeries,
        *,
        language: str,
    ) -> Series:
        ocr_sizes.append(
            [cast(ImageSubtitle, event).img.size for event in sampled_series]
        )
        return Series(
            events=[
                Subtitle(start=event.start, end=event.end, text="繁體中文漢字")
                for event in sampled_series
            ]
        )

    monkeypatch.setattr(
        "scinoephile.image.ocr.paddle.ocr_image_series_with_paddle",
        fake_ocr_image_series_with_paddle,
    )
    analysis = analyze_zho_subtitle_stream_script(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )

    assert analysis.script == "zho-Hant"
    assert analysis.sample_indexes == (0, 2, 4, 6)
    assert ocr_sizes == [
        [(10, 8), (12, 8), (14, 8), (16, 8)],
        [(10, 8), (12, 8), (14, 8), (16, 8)],
    ]


def test_analyze_image_subtitle_stream_expands_samples_on_title_conflict(
    tmp_path: Path,
    monkeypatch,
):
    """Test image subtitle analysis expands OCR samples when title conflicts.

    Arguments:
        tmp_path: temporary directory provided by pytest
        monkeypatch: pytest monkeypatch fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(
        index=2,
        language="zho",
        codec_name="hdmv_pgs_subtitle",
        title="Chinese (Simplified)",
    )
    _cache_image_subtitles(
        infile_path,
        stream,
        tmp_path / "cache",
        event_count=16,
    )
    sample_lengths: list[int] = []

    def fake_ocr_image_series_with_paddle(
        sampled_series: ImageSeries,
        *,
        language: str,
    ) -> Series:
        sample_lengths.append(len(sampled_series))
        if len(sampled_series) == 4:
            text = "繁體中文漢字"
        else:
            text = "简体中文汉字"
        return Series(
            events=[
                Subtitle(start=event.start, end=event.end, text=text)
                for event in sampled_series
            ]
        )

    monkeypatch.setattr(
        "scinoephile.image.ocr.paddle.ocr_image_series_with_paddle",
        fake_ocr_image_series_with_paddle,
    )

    analysis = analyze_zho_subtitle_stream_script(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )

    assert analysis.script == "zho-Hans"
    assert analysis.sample_indexes == tuple(range(16))
    assert sample_lengths == [4, 4, 16, 16]


def test_analyze_image_subtitle_stream_expands_samples_when_inconclusive(
    tmp_path: Path,
    monkeypatch,
):
    """Test image subtitle analysis expands OCR samples when inconclusive.

    Arguments:
        tmp_path: temporary directory provided by pytest
        monkeypatch: pytest monkeypatch fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(
        index=2,
        language="zho",
        codec_name="hdmv_pgs_subtitle",
    )
    _cache_image_subtitles(
        infile_path,
        stream,
        tmp_path / "cache",
        event_count=16,
    )
    sample_lengths: list[int] = []

    def fake_ocr_image_series_with_paddle(
        sampled_series: ImageSeries,
        *,
        language: str,
    ) -> Series:
        sample_lengths.append(len(sampled_series))
        if len(sampled_series) == 4:
            text = "中文"
        else:
            text = "繁體中文漢字"
        return Series(
            events=[
                Subtitle(start=event.start, end=event.end, text=text)
                for event in sampled_series
            ]
        )

    monkeypatch.setattr(
        "scinoephile.image.ocr.paddle.ocr_image_series_with_paddle",
        fake_ocr_image_series_with_paddle,
    )

    analysis = analyze_zho_subtitle_stream_script(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )

    assert analysis.script == "zho-Hant"
    assert analysis.sample_indexes == tuple(range(16))
    assert sample_lengths == [4, 4, 16, 16]


def test_cache_subtitle_streams_extracts_missing_streams(tmp_path: Path, caplog):
    """Test subtitle stream cache extracts missing streams with ffmpeg.

    Arguments:
        tmp_path: temporary directory provided by pytest
        caplog: pytest log capture fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    streams = [
        SubtitleStream(index=2, language="eng", codec_name="subrip"),
        SubtitleStream(index=3, language="zho", codec_name="subrip"),
    ]

    caplog.set_level("INFO", logger="scinoephile.media.subtitles.cache")
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
    ffmpeg_input.assert_called_once_with(str(infile_path))
    output = ffmpeg_input.return_value.output
    assert output.call_count == 2
    assert output.call_args_list[0].args == (str(first_stream_path),)
    assert output.call_args_list[0].kwargs == {"map": "0:2", "c:s": "subrip"}
    assert output.call_args_list[1].args == (str(second_stream_path),)
    assert output.call_args_list[1].kwargs == {"map": "0:3", "c:s": "subrip"}
    merge_outputs.assert_called_once()
    assert len(merge_outputs.call_args.args) == 2
    merge_outputs.return_value.run.assert_called_once_with(
        quiet=False,
        overwrite_output=True,
    )
    assert first_stream_path.parent.exists()
    assert second_stream_path.parent.exists()
    messages = [record.getMessage() for record in caplog.records]
    assert f"Created cache directory: {first_stream_path.parent}" in messages
    assert f"Created cache directory: {second_stream_path.parent}" in messages


def _cache_image_subtitles(
    infile_path: Path,
    stream: SubtitleStream,
    cache_dir_path: Path,
    *,
    event_count: int,
    first_start_ms: int | None = None,
    last_end_ms: int | None = None,
) -> Path:
    """Write cached SUP data and rendered image subtitles.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to cache
        cache_dir_path: cache directory path
        event_count: number of rendered subtitle events to write
        first_start_ms: start timestamp for the first event, if overridden
        last_end_ms: end timestamp for the final event, if overridden
    Returns:
        rendered image subtitle directory path
    """
    _cache_subtitle_stream(infile_path, stream, cache_dir_path, b"not a real sup")
    image_dir_path = _get_cached_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    events: list[ImageSubtitle] = []
    for index in range(event_count):
        start = index * 10_000
        if index == 0 and first_start_ms is not None:
            start = first_start_ms
        end = index * 10_000 + 500
        if index == event_count - 1 and last_end_ms is not None:
            end = last_end_ms
        events.append(
            ImageSubtitle(
                start=start,
                end=end,
                img=Image.new("RGBA", (10 + index, 8), (255, 255, 255, 0)),
            )
        )
    ImageSeries(events=events).save(image_dir_path)
    return image_dir_path


def _cache_subtitle_stream(
    infile_path: Path,
    stream: SubtitleStream,
    cache_dir_path: Path,
    data: bytes | str,
) -> Path:
    """Write a cached extracted subtitle stream.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to cache
        cache_dir_path: cache directory path
        data: data to write to the cached stream
    Returns:
        cached subtitle stream path
    """
    stream_path = get_subtitle_cache_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    stream_path.parent.mkdir(parents=True)
    if isinstance(data, bytes):
        stream_path.write_bytes(data)
    else:
        stream_path.write_text(data, encoding="utf-8")
    return stream_path
