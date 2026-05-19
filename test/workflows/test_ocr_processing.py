#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR processing workflow."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries
from scinoephile.workflows.ocr_processing import process_eng_ocr, process_zho_ocr


def _series(text: str) -> Series:
    """Build a single-subtitle text series.

    Arguments:
        text: subtitle text
    Returns:
        text subtitle series
    """
    return Series(events=[Subtitle(start=1000, end=2000, text=text)])


def _series_with_texts(texts: list[str]) -> Series:
    """Build a text series with one subtitle per provided text.

    Arguments:
        texts: subtitle texts
    Returns:
        text subtitle series
    """
    return Series(
        events=[
            Subtitle(start=(idx * 2000) + 1000, end=(idx * 2000) + 2000, text=text)
            for idx, text in enumerate(texts)
        ]
    )


def test_process_eng_ocr_runs_lens_tesseract_and_fusion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test English OCR processing runs Lens and Tesseract before fusion.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    source_path = tmp_path / "source.sup"
    source_path.write_bytes(b"unused")
    output_dir_path = tmp_path / "output"
    loaded_paths: list[Path] = []

    def fake_load(path: Path) -> ImageSeries:
        """Fake image subtitle loading."""
        loaded_paths.append(path)
        return tiny_image_series

    def fake_lens(image_series: ImageSeries, *, language: str) -> Series:
        """Fake Google Lens OCR."""
        assert image_series is tiny_image_series
        assert language == "en"
        return _series("lens")

    def fake_tesseract(
        image_series: ImageSeries,
        *,
        language: str,
    ) -> Series:
        """Fake Tesseract OCR."""
        assert image_series is tiny_image_series
        assert language == "eng"
        return _series("tesseract")

    def fake_fuse(lens: Series, tesseract: Series, **kwargs: object) -> Series:
        """Fake English OCR fusion."""
        assert [subtitle.text for subtitle in lens] == ["lens"]
        assert [subtitle.text for subtitle in tesseract] == ["tesseract"]
        assert kwargs == {"processor": fuser}
        return _series("fused")

    fuser = object()
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ImageSeries.load", fake_load
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ocr_image_series_with_lens",
        fake_lens,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ocr_image_series_with_tesseract",
        fake_tesseract,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.get_eng_ocr_fuser",
        lambda provider, additional_context: fuser,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.get_eng_ocr_fused",
        fake_fuse,
    )

    result = process_eng_ocr(
        infile_path=source_path,
        output_dir_path=output_dir_path,
    )

    assert loaded_paths == [source_path]
    assert result.output_dir_path == output_dir_path
    assert result.output_paths == {
        "lens": output_dir_path / "lens.srt",
        "tesseract": output_dir_path / "tesseract.srt",
        "fuse": output_dir_path / "fuse.srt",
    }
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "lens.srt")
    ] == ["lens"]
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "tesseract.srt")
    ] == ["tesseract"]
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "fuse.srt")
    ] == ["fused"]


def test_process_zho_ocr_runs_lens_paddle_and_fusion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test Chinese OCR processing runs Lens and PaddleOCR before fusion.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    source_path = tmp_path / "source.sup"
    source_path.write_bytes(b"unused")
    output_dir_path = tmp_path / "output"

    def fake_lens(image_series: ImageSeries, *, language: str) -> Series:
        """Fake Google Lens OCR."""
        assert image_series is tiny_image_series
        assert language == "zh-CN"
        return _series("lens")

    def fake_paddle(image_series: ImageSeries, *, language: str) -> Series:
        """Fake PaddleOCR."""
        assert image_series is tiny_image_series
        assert language == "ch"
        return _series("paddle")

    def fake_fuse(lens: Series, paddle: Series, **kwargs: object) -> Series:
        """Fake Chinese OCR fusion."""
        assert [subtitle.text for subtitle in lens] == ["lens"]
        assert [subtitle.text for subtitle in paddle] == ["paddle"]
        assert kwargs == {"processor": fuser}
        return _series("fused")

    fuser = object()
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ImageSeries.load",
        lambda path: tiny_image_series,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ocr_image_series_with_lens",
        fake_lens,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ocr_image_series_with_paddle",
        fake_paddle,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.get_zho_ocr_fuser",
        lambda provider, additional_context: fuser,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.get_zho_ocr_fused",
        fake_fuse,
    )

    result = process_zho_ocr(
        infile_path=source_path,
        output_dir_path=output_dir_path,
    )

    assert result.output_paths == {
        "lens": output_dir_path / "lens.srt",
        "paddle": output_dir_path / "paddle.srt",
        "fuse": output_dir_path / "fuse.srt",
    }
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "lens.srt")
    ] == ["lens"]
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "paddle.srt")
    ] == ["paddle"]
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "fuse.srt")
    ] == ["fused"]


def test_process_zho_ocr_passes_traditional_languages_to_ocr_engines(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test Chinese OCR processing maps traditional script to OCR language codes.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    source_path = tmp_path / "source.sup"
    source_path.write_bytes(b"unused")
    output_dir_path = tmp_path / "output"
    fuser = object()

    def fake_lens(image_series: ImageSeries, *, language: str) -> Series:
        """Fake Google Lens OCR."""
        assert image_series is tiny_image_series
        assert language == "zh-TW"
        return _series("lens")

    def fake_paddle(image_series: ImageSeries, *, language: str) -> Series:
        """Fake PaddleOCR."""
        assert image_series is tiny_image_series
        assert language == "chinese_cht"
        return _series("paddle")

    def fake_fuse(lens: Series, paddle: Series, **kwargs: object) -> Series:
        """Fake Chinese OCR fusion."""
        assert kwargs == {"processor": fuser}
        return _series("fused")

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ImageSeries.load",
        lambda path: tiny_image_series,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ocr_image_series_with_lens",
        fake_lens,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ocr_image_series_with_paddle",
        fake_paddle,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.get_zho_ocr_fuser",
        lambda provider, additional_context: fuser,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.get_zho_ocr_fused",
        fake_fuse,
    )

    process_zho_ocr(
        infile_path=source_path,
        output_dir_path=output_dir_path,
        script="traditional",
    )


def test_process_eng_ocr_can_export_source_image_series(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test OCR processing can export source image subtitles.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    source_path = tmp_path / "source.sup"
    source_path.write_bytes(b"unused")
    output_dir_path = tmp_path / "output"

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ImageSeries.load",
        lambda path: tiny_image_series,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ocr_image_series_with_lens",
        lambda image_series, *, language: _series_with_texts(
            ["lens text", "lens text 2"]
        ),
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ocr_image_series_with_tesseract",
        lambda image_series, *, language: _series_with_texts(
            ["tesseract text", "tesseract text 2"]
        ),
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.get_eng_ocr_fuser",
        lambda provider, additional_context: object(),
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.get_eng_ocr_fused",
        lambda lens, tesseract, **kwargs: _series_with_texts(
            ["fused text", "fused text 2"]
        ),
    )

    result = process_eng_ocr(
        infile_path=source_path,
        output_dir_path=output_dir_path,
        export_images=True,
    )

    assert result.output_paths["image"] == output_dir_path / "image"
    assert "recognized" in (output_dir_path / "image/index.html").read_text(
        encoding="utf-8"
    )


def test_process_eng_ocr_media_input_loads_selected_subtitle_stream(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test media OCR processing loads the selected cached subtitle stream.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    source_path = tmp_path / "movie.mkv"
    source_path.write_bytes(b"unused")
    cached_sup_path = tmp_path / "cache" / "5.sup"
    output_dir_path = tmp_path / "output"
    stream = SubtitleStream(index=5, codec_name="hdmv_pgs_subtitle")
    cache_calls: list[tuple[Path, list[SubtitleStream], Path | None]] = []
    loaded_paths: list[Path] = []

    def fake_cache_subtitles(
        infile_path: Path,
        streams: list[SubtitleStream],
        *,
        cache_dir_path: Path | None = None,
    ):
        """Fake media subtitle caching."""
        cache_calls.append((infile_path, streams, cache_dir_path))

    def fake_load(path: Path) -> ImageSeries:
        """Fake image subtitle loading."""
        loaded_paths.append(path)
        return tiny_image_series

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.get_subtitle_streams",
        lambda path: [stream],
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.cache_subtitles",
        fake_cache_subtitles,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.get_subtitle_cache_path",
        lambda infile_path, selected_stream, cache_dir_path=None: cached_sup_path,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ImageSeries.load",
        fake_load,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ocr_image_series_with_lens",
        lambda image_series, *, language: _series("lens"),
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ocr_image_series_with_tesseract",
        lambda image_series, *, language: _series("tesseract"),
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.get_eng_ocr_fuser",
        lambda provider, additional_context: object(),
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.get_eng_ocr_fused",
        lambda lens, tesseract, **kwargs: _series("fused"),
    )

    process_eng_ocr(
        infile_path=source_path,
        output_dir_path=output_dir_path,
        stream_index=5,
    )

    assert cache_calls == [(source_path, [stream], None)]
    assert loaded_paths == [cached_sup_path]


def test_process_eng_ocr_media_input_requires_matching_stream_index(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test media OCR processing rejects missing subtitle stream indexes.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    source_path = tmp_path / "movie.mkv"
    source_path.write_bytes(b"unused")
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.get_subtitle_streams",
        lambda path: [SubtitleStream(index=5, codec_name="hdmv_pgs_subtitle")],
    )

    with pytest.raises(ScinoephileError, match="No subtitle stream 7"):
        process_eng_ocr(
            infile_path=source_path,
            output_dir_path=tmp_path / "output",
            stream_index=7,
        )
