#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Chinese subtitle script analysis caching."""

from __future__ import annotations

import json
from pathlib import Path

from scinoephile.core.media import SubtitleStream
from scinoephile.lang.zho.subtitles.analysis.cache import ZhoScriptAnalysisCache
from scinoephile.lang.zho.subtitles.analysis.result import ZhoScriptAnalysisResult


def test_subtitle_script_analysis_cache_uses_runtime_default(
    runtime_cache_root_path: Path,
):
    """Test a missing configured root selects the runtime cache root.

    Arguments:
        runtime_cache_root_path: isolated default runtime cache root
    """
    cache = ZhoScriptAnalysisCache()

    assert cache.cache_root_path == runtime_cache_root_path
    assert cache.cache_dir_path == (
        runtime_cache_root_path / "media" / "subtitles" / "analysis"
    )


def test_subtitle_script_analysis_cache_round_trip(tmp_path: Path):
    """Test script analysis results round-trip through their cache.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    analysis = ZhoScriptAnalysisResult(
        script="zho-Hant", traditional_count=4, shared_count=2
    )
    cache = ZhoScriptAnalysisCache(tmp_path / "cache")

    cache_path = cache.save(infile_path, stream, 4, ("zho-Hans", "zho-Hant"), analysis)

    assert cache_path.parent == tmp_path / "cache/media/subtitles/analysis"
    assert cache.load(infile_path, stream, 4, ("zho-Hans", "zho-Hant")) == analysis
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    assert payload["cache_version"] == 1
    assert payload["analysis"]["script"] == "zho-Hant"


def test_subtitle_script_analysis_cache_discards_invalid_entry(tmp_path: Path):
    """Test invalid script analysis cache entries are discarded.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache = ZhoScriptAnalysisCache(tmp_path / "cache")
    cache_path = cache.get_path(infile_path, stream, 4, ("zho-Hans", "zho-Hant"))
    cache_path.write_text("{", encoding="utf-8")

    assert cache.load(infile_path, stream, 4, ("zho-Hans", "zho-Hant")) is None
    assert not cache_path.exists()


def test_subtitle_script_analysis_cache_discards_mismatched_version(tmp_path: Path):
    """Test script analysis cache version mismatches are discarded."""
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache = ZhoScriptAnalysisCache(tmp_path / "cache")
    cache_path = cache.save(
        infile_path,
        stream,
        4,
        ("zho-Hans", "zho-Hant"),
        ZhoScriptAnalysisResult(script="zho-Hant"),
    )
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    payload["cache_version"] = 0
    cache_path.write_text(json.dumps(payload), encoding="utf-8")

    assert cache.load(infile_path, stream, 4, ("zho-Hans", "zho-Hant")) is None
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
    cache = ZhoScriptAnalysisCache(cache_root_path)
    cache_path = cache.save(
        infile_path,
        stream,
        4,
        ("zho-Hans", "zho-Hant"),
        ZhoScriptAnalysisResult(script="zho-Hant"),
    )

    overwrite_cache = ZhoScriptAnalysisCache(cache_root_path, overwrite=True)

    assert (
        overwrite_cache.load(infile_path, stream, 4, ("zho-Hans", "zho-Hant")) is None
    )
    assert not cache_path.exists()


def test_subtitle_script_analysis_cache_overwrites_entry_once(tmp_path: Path):
    """Test overwrite refreshes a matching analysis once per instance."""
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache_root_path = tmp_path / "cache"
    languages = ("zho-Hans", "zho-Hant")
    ZhoScriptAnalysisCache(cache_root_path).save(
        infile_path, stream, 4, languages, ZhoScriptAnalysisResult(script="zho-Hant")
    )
    overwrite_cache = ZhoScriptAnalysisCache(cache_root_path, True)

    assert overwrite_cache.load(infile_path, stream, 4, languages) is None
    overwrite_cache.save(
        infile_path, stream, 4, languages, ZhoScriptAnalysisResult(script="zho-Hans")
    )

    assert overwrite_cache.load(infile_path, stream, 4, languages) == (
        ZhoScriptAnalysisResult(script="zho-Hans")
    )
