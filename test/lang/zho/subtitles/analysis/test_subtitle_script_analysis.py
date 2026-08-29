#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Chinese subtitle stream script analysis."""

from __future__ import annotations

from pathlib import Path
from time import time
from typing import cast
from unittest.mock import patch

from scinoephile.core import Language
from scinoephile.core.media import SubtitleStream
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from scinoephile.lang.zho.subtitles.analysis.script import (
    analyze_zho_subtitle_stream_script,
)
from scinoephile.media.subtitles.cache import SubtitleCache
from test.helpers.files import set_mtime
from test.helpers.media_subtitles import cache_image_subtitles, cache_subtitle_stream


def test_analyze_text_subtitle_stream_uses_cached_stream(tmp_path: Path):
    """Test text subtitle stream analysis reads cached extracted subtitles.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache_root_path = tmp_path / "cache"
    cache_subtitle_stream(
        infile_path,
        stream,
        cache_root_path,
        "1\n00:00:00,000 --> 00:00:01,000\n简体中文汉字\n",
    )
    subtitle_cache = SubtitleCache(cache_root_path)

    with patch("scinoephile.media.subtitles.extractor.ffmpeg.input") as ffmpeg_input:
        analysis = analyze_zho_subtitle_stream_script(
            infile_path, stream, subtitle_cache=subtitle_cache
        )

    ffmpeg_input.assert_not_called()
    assert analysis.script == "zho-Hans"


def test_analyze_text_subtitle_stream_marks_cached_analysis_used(tmp_path: Path):
    """Test a subtitle-analysis cache hit refreshes its pruning timestamp.

    Arguments:
        tmp_path: temporary directory path
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache_root_path = tmp_path / "cache"
    cache_subtitle_stream(
        infile_path,
        stream,
        cache_root_path,
        "1\n00:00:00,000 --> 00:00:01,000\n简体中文汉字\n",
    )
    subtitle_cache = SubtitleCache(cache_root_path)
    analyze_zho_subtitle_stream_script(
        infile_path, stream, subtitle_cache=subtitle_cache
    )
    cache_path = next(
        (cache_root_path / "lang" / "zho" / "subtitles" / "analysis").glob("*.json")
    )
    old_timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(cache_path, old_timestamp)

    with patch(
        "scinoephile.lang.zho.subtitles.analysis.script.SubtitleExtractor.extract"
    ) as extract:
        analysis = analyze_zho_subtitle_stream_script(
            infile_path, stream, subtitle_cache=subtitle_cache
        )

    extract.assert_not_called()
    assert analysis.script == "zho-Hans"
    assert cache_path.stat().st_mtime > old_timestamp


def test_analyze_text_subtitle_stream_regenerates_invalid_analysis_cache(
    tmp_path: Path,
):
    """Test invalid subtitle-analysis cache data is treated as a miss.

    Arguments:
        tmp_path: temporary directory path
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache_root_path = tmp_path / "cache"
    cache_subtitle_stream(
        infile_path,
        stream,
        cache_root_path,
        "1\n00:00:00,000 --> 00:00:01,000\n简体中文汉字\n",
    )
    subtitle_cache = SubtitleCache(cache_root_path)
    analyze_zho_subtitle_stream_script(
        infile_path, stream, subtitle_cache=subtitle_cache
    )
    cache_path = next(
        (cache_root_path / "lang" / "zho" / "subtitles" / "analysis").glob("*.json")
    )
    cache_path.write_text("{", encoding="utf-8")

    analysis = analyze_zho_subtitle_stream_script(
        infile_path, stream, subtitle_cache=subtitle_cache
    )

    assert analysis.script == "zho-Hans"


def test_analyze_text_subtitle_stream_overwrites_cached_stream(tmp_path: Path):
    """Test cache overwrite is forwarded to subtitle extraction.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache_root_path = tmp_path / "cache"
    cache_subtitle_stream(
        infile_path,
        stream,
        cache_root_path,
        "1\n00:00:00,000 --> 00:00:01,000\n简体中文汉字\n",
    )
    subtitle_cache = SubtitleCache(cache_root_path, overwrite=True)
    stream_path = subtitle_cache.get_path(infile_path, stream)

    with patch(
        "scinoephile.lang.zho.subtitles.analysis.script.SubtitleExtractor.extract",
        return_value=[stream_path],
    ) as extract:
        analysis = analyze_zho_subtitle_stream_script(
            infile_path, stream, subtitle_cache=subtitle_cache
        )

    extract.assert_called_once_with(infile_path, [stream])
    assert analysis.script == "zho-Hans"


def test_analyze_image_subtitle_stream_uses_cached_sampled_pngs(
    tmp_path: Path, monkeypatch
):
    """Test image subtitle analysis OCRs sampled cached PNGs.

    Arguments:
        tmp_path: temporary directory provided by pytest
        monkeypatch: pytest monkeypatch fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="hdmv_pgs_subtitle")
    cache_root_path = tmp_path / "cache"
    cache_image_subtitles(infile_path, stream, cache_root_path, event_count=7)
    subtitle_cache = SubtitleCache(cache_root_path)
    ocr_sizes: list[list[tuple[int, int]]] = []

    def fake_ocr_image_series_with_paddle(
        sampled_series: ImageSeries,
        *,
        cache_root_path: Path | None,
        language: Language,
        overwrite_cache: bool,
    ) -> Series:
        """Return a fake PaddleOCR subtitle series.

        Arguments:
            sampled_series: sampled series
            cache_root_path: cache root path
            language: language
            overwrite_cache: overwrite cache
        Returns:
            fake OCR subtitle series
        """
        assert cache_root_path == tmp_path / "cache"
        assert language in (Language.zho_hans, Language.zho_hant)
        assert overwrite_cache is False
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
        infile_path, stream, subtitle_cache=subtitle_cache
    )

    assert analysis.script == "zho-Hant"
    assert analysis.sample_indexes == (0, 2, 4, 6)
    assert ocr_sizes == [
        [(10, 8), (12, 8), (14, 8), (16, 8)],
        [(10, 8), (12, 8), (14, 8), (16, 8)],
    ]
