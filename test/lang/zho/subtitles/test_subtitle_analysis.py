#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Chinese subtitle stream script analysis."""

from __future__ import annotations

from pathlib import Path
from typing import cast
from unittest.mock import patch

from PIL import Image

from scinoephile.core import Language
from scinoephile.core.media import SubtitleStream
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from scinoephile.lang.zho.subtitles.analysis import (
    analyze_zho_subtitle_stream_script,
)
from scinoephile.media.subtitles.cache import get_subtitle_cache_path


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
        language: Language,
    ) -> Series:
        assert language in (Language.zho_hans, Language.zho_hant)
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


def _cache_image_subtitles(
    infile_path: Path,
    stream: SubtitleStream,
    cache_dir_path: Path,
    *,
    event_count: int,
) -> Path:
    """Write cached SUP data and rendered image subtitles.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to cache
        cache_dir_path: cache directory path
        event_count: number of rendered subtitle events to write
    Returns:
        rendered image subtitle directory path
    """
    _cache_subtitle_stream(infile_path, stream, cache_dir_path, b"not a real sup")
    image_dir_path = (
        get_subtitle_cache_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        ).parent
        / "image-series"
    )
    events = [
        ImageSubtitle(
            start=index * 10_000,
            end=index * 10_000 + 500,
            img=Image.new("RGBA", (10 + index, 8), (255, 255, 255, 0)),
        )
        for index in range(event_count)
    ]
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
