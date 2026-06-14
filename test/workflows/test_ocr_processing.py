#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR processing workflow."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.zho.ocr_fusion import OcrFusionPromptZhoHant
from scinoephile.web.ocr_validation.html_index import load_html_entries
from scinoephile.workflows.ocr_processing import (
    OcrProcessingResult,
    OcrProcessingWorkflow,
)


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


def process_eng_ocr(
    infile_path: Path,
    output_dir_path: Path,
    **kwargs: Any,
) -> OcrProcessingResult:
    """Run English OCR processing workflow for tests.

    Arguments:
        infile_path: OCR image subtitle input path
        output_dir_path: OCR processing output directory path
        kwargs: additional OCR processing workflow arguments
    Returns:
        OCR processing result
    """
    return OcrProcessingWorkflow(
        infile_path,
        output_dir_path,
        language="eng",
        **kwargs,
    )()


def process_zho_ocr(
    infile_path: Path,
    output_dir_path: Path,
    *,
    language: str = "zho-Hans",
    **kwargs: Any,
) -> OcrProcessingResult:
    """Run Chinese OCR processing workflow for tests.

    Arguments:
        infile_path: OCR image subtitle input path
        output_dir_path: OCR processing output directory path
        language: Chinese OCR processing language
        kwargs: additional OCR processing workflow arguments
    Returns:
        OCR processing result
    """
    return OcrProcessingWorkflow(
        infile_path,
        output_dir_path,
        language=language,
        **kwargs,
    )()


class _PatchedEngOcrPipeline:
    """Recording fake for the English OCR workflow dependencies."""

    def __init__(
        self,
        monkeypatch: pytest.MonkeyPatch,
        image_series: ImageSeries,
        *,
        lens_texts: list[str] | None = None,
        tesseract_texts: list[str] | None = None,
        fused_texts: list[str] | None = None,
    ):
        """Initialize and patch English OCR workflow dependencies.

        Arguments:
            monkeypatch: pytest monkeypatch fixture
            image_series: image subtitle series returned by fake loading
            lens_texts: texts returned by fake Google Lens OCR
            tesseract_texts: texts returned by fake Tesseract OCR
            fused_texts: texts returned by fake OCR fusion
        """
        self.image_series = image_series
        self.lens_texts = lens_texts or ["lens"]
        self.tesseract_texts = tesseract_texts or ["tesseract"]
        self.fused_texts = fused_texts or ["fused"]
        self.fuser = object()
        self.loaded_paths: list[Path] = []
        self.lens_calls: list[Language] = []
        self.tesseract_calls: list[Language] = []
        self.fuser_calls: list[dict[str, object]] = []
        self.fusion_calls: list[tuple[list[str], list[str], object]] = []

        monkeypatch.setattr(
            "scinoephile.workflows.ocr_processing.ImageSeries.load",
            self.load,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.ocr_processing.ocr_image_series_with_lens",
            self.ocr_with_lens,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.ocr_processing.ocr_image_series_with_tesseract",
            self.ocr_with_tesseract,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.ocr_processing.get_eng_ocr_fuser",
            self.get_fuser,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.ocr_processing.get_eng_ocr_fused",
            self.fuse,
        )

    def fuse(self, lens: Series, tesseract: Series, processor: object) -> Series:
        """Fake English OCR fusion."""
        lens_texts = [subtitle.text for subtitle in lens]
        tesseract_texts = [subtitle.text for subtitle in tesseract]
        self.fusion_calls.append((lens_texts, tesseract_texts, processor))
        return _series_with_texts(self.fused_texts)

    def get_fuser(self, provider: object, additional_context: str | None) -> object:
        """Return a fixed fake fuser."""
        self.fuser_calls.append(
            {
                "provider": provider,
                "additional_context": additional_context,
            }
        )
        return self.fuser

    def load(self, path: Path) -> ImageSeries:
        """Fake image subtitle loading."""
        self.loaded_paths.append(path)
        return self.image_series

    def ocr_with_lens(self, image_series: ImageSeries, *, language: Language) -> Series:
        """Fake Google Lens OCR."""
        assert image_series is self.image_series
        self.lens_calls.append(language)
        return _series_with_texts(self.lens_texts)

    def ocr_with_tesseract(
        self,
        image_series: ImageSeries,
        *,
        language: Language,
    ) -> Series:
        """Fake Tesseract OCR."""
        assert image_series is self.image_series
        self.tesseract_calls.append(language)
        return _series_with_texts(self.tesseract_texts)


class _PatchedZhoOcrPipeline:
    """Recording fake for the Chinese OCR workflow dependencies."""

    def __init__(
        self,
        monkeypatch: pytest.MonkeyPatch,
        image_series: ImageSeries,
        *,
        lens_texts: list[str] | None = None,
        paddle_texts: list[str] | None = None,
        fused_texts: list[str] | None = None,
    ):
        """Initialize and patch Chinese OCR workflow dependencies.

        Arguments:
            monkeypatch: pytest monkeypatch fixture
            image_series: image subtitle series returned by fake loading
            lens_texts: texts returned by fake Google Lens OCR
            paddle_texts: texts returned by fake PaddleOCR
            fused_texts: texts returned by fake OCR fusion
        """
        self.image_series = image_series
        self.lens_texts = lens_texts or ["lens"]
        self.paddle_texts = paddle_texts or ["paddle"]
        self.fused_texts = fused_texts or ["fused"]
        self.fuser = object()
        self.loaded_paths: list[Path] = []
        self.lens_calls: list[Language] = []
        self.paddle_calls: list[Language] = []
        self.fuser_calls: list[dict[str, object]] = []
        self.fusion_calls: list[tuple[list[str], list[str], object]] = []

        monkeypatch.setattr(
            "scinoephile.workflows.ocr_processing.ImageSeries.load",
            self.load,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.ocr_processing.ocr_image_series_with_lens",
            self.ocr_with_lens,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.ocr_processing.ocr_image_series_with_paddle",
            self.ocr_with_paddle,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.ocr_processing.get_zho_ocr_fuser",
            self.get_fuser,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.ocr_processing.get_zho_ocr_fused",
            self.fuse,
        )

    def fuse(self, lens: Series, paddle: Series, processor: object) -> Series:
        """Fake Chinese OCR fusion."""
        lens_texts = [subtitle.text for subtitle in lens]
        paddle_texts = [subtitle.text for subtitle in paddle]
        self.fusion_calls.append((lens_texts, paddle_texts, processor))
        return _series_with_texts(self.fused_texts)

    def get_fuser(self, **kwargs: object) -> object:
        """Return a fixed fake fuser."""
        self.fuser_calls.append(kwargs)
        return self.fuser

    def load(self, path: Path) -> ImageSeries:
        """Fake image subtitle loading."""
        self.loaded_paths.append(path)
        return self.image_series

    def ocr_with_lens(self, image_series: ImageSeries, *, language: Language) -> Series:
        """Fake Google Lens OCR."""
        assert image_series is self.image_series
        self.lens_calls.append(language)
        return _series_with_texts(self.lens_texts)

    def ocr_with_paddle(
        self,
        image_series: ImageSeries,
        *,
        language: Language,
    ) -> Series:
        """Fake PaddleOCR."""
        assert image_series is self.image_series
        self.paddle_calls.append(language)
        return _series_with_texts(self.paddle_texts)


def test_ocr_processing_workflow_is_callable(
    tmp_path: Path,
):
    """Test OCR processing workflow exposes a callable class API.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    source_path = tmp_path / "source.sup"
    output_dir_path = tmp_path / "output"

    workflow = OcrProcessingWorkflow(
        source_path,
        output_dir_path,
        language="eng",
        validate=False,
    )

    assert callable(workflow)
    assert workflow.language is Language.eng


def test_ocr_processing_workflow_accepts_language_object(tmp_path: Path):
    """Test OCR processing workflow accepts a core language object.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    workflow = OcrProcessingWorkflow(
        tmp_path / "source.sup",
        tmp_path / "output",
        language=Language.zho_hans,
        validate=False,
    )

    assert workflow.language is Language.zho_hans


def test_ocr_processing_workflow_rejects_invalid_language_in_init(tmp_path: Path):
    """Test OCR processing workflow rejects invalid languages during initialization.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    invalid_language: Any = "spa"

    with pytest.raises(
        ScinoephileError,
        match=(
            "language must be eng, yue-Hans, yue-Hant, zho-Hans, or zho-Hant, not spa"
        ),
    ):
        OcrProcessingWorkflow(
            tmp_path / "source.sup",
            tmp_path / "output",
            language=invalid_language,
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
    pipeline = _PatchedEngOcrPipeline(monkeypatch, tiny_image_series)

    result = process_eng_ocr(source_path, output_dir_path, validate=False)

    assert pipeline.loaded_paths == [source_path]
    assert pipeline.lens_calls == [Language.eng]
    assert pipeline.tesseract_calls == [Language.eng]
    assert pipeline.fusion_calls == [(["lens"], ["tesseract"], pipeline.fuser)]
    assert result.output_dir_path == output_dir_path
    assert result.output_paths == {
        "image": output_dir_path / "image",
        "lens": output_dir_path / "lens.srt",
        "tesseract": output_dir_path / "tesseract.srt",
        "fuse": output_dir_path / "fuse.srt",
        "fuse_clean": output_dir_path / "fuse_clean.srt",
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
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "fuse_clean.srt")
    ] == ["fused"]


@pytest.mark.parametrize("process_ocr", [process_eng_ocr, process_zho_ocr])
def test_process_ocr_wraps_filesystem_errors(
    process_ocr: Callable[..., OcrProcessingResult],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR processing maps filesystem errors to user-facing errors.

    Arguments:
        process_ocr: OCR processing workflow function to test
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """

    def fake_load(path: Path) -> ImageSeries:
        """Fake image subtitle loading failure.

        Arguments:
            path: image subtitle input path
        """
        raise FileNotFoundError(f"{path} missing")

    source_path = tmp_path / "source.sup"
    output_dir_path = tmp_path / "output"
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.ImageSeries.load",
        fake_load,
    )

    with pytest.raises(
        ScinoephileError,
        match=(
            "Unable to load OCR image subtitles from .*source.sup.*source.sup missing"
        ),
    ) as excinfo:
        process_ocr(source_path, output_dir_path, validate=False)

    assert isinstance(excinfo.value.__cause__, FileNotFoundError)


def test_process_eng_ocr_can_clean_provider_outputs_before_fusion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test English OCR processing can clean provider outputs before fusion.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    source_path = tmp_path / "source.sup"
    source_path.write_bytes(b"unused")
    output_dir_path = tmp_path / "output"

    pipeline = _PatchedEngOcrPipeline(
        monkeypatch,
        tiny_image_series,
        lens_texts=["lens..."],
        tesseract_texts=["[MUSIC] tesseract"],
    )

    result = process_eng_ocr(source_path, output_dir_path, clean=True, validate=False)

    assert pipeline.fusion_calls == [(["lens…"], ["tesseract"], pipeline.fuser)]
    assert result.output_paths == {
        "image": output_dir_path / "image",
        "lens": output_dir_path / "lens.srt",
        "tesseract": output_dir_path / "tesseract.srt",
        "lens_clean": output_dir_path / "lens_clean.srt",
        "tesseract_clean": output_dir_path / "tesseract_clean.srt",
        "fuse": output_dir_path / "fuse.srt",
        "fuse_clean": output_dir_path / "fuse_clean.srt",
    }
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "lens.srt")
    ] == ["lens..."]
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "tesseract.srt")
    ] == ["[MUSIC] tesseract"]
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "lens_clean.srt")
    ] == ["lens…"]
    assert [
        subtitle.text
        for subtitle in Series.load(output_dir_path / "tesseract_clean.srt")
    ] == ["tesseract"]


def test_process_eng_ocr_validates_fuse_clean_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test English OCR processing validates cleaned fused output by default.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    source_path = tmp_path / "source.sup"
    source_path.write_bytes(b"unused")
    output_dir_path = tmp_path / "output"
    manager_instances: list[object] = []
    manager_calls: list[bool] = []
    validate_calls: list[tuple[list[str], object]] = []

    class FakeValidationManager:
        """Fake validation manager."""

        def __init__(
            self,
            *,
            cache_dir_path: Path | str | None = None,
            dev: bool = False,
        ):
            """Initialize."""
            manager_instances.append(self)
            manager_calls.append(dev)

        def validate(self, series: ImageSeries) -> Series:
            """Validate an image series."""
            validate_calls.append(([subtitle.text for subtitle in series], self))
            return _series_with_texts(["validated 1", "validated 2"])

    _PatchedEngOcrPipeline(
        monkeypatch,
        tiny_image_series,
        lens_texts=["lens 1", "lens 2"],
        tesseract_texts=["tesseract 1", "tesseract 2"],
        fused_texts=["fused 1...", "fused 2..."],
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ValidationManager",
        FakeValidationManager,
    )

    result = process_eng_ocr(source_path, output_dir_path, dev=True)

    assert result.output_paths["image"] == output_dir_path / "image"
    assert result.output_paths["fuse_clean_validate"] == (
        output_dir_path / "fuse_clean_validate.srt"
    )
    assert manager_calls == [True]
    assert validate_calls == [(["fused 1…", "fused 2…"], manager_instances[0])]
    assert [
        subtitle.text
        for subtitle in Series.load(output_dir_path / "fuse_clean_validate.srt")
    ] == ["validated 1", "validated 2"]


def test_process_eng_ocr_interactive_launches_web_validation_for_sup(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test interactive OCR processing launches web validation after SUP extraction.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    source_path = tmp_path / "source.sup"
    source_path.write_bytes(b"unused")
    output_dir_path = tmp_path / "output"
    validate_calls: list[dict[str, object]] = []

    def fake_validate_ocr(
        infile_path: Path,
        outfile_path: Path,
        *,
        cache_dir_path: Path | str | None = None,
        interactive: bool = False,
        dev: bool = False,
        overwrite: bool = False,
        host: str = "127.0.0.1",
        port: int = 5000,
    ) -> Series:
        """Fake web validation by writing the expected validation output."""
        validate_calls.append(
            {
                "infile_path": infile_path,
                "outfile_path": outfile_path,
                "texts": [entry.text for entry in load_html_entries(infile_path)],
                "cache_dir_path": cache_dir_path,
                "interactive": interactive,
                "dev": dev,
                "overwrite": overwrite,
                "host": host,
                "port": port,
            }
        )
        validated = _series_with_texts(
            ["interactive validated 1", "interactive validated 2"]
        )
        validated.save(outfile_path)
        return validated

    _PatchedEngOcrPipeline(
        monkeypatch,
        tiny_image_series,
        lens_texts=["lens 1", "lens 2"],
        tesseract_texts=["tesseract 1", "tesseract 2"],
        fused_texts=["fused 1...", "fused 2..."],
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.validate_ocr",
        fake_validate_ocr,
    )

    result = process_eng_ocr(
        source_path,
        output_dir_path,
        interactive=True,
        dev=True,
        host="0.0.0.0",
        port=5050,
    )

    validate_path = output_dir_path / "fuse_clean_validate.srt"
    assert validate_calls == [
        {
            "infile_path": output_dir_path / "image",
            "outfile_path": validate_path,
            "texts": ["fused 1…", "fused 2…"],
            "cache_dir_path": None,
            "interactive": True,
            "dev": True,
            "overwrite": False,
            "host": "0.0.0.0",
            "port": 5050,
        }
    ]
    assert result.output_paths["fuse_clean_validate"] == validate_path
    assert [subtitle.text for subtitle in Series.load(validate_path)] == [
        "interactive validated 1",
        "interactive validated 2",
    ]


def test_process_eng_ocr_does_not_overwrite_existing_validation_images(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test validation does not overwrite existing image output by default.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    source_path = tmp_path / "source.sup"
    source_path.write_bytes(b"unused")
    output_dir_path = tmp_path / "output"
    image_dir_path = output_dir_path / "image"
    existing_image_series = ImageSeries(
        events=[
            type(tiny_image_series.events[0])(
                start=subtitle.start,
                end=subtitle.end,
                img=subtitle.img,
                text="existing text",
            )
            for subtitle in tiny_image_series.events
        ]
    )
    existing_image_series.save(image_dir_path)
    original_images = {
        image_path.name: image_path.read_bytes()
        for image_path in image_dir_path.glob("*.png")
    }
    validate_texts: list[list[str]] = []
    validate_managers: list[object] = []

    class FakeValidationManager:
        """Fake validation manager."""

        def __init__(
            self,
            *,
            cache_dir_path: Path | str | None = None,
            dev: bool = False,
        ):
            """Initialize."""

        def validate(self, series: ImageSeries) -> Series:
            """Validate an image series."""
            validate_managers.append(self)
            validate_texts.append([subtitle.text for subtitle in series])
            return _series_with_texts(["validated 1", "validated 2"])

    _PatchedEngOcrPipeline(
        monkeypatch,
        tiny_image_series,
        lens_texts=["lens 1", "lens 2"],
        tesseract_texts=["tesseract 1", "tesseract 2"],
        fused_texts=["fused 1...", "fused 2..."],
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ValidationManager",
        FakeValidationManager,
    )

    process_eng_ocr(source_path, output_dir_path)

    assert validate_texts == [["fused 1…", "fused 2…"]]
    assert len(validate_managers) == 1
    current_images = {
        image_path.name: image_path.read_bytes()
        for image_path in image_dir_path.glob("*.png")
    }
    assert current_images == original_images
    current_index = (image_dir_path / "index.html").read_text(encoding="utf-8")
    assert "fused 1…" in current_index
    assert "fused 2…" in current_index


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

    pipeline = _PatchedZhoOcrPipeline(monkeypatch, tiny_image_series)

    result = process_zho_ocr(source_path, output_dir_path, validate=False)

    assert pipeline.lens_calls == [Language.zho_hans]
    assert pipeline.paddle_calls == [Language.zho_hans]
    assert pipeline.fusion_calls == [(["lens"], ["paddle"], pipeline.fuser)]
    assert result.output_paths == {
        "image": output_dir_path / "image",
        "lens": output_dir_path / "lens.srt",
        "paddle": output_dir_path / "paddle.srt",
        "fuse": output_dir_path / "fuse.srt",
        "fuse_clean": output_dir_path / "fuse_clean.srt",
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
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "fuse_clean.srt")
    ] == ["fused"]


def test_process_zho_ocr_can_clean_provider_outputs_before_fusion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test Chinese OCR processing can clean provider outputs before fusion.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    source_path = tmp_path / "source.sup"
    source_path.write_bytes(b"unused")
    output_dir_path = tmp_path / "output"

    pipeline = _PatchedZhoOcrPipeline(
        monkeypatch,
        tiny_image_series,
        lens_texts=["镜头..."],
        paddle_texts=["字幕, 好?"],
    )

    result = process_zho_ocr(source_path, output_dir_path, clean=True, validate=False)

    assert pipeline.fusion_calls == [(["镜头⋯"], ["字幕，好？"], pipeline.fuser)]
    assert result.output_paths == {
        "image": output_dir_path / "image",
        "lens": output_dir_path / "lens.srt",
        "paddle": output_dir_path / "paddle.srt",
        "lens_clean": output_dir_path / "lens_clean.srt",
        "paddle_clean": output_dir_path / "paddle_clean.srt",
        "fuse": output_dir_path / "fuse.srt",
        "fuse_clean": output_dir_path / "fuse_clean.srt",
    }
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "lens.srt")
    ] == ["镜头..."]
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "paddle.srt")
    ] == ["字幕, 好?"]
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "lens_clean.srt")
    ] == ["镜头⋯"]
    assert [
        subtitle.text for subtitle in Series.load(output_dir_path / "paddle_clean.srt")
    ] == ["字幕，好？"]


def test_process_zho_ocr_passes_zho_hant_languages_to_ocr_engines(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test Chinese OCR processing maps zho-Hant to OCR language codes.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    source_path = tmp_path / "source.sup"
    source_path.write_bytes(b"unused")
    output_dir_path = tmp_path / "output"
    pipeline = _PatchedZhoOcrPipeline(monkeypatch, tiny_image_series)

    process_zho_ocr(
        source_path,
        output_dir_path,
        language="zho-Hant",
        validate=False,
    )
    assert pipeline.lens_calls == [Language.zho_hant]
    assert pipeline.paddle_calls == [Language.zho_hant]
    assert pipeline.fuser_calls == [
        {
            "provider": None,
            "additional_context": None,
            "prompt_cls": OcrFusionPromptZhoHant,
        }
    ]


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

    def fake_cache_subtitles(
        infile_path: Path,
        streams: list[SubtitleStream],
        *,
        cache_dir_path: Path | None = None,
    ):
        """Fake media subtitle caching."""
        cache_calls.append((infile_path, streams, cache_dir_path))

    pipeline = _PatchedEngOcrPipeline(monkeypatch, tiny_image_series)
    monkeypatch.setattr(
        "scinoephile.media.subtitles.selection.get_subtitle_streams",
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

    process_eng_ocr(source_path, output_dir_path, stream_index=5, validate=False)

    assert cache_calls == [(source_path, [stream], None)]
    assert pipeline.loaded_paths == [cached_sup_path]


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
        "scinoephile.media.subtitles.selection.get_subtitle_streams",
        lambda path: [SubtitleStream(index=5, codec_name="hdmv_pgs_subtitle")],
    )

    with pytest.raises(ScinoephileError, match="No subtitle stream 7"):
        process_eng_ocr(
            source_path,
            tmp_path / "output",
            stream_index=7,
            validate=False,
        )
