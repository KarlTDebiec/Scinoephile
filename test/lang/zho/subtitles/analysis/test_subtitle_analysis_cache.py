#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Chinese subtitle script analysis caching."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core.media import SubtitleStream
from scinoephile.lang.zho.subtitles.analysis.cache import (
    ZhoSubtitleScriptAnalysisCache,
)
from scinoephile.lang.zho.subtitles.analysis.result import (
    ZhoSubtitleScriptAnalysis,
)


def test_subtitle_script_analysis_cache_round_trip(tmp_path: Path):
    """Test script analysis results round-trip through their cache.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    analysis = ZhoSubtitleScriptAnalysis(
        script="zho-Hant",
        traditional_count=4,
        shared_count=2,
    )
    cache = ZhoSubtitleScriptAnalysisCache(tmp_path / "cache")

    cache_path = cache.save(
        infile_path,
        stream,
        4,
        ("zho-Hans", "zho-Hant"),
        analysis,
    )

    assert cache_path.parent == tmp_path / "cache/media/subtitles/analysis"
    assert (
        cache.load(
            infile_path,
            stream,
            4,
            ("zho-Hans", "zho-Hant"),
        )
        == analysis
    )


def test_subtitle_script_analysis_cache_discards_invalid_entry(tmp_path: Path):
    """Test invalid script analysis cache entries are discarded.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache = ZhoSubtitleScriptAnalysisCache(tmp_path / "cache")
    cache_path = cache.get_path(
        infile_path,
        stream,
        4,
        ("zho-Hans", "zho-Hant"),
    )
    cache_path.write_text("{", encoding="utf-8")

    assert (
        cache.load(
            infile_path,
            stream,
            4,
            ("zho-Hans", "zho-Hant"),
        )
        is None
    )
    assert not cache_path.exists()


def test_subtitle_script_analysis_cache_overwrite_removes_entry(tmp_path: Path):
    """Test cache overwrite converts a matching entry into a cache miss.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache_root_path = tmp_path / "cache"
    cache = ZhoSubtitleScriptAnalysisCache(cache_root_path)
    cache_path = cache.save(
        infile_path,
        stream,
        4,
        ("zho-Hans", "zho-Hant"),
        ZhoSubtitleScriptAnalysis(script="zho-Hant"),
    )

    overwrite_cache = ZhoSubtitleScriptAnalysisCache(cache_root_path, overwrite=True)

    assert (
        overwrite_cache.load(
            infile_path,
            stream,
            4,
            ("zho-Hans", "zho-Hant"),
        )
        is None
    )
    assert not cache_path.exists()
