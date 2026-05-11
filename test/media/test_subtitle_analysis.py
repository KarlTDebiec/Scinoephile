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
from scinoephile.media.subtitle_analysis import (
    analyze_subtitle_stream_script,
    cache_subtitle_stream_artifacts,
    count_subtitle_stream_events,
    get_cached_image_subtitle_dir_path,
    get_cached_subtitle_artifact_path,
    get_subtitle_stream_stats,
)


def test_subtitle_stream_uses_language_for_description_and_filename():
    """Test subtitle stream output uses its language tag."""
    stream = SubtitleStream(
        index=2,
        language="zho-Hant",
        codec_name="subrip",
    )

    assert stream.description == "Stream #0:2(zho-Hant): Subtitle: subrip"
    assert stream.outfile_filename == "zho-Hant-2.srt"


def test_get_cached_subtitle_artifact_path_changes_by_stream(tmp_path: Path):
    """Test subtitle artifact cache paths include stream identity.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")

    first = get_cached_subtitle_artifact_path(
        infile_path,
        SubtitleStream(index=2, language="zho", codec_name="subrip"),
        cache_dir_path=tmp_path / "cache",
    )
    second = get_cached_subtitle_artifact_path(
        infile_path,
        SubtitleStream(index=3, language="zho", codec_name="subrip"),
        cache_dir_path=tmp_path / "cache",
    )

    assert first != second
    assert first.suffix == ".srt"
    assert second.suffix == ".srt"


def test_get_cached_subtitle_artifact_path_ignores_script_analysis_version(
    tmp_path: Path,
    monkeypatch,
):
    """Test subtitle artifact cache paths are independent of OCR versioning.

    Arguments:
        tmp_path: temporary directory provided by pytest
        monkeypatch: pytest monkeypatch fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    cache_dir_path = tmp_path / "cache"

    original = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.media.subtitle_analysis.cache_keys.SCRIPT_ANALYSIS_CACHE_VERSION",
        999,
    )
    changed = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )

    assert changed == original


def test_cache_subtitle_stream_artifacts_reextracts_empty_artifact(tmp_path: Path):
    """Test empty cached subtitle artifacts are re-extracted.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_bytes(b"")

    with patch(
        "scinoephile.media.subtitle_analysis.artifacts.run_command"
    ) as run_command:
        cache_subtitle_stream_artifacts(
            infile_path,
            [stream],
            cache_dir_path=tmp_path / "cache",
        )

    run_command.assert_called_once()


def test_analyze_text_subtitle_stream_uses_cached_artifact(tmp_path: Path):
    """Test text subtitle stream analysis reads cached extracted subtitles.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\n简体中文汉字\n",
        encoding="utf-8",
    )

    with patch(
        "scinoephile.media.subtitle_analysis.artifacts.run_command"
    ) as run_command:
        analysis = analyze_subtitle_stream_script(
            infile_path,
            stream,
            cache_dir_path=tmp_path / "cache",
        )

    run_command.assert_not_called()
    assert analysis.script == "zho-Hans"


def test_count_text_subtitle_stream_events_from_cached_artifact(tmp_path: Path):
    """Test text subtitle event counting reads cached extracted subtitles.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(
        (
            "1\n00:00:00,000 --> 00:00:01,000\n第一行\n\n"
            "2\n00:00:02,000 --> 00:00:03,000\n第二行\n"
        ),
        encoding="utf-8",
    )

    with patch(
        "scinoephile.media.subtitle_analysis.artifacts.run_command"
    ) as run_command:
        count = count_subtitle_stream_events(
            infile_path,
            stream,
            cache_dir_path=tmp_path / "cache",
        )

    run_command.assert_not_called()
    assert count == 2


def test_get_text_subtitle_stream_stats_from_cached_artifact(tmp_path: Path):
    """Test text subtitle stream stats read cached extracted subtitles.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(
        (
            "1\n00:00:02,500 --> 00:00:04,000\n第一行\n\n"
            "2\n00:01:02,000 --> 00:01:05,250\n第二行\n"
        ),
        encoding="utf-8",
    )

    with patch(
        "scinoephile.media.subtitle_analysis.artifacts.run_command"
    ) as run_command:
        stats = get_subtitle_stream_stats(
            infile_path,
            stream,
            cache_dir_path=tmp_path / "cache",
        )

    run_command.assert_not_called()
    assert stats.event_count == 2
    assert stats.first_start_ms == 2500
    assert stats.last_end_ms == 65250


def test_count_image_subtitle_stream_events_from_cached_manifest(tmp_path: Path):
    """Test image subtitle event counting reads cached image metadata.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="hdmv_pgs_subtitle")
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_bytes(b"not a real sup")
    image_dir_path = get_cached_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    image_dir_path.mkdir()
    (image_dir_path / "index.html").write_text("", encoding="utf-8")
    (image_dir_path / "manifest.json").write_text(
        '{"event_count": 7, "image_count": 7, "version": 1}',
        encoding="utf-8",
    )

    with patch(
        "scinoephile.media.subtitle_analysis.image_cache.ImageSeries.load"
    ) as load_image_series:
        count = count_subtitle_stream_events(
            infile_path,
            stream,
            cache_dir_path=tmp_path / "cache",
        )

    load_image_series.assert_not_called()
    assert count == 7


def test_get_image_subtitle_stream_stats_from_cached_manifest(tmp_path: Path):
    """Test image subtitle stats read cached image metadata.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="hdmv_pgs_subtitle")
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_bytes(b"not a real sup")
    image_dir_path = get_cached_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    image_dir_path.mkdir()
    (image_dir_path / "index.html").write_text("", encoding="utf-8")
    (image_dir_path / "manifest.json").write_text(
        (
            '{"event_count": 7, "first_start_ms": 2500, "image_count": 7, '
            '"last_end_ms": 65250, "version": 1}'
        ),
        encoding="utf-8",
    )

    with patch(
        "scinoephile.media.subtitle_analysis.image_cache.ImageSeries.load"
    ) as load_image_series:
        stats = get_subtitle_stream_stats(
            infile_path,
            stream,
            cache_dir_path=tmp_path / "cache",
        )

    load_image_series.assert_not_called()
    assert stats.event_count == 7
    assert stats.first_start_ms == 2500
    assert stats.last_end_ms == 65250


def test_count_image_subtitle_stream_events_builds_image_cache(tmp_path: Path):
    """Test image subtitle event counting builds rendered image cache.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="hdmv_pgs_subtitle")
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_bytes(b"not a real sup")
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
        "scinoephile.media.subtitle_analysis.image_cache.ImageSeries.load",
        return_value=image_series,
    ):
        count = count_subtitle_stream_events(
            infile_path,
            stream,
            cache_dir_path=tmp_path / "cache",
        )

    image_dir_path = get_cached_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    assert count == 1
    assert (image_dir_path / "index.html").exists()
    assert (image_dir_path / "manifest.json").exists()


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
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_bytes(b"not a real sup")
    image_dir_path = get_cached_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    image_series = ImageSeries(
        events=[
            ImageSubtitle(
                start=index * 1000,
                end=index * 1000 + 500,
                img=Image.new("RGBA", (10 + index, 8), (255, 255, 255, 0)),
            )
            for index in range(7)
        ]
    )
    image_series.save(image_dir_path)
    (image_dir_path / "manifest.json").write_text(
        '{"event_count": 7, "image_count": 7, "version": 1}',
        encoding="utf-8",
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
    with patch(
        "scinoephile.media.subtitle_analysis.image_cache.ImageSeries.load"
    ) as load_image_series:
        analysis = analyze_subtitle_stream_script(
            infile_path,
            stream,
            cache_dir_path=tmp_path / "cache",
        )

    load_image_series.assert_not_called()
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
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_bytes(b"not a real sup")
    image_dir_path = get_cached_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    image_series = ImageSeries(
        events=[
            ImageSubtitle(
                start=index * 1000,
                end=index * 1000 + 500,
                img=Image.new("RGBA", (10 + index, 8), (255, 255, 255, 0)),
            )
            for index in range(16)
        ]
    )
    image_series.save(image_dir_path)
    (image_dir_path / "manifest.json").write_text(
        '{"event_count": 16, "image_count": 16, "version": 1}',
        encoding="utf-8",
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

    analysis = analyze_subtitle_stream_script(
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
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_bytes(b"not a real sup")
    image_dir_path = get_cached_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    image_series = ImageSeries(
        events=[
            ImageSubtitle(
                start=index * 1000,
                end=index * 1000 + 500,
                img=Image.new("RGBA", (10 + index, 8), (255, 255, 255, 0)),
            )
            for index in range(16)
        ]
    )
    image_series.save(image_dir_path)
    (image_dir_path / "manifest.json").write_text(
        '{"event_count": 16, "image_count": 16, "version": 1}',
        encoding="utf-8",
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

    analysis = analyze_subtitle_stream_script(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )

    assert analysis.script == "zho-Hant"
    assert analysis.sample_indexes == tuple(range(16))
    assert sample_lengths == [4, 4, 16, 16]


def test_subtitle_cache_logs_hits_and_analysis_loads(
    tmp_path: Path,
    caplog,
):
    """Test subtitle artifact and analysis cache hits are logged.

    Arguments:
        tmp_path: temporary directory provided by pytest
        caplog: pytest log capture fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    stream = SubtitleStream(index=2, language="zho", codec_name="subrip")
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\n简体中文汉字\n",
        encoding="utf-8",
    )

    caplog.set_level("INFO")
    cache_subtitle_stream_artifacts(
        infile_path,
        [stream],
        cache_dir_path=tmp_path / "cache",
    )
    analyze_subtitle_stream_script(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    analyze_subtitle_stream_script(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )

    messages = [record.getMessage() for record in caplog.records]
    assert f"Loaded subtitle artifact from cache: {artifact_path}" in messages
    assert any(
        message.startswith("Saved subtitle script analysis to cache: ")
        for message in messages
    )
    assert any(
        message.startswith("Loaded subtitle script analysis from cache: ")
        for message in messages
    )


def test_cache_subtitle_stream_artifacts_extracts_missing_streams_together(
    tmp_path: Path,
):
    """Test subtitle artifact cache extracts missing streams in one ffmpeg command.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.write_bytes(b"video")
    streams = [
        SubtitleStream(index=2, language="eng", codec_name="subrip"),
        SubtitleStream(index=3, language="zho", codec_name="subrip"),
    ]

    with patch(
        "scinoephile.media.subtitle_analysis.artifacts.run_command"
    ) as run_command:
        cache_subtitle_stream_artifacts(
            infile_path,
            streams,
            cache_dir_path=tmp_path / "cache",
        )

    run_command.assert_called_once()
    command = run_command.call_args.args[0]
    assert command[:4] == ["ffmpeg", "-y", "-i", str(infile_path)]
    assert command.count("-map") == 2
    assert "0:2" in command
    assert "0:3" in command
    assert (
        str(
            get_cached_subtitle_artifact_path(
                infile_path,
                streams[0],
                cache_dir_path=tmp_path / "cache",
            )
        )
        not in command
    )
    assert (
        str(
            get_cached_subtitle_artifact_path(
                infile_path,
                streams[1],
                cache_dir_path=tmp_path / "cache",
            )
        )
        not in command
    )
