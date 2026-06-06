#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for processing image subtitle OCR end to end."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Any

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.core.media import SubtitleStream
from scinoephile.core.subtitles import Series
from scinoephile.core.text import ChineseScript
from scinoephile.image.ocr.lens import get_lens_zho_code, ocr_image_series_with_lens
from scinoephile.image.ocr.paddle import (
    get_paddle_zho_code,
    ocr_image_series_with_paddle,
)
from scinoephile.image.ocr.tesseract import ocr_image_series_with_tesseract
from scinoephile.image.ocr.validation import ValidationManager
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from scinoephile.lang.eng.cleaning import get_eng_cleaned
from scinoephile.lang.eng.ocr_fusion import get_eng_ocr_fused, get_eng_ocr_fuser
from scinoephile.lang.eng.ocr_validation import validate_eng_ocr
from scinoephile.lang.zho.cleaning import get_zho_cleaned
from scinoephile.lang.zho.ocr_fusion import (
    OcrFusionPromptZhoHant,
    get_zho_ocr_fused,
    get_zho_ocr_fuser,
)
from scinoephile.lang.zho.ocr_validation import validate_zho_ocr
from scinoephile.media.probe import get_subtitle_streams
from scinoephile.media.subtitles.cache import (
    cache_subtitles,
    get_subtitle_cache_path,
)

__all__ = [
    "OcrProcessingResult",
    "process_eng_ocr",
    "process_zho_ocr",
]

logger = getLogger(__name__)


@dataclass(frozen=True)
class OcrProcessingResult:
    """Result of an OCR processing workflow run."""

    infile_path: Path
    """Input path processed by the workflow."""
    output_dir_path: Path
    """Directory containing workflow outputs."""
    output_paths: dict[str, Path]
    """Output paths keyed by output name."""


def process_eng_ocr(
    infile_path: Path,
    output_dir_path: Path,
    *,
    source_dir_path: Path | None = None,
    stream_index: int | None = None,
    cache_dir_path: Path | None = None,
    clean: bool = False,
    validate: bool = True,
    interactive: bool = False,
    dev: bool = False,
    overwrite: bool = False,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    fuser_kw: dict[str, Any] | None = None,
    host: str = "127.0.0.1",
    port: int = 5000,
) -> OcrProcessingResult:
    """Process English image subtitle OCR and fuse the OCR outputs.

    Arguments:
        infile_path: SUP, image subtitle directory, or media input path
        output_dir_path: directory where OCR outputs are written
        source_dir_path: optional directory containing existing provider OCR outputs
        stream_index: media subtitle stream index when infile is media
        cache_dir_path: media subtitle cache directory path
        clean: whether to clean OCR subtitle outputs before fusing
        validate: whether to validate fused OCR subtitles against images
        interactive: whether to launch the OCR validation web UI
        dev: whether validation should write data updates to repo data
        overwrite: whether to overwrite existing workflow outputs
        provider: provider to use for OCR fusion queries
        additional_context: additional context to include in OCR fusion prompts
        fuser_kw: keyword arguments for OCR fuser construction
        host: OCR validation web UI host
        port: OCR validation web UI port
    Returns:
        OCR processing result
    """
    # Read inputs
    image_series = _load_image_series(infile_path, stream_index, cache_dir_path)

    # Write outputs
    _ensure_output_dir(output_dir_path)
    output_paths = {}

    # Image
    _export_image_series(image_series, output_dir_path, overwrite, output_paths)

    # Google Lens
    lens = _load_or_create_lens_output(
        image_series,
        output_dir_path,
        "en",
        overwrite,
        output_paths,
        _source_output_path(source_dir_path, "lens"),
    )

    # Tesseract
    tesseract = _load_or_create_tesseract_output(
        image_series,
        output_dir_path,
        overwrite,
        output_paths,
        _source_output_path(source_dir_path, "tesseract"),
    )

    # Clean provider outputs
    if clean:
        lens = _load_or_create_eng_clean_output(
            output_dir_path, "lens", lens, overwrite, output_paths
        )
        tesseract = _load_or_create_eng_clean_output(
            output_dir_path, "tesseract", tesseract, overwrite, output_paths
        )

    # Fusion
    fuse = _load_or_create_eng_fuse_output(
        output_dir_path,
        lens,
        tesseract,
        overwrite,
        provider,
        additional_context,
        fuser_kw,
        output_paths,
    )
    fuse_clean = _load_or_create_eng_clean_output(
        output_dir_path, "fuse", fuse, overwrite, output_paths
    )

    # Validation
    if validate:
        _load_or_create_validation_output(
            output_dir_path,
            image_series,
            fuse_clean,
            "eng",
            interactive=interactive,
            dev=dev,
            overwrite=overwrite,
            host=host,
            port=port,
            output_paths=output_paths,
        )

    return OcrProcessingResult(
        infile_path=infile_path,
        output_dir_path=output_dir_path,
        output_paths=output_paths,
    )


def process_zho_ocr(
    infile_path: Path,
    output_dir_path: Path,
    *,
    source_dir_path: Path | None = None,
    stream_index: int | None = None,
    cache_dir_path: Path | None = None,
    script: ChineseScript = "simplified",
    clean: bool = False,
    validate: bool = True,
    interactive: bool = False,
    dev: bool = False,
    overwrite: bool = False,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    fuser_kw: dict[str, Any] | None = None,
    host: str = "127.0.0.1",
    port: int = 5000,
) -> OcrProcessingResult:
    """Process standard Chinese image subtitle OCR and fuse the OCR outputs.

    Arguments:
        infile_path: SUP, image subtitle directory, or media input path
        output_dir_path: directory where OCR outputs are written
        source_dir_path: optional directory containing existing provider OCR outputs
        stream_index: media subtitle stream index when infile is media
        cache_dir_path: media subtitle cache directory path
        script: Chinese script to OCR, either simplified or traditional
        clean: whether to clean OCR subtitle outputs before fusing
        validate: whether to validate fused OCR subtitles against images
        interactive: whether to launch the OCR validation web UI
        dev: whether validation should write data updates to repo data
        overwrite: whether to overwrite existing workflow outputs
        provider: provider to use for OCR fusion queries
        additional_context: additional context to include in OCR fusion prompts
        fuser_kw: keyword arguments for OCR fuser construction
        host: OCR validation web UI host
        port: OCR validation web UI port
    Returns:
        OCR processing result
    """
    lens_language = get_lens_zho_code(script)
    paddle_language = get_paddle_zho_code(script)

    # Read inputs
    image_series = _load_image_series(infile_path, stream_index, cache_dir_path)

    # Write outputs
    _ensure_output_dir(output_dir_path)
    output_paths = {}

    # Image
    _export_image_series(image_series, output_dir_path, overwrite, output_paths)

    # Google Lens
    lens = _load_or_create_lens_output(
        image_series,
        output_dir_path,
        lens_language,
        overwrite,
        output_paths,
        _source_output_path(source_dir_path, "lens"),
    )

    # PaddleOCR
    paddle = _load_or_create_paddle_output(
        image_series,
        output_dir_path,
        paddle_language,
        overwrite,
        output_paths,
        _source_output_path(source_dir_path, "paddle"),
    )

    # Clean provider outputs
    if clean:
        lens = _load_or_create_zho_clean_output(
            output_dir_path, "lens", lens, overwrite, output_paths
        )
        paddle = _load_or_create_zho_clean_output(
            output_dir_path, "paddle", paddle, overwrite, output_paths
        )

    # Fusion
    fuse = _load_or_create_zho_fuse_output(
        output_dir_path,
        lens,
        paddle,
        script,
        overwrite,
        provider,
        additional_context,
        fuser_kw,
        output_paths,
    )
    fuse_clean = _load_or_create_zho_clean_output(
        output_dir_path, "fuse", fuse, overwrite, output_paths
    )

    # Validation
    if validate:
        _load_or_create_validation_output(
            output_dir_path,
            image_series,
            fuse_clean,
            "zho",
            interactive=interactive,
            dev=dev,
            overwrite=overwrite,
            host=host,
            port=port,
            output_paths=output_paths,
        )

    return OcrProcessingResult(
        infile_path=infile_path,
        output_dir_path=output_dir_path,
        output_paths=output_paths,
    )


def _ensure_output_dir(output_dir_path: Path):
    """Ensure an OCR output directory exists.

    Arguments:
        output_dir_path: OCR output directory
    """
    if output_dir_path.exists():
        return
    output_dir_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created output directory: {output_dir_path}")


def _export_image_series(
    image_series: ImageSeries,
    output_dir_path: Path,
    overwrite: bool,
    output_paths: dict[str, Path],
):
    """Export source image subtitles.

    Arguments:
        image_series: image subtitle series
        output_dir_path: OCR output directory
        overwrite: whether to overwrite existing workflow outputs
        output_paths: output paths to update
    """
    image_dir_path = output_dir_path / "image"
    if image_dir_path.exists() and not overwrite:
        logger.info(f"Image OCR output exists: {image_dir_path}")
    else:
        image_series.save(image_dir_path)
    output_paths["image"] = image_dir_path


def _get_image_series_with_text(
    image_series: ImageSeries,
    text_series: Series,
) -> ImageSeries:
    """Get a copy of image subtitles with matching text subtitle text.

    Arguments:
        image_series: image subtitle series
        text_series: text subtitle series
    Returns:
        copied image subtitle series with text
    """
    if len(text_series) != len(image_series):
        raise ScinoephileError(
            f"Length mismatch: {len(text_series)} vs {len(image_series)}"
        )
    image_subtitles: list[ImageSubtitle] = []
    for text_subtitle, image_subtitle in zip(text_series, image_series.events):
        if image_subtitle.bboxes is None:
            bboxes = None
        else:
            bboxes = list(image_subtitle.bboxes)
        image_subtitles.append(
            ImageSubtitle(
                img=image_subtitle.img.copy(),
                bboxes=bboxes,
                start=image_subtitle.start,
                end=image_subtitle.end,
                text=text_subtitle.text,
            )
        )
    return ImageSeries(events=image_subtitles)


def _get_media_subtitle_stream(
    infile_path: Path,
    stream_index: int | None,
) -> SubtitleStream:
    """Get selected subtitle stream from media input.

    Arguments:
        infile_path: media input path
        stream_index: media subtitle stream index
    Returns:
        selected subtitle stream
    """
    if stream_index is None:
        raise ScinoephileError("stream index is required for media OCR input")

    for stream in get_subtitle_streams(infile_path):
        if stream.index == stream_index:
            if stream.extension != "sup":
                raise ScinoephileError(
                    f"Subtitle stream {stream_index} is not an image-based SUP stream"
                )
            return stream
    raise ScinoephileError(f"No subtitle stream {stream_index} found in {infile_path}")


def _load_image_series(
    infile_path: Path,
    stream_index: int | None,
    cache_dir_path: Path | None,
) -> ImageSeries:
    """Load image subtitles from SUP, image directory, or selected media stream.

    Arguments:
        infile_path: SUP, image subtitle directory, or media input path
        stream_index: media subtitle stream index when infile is media
        cache_dir_path: media subtitle cache directory path
    Returns:
        image subtitle series
    """
    if infile_path.is_dir() or infile_path.suffix.lower() == ".sup":
        return ImageSeries.load(infile_path)

    stream = _get_media_subtitle_stream(infile_path, stream_index)
    cache_subtitles(infile_path, [stream], cache_dir_path=cache_dir_path)
    stream_path = get_subtitle_cache_path(
        infile_path, stream, cache_dir_path=cache_dir_path
    )
    return ImageSeries.load(stream_path)


def _load_or_create_eng_clean_output(
    output_dir_path: Path,
    output_name: str,
    series: Series,
    overwrite: bool,
    output_paths: dict[str, Path],
) -> Series:
    """Load or create a cleaned English OCR provider output.

    Arguments:
        output_dir_path: OCR output directory
        output_name: output name
        series: source series to clean
        overwrite: whether to overwrite existing workflow outputs
        output_paths: output paths to update
    Returns:
        cleaned series
    """
    if output_name == "fuse":
        display_name = "Cleaned fused OCR output"
    elif output_name == "tesseract":
        display_name = "Cleaned Tesseract OCR output"
    else:
        display_name = "Cleaned Lens OCR output"
    return _load_or_create_series_output(
        output_dir_path,
        f"{output_name}_clean",
        display_name,
        overwrite,
        output_paths,
        lambda: get_eng_cleaned(series, remove_empty=False),
    )


def _load_or_create_eng_fuse_output(
    output_dir_path: Path,
    lens: Series,
    tesseract: Series,
    overwrite: bool,
    provider: LLMProvider | None,
    additional_context: str | None,
    fuser_kw: dict[str, Any] | None,
    output_paths: dict[str, Path],
) -> Series:
    """Load or create fused English OCR output.

    Arguments:
        output_dir_path: OCR output directory
        lens: Google Lens OCR series
        tesseract: Tesseract OCR series
        overwrite: whether to overwrite existing workflow outputs
        provider: provider to use for OCR fusion queries
        additional_context: additional context to include in OCR fusion prompts
        fuser_kw: keyword arguments for OCR fuser construction
        output_paths: output paths to update
    Returns:
        fused English OCR series
    """
    kwargs = _get_fuser_kw(fuser_kw, additional_context)
    return _load_or_create_series_output(
        output_dir_path,
        "fuse",
        "Fuse OCR output",
        overwrite,
        output_paths,
        lambda: get_eng_ocr_fused(
            lens,
            tesseract,
            processor=get_eng_ocr_fuser(
                provider=provider,
                **kwargs,
            ),
        ),
    )


def _load_or_create_lens_output(
    image_series: ImageSeries,
    output_dir_path: Path,
    language: str,
    overwrite: bool,
    output_paths: dict[str, Path],
    source_path: Path | None,
) -> Series:
    """Load or create Google Lens OCR output.

    Arguments:
        image_series: image subtitle series
        output_dir_path: OCR output directory
        language: Google Lens language code
        overwrite: whether to overwrite existing workflow outputs
        output_paths: output paths to update
        source_path: optional existing Google Lens OCR output path
    Returns:
        Google Lens OCR series
    """
    return _load_or_create_series_output(
        output_dir_path,
        "lens",
        "Lens OCR output",
        overwrite,
        output_paths,
        lambda: ocr_image_series_with_lens(image_series, language=language),
        source_path,
    )


def _load_or_create_paddle_output(
    image_series: ImageSeries,
    output_dir_path: Path,
    language: str,
    overwrite: bool,
    output_paths: dict[str, Path],
    source_path: Path | None,
) -> Series:
    """Load or create PaddleOCR output.

    Arguments:
        image_series: image subtitle series
        output_dir_path: OCR output directory
        language: PaddleOCR language code
        overwrite: whether to overwrite existing workflow outputs
        output_paths: output paths to update
        source_path: optional existing PaddleOCR output path
    Returns:
        PaddleOCR series
    """
    return _load_or_create_series_output(
        output_dir_path,
        "paddle",
        "PaddleOCR output",
        overwrite,
        output_paths,
        lambda: ocr_image_series_with_paddle(image_series, language=language),
        source_path,
    )


def _load_or_create_series_output(
    output_dir_path: Path,
    output_name: str,
    display_name: str,
    overwrite: bool,
    output_paths: dict[str, Path],
    create_series: Callable[[], Series],
    source_path: Path | None = None,
) -> Series:
    """Load or create a text subtitle output.

    Arguments:
        output_dir_path: OCR output directory
        output_name: output name
        display_name: output display name for logs
        overwrite: whether to overwrite existing workflow outputs
        output_paths: output paths to update
        create_series: function that creates the series when needed
        source_path: optional existing source output path to copy from
    Returns:
        text subtitle series
    """
    output_path = output_dir_path / f"{output_name}.srt"
    if output_path.exists() and not overwrite:
        logger.info(f"{display_name} exists: {output_path}")
        series = Series.load(output_path)
    elif source_path is not None and source_path.exists():
        logger.info(f"Using existing {display_name}: {source_path}")
        series = Series.load(source_path)
        series.save(output_path, format_="srt")
    else:
        series = create_series()
        series.save(output_path, format_="srt")
    output_paths[output_name] = output_path
    return series


def _load_or_create_tesseract_output(
    image_series: ImageSeries,
    output_dir_path: Path,
    overwrite: bool,
    output_paths: dict[str, Path],
    source_path: Path | None,
) -> Series:
    """Load or create Tesseract OCR output.

    Arguments:
        image_series: image subtitle series
        output_dir_path: OCR output directory
        overwrite: whether to overwrite existing workflow outputs
        output_paths: output paths to update
        source_path: optional existing Tesseract OCR output path
    Returns:
        Tesseract OCR series
    """
    return _load_or_create_series_output(
        output_dir_path,
        "tesseract",
        "Tesseract OCR output",
        overwrite,
        output_paths,
        lambda: ocr_image_series_with_tesseract(image_series, language="eng"),
        source_path,
    )


def _load_or_create_zho_clean_output(
    output_dir_path: Path,
    output_name: str,
    series: Series,
    overwrite: bool,
    output_paths: dict[str, Path],
) -> Series:
    """Load or create a cleaned Chinese OCR provider output.

    Arguments:
        output_dir_path: OCR output directory
        output_name: output name
        series: source series to clean
        overwrite: whether to overwrite existing workflow outputs
        output_paths: output paths to update
    Returns:
        cleaned series
    """
    if output_name == "fuse":
        display_name = "Cleaned fused OCR output"
    elif output_name == "paddle":
        display_name = "Cleaned PaddleOCR output"
    else:
        display_name = "Cleaned Lens OCR output"
    return _load_or_create_series_output(
        output_dir_path,
        f"{output_name}_clean",
        display_name,
        overwrite,
        output_paths,
        lambda: get_zho_cleaned(series, remove_empty=False),
    )


def _load_or_create_zho_fuse_output(
    output_dir_path: Path,
    lens: Series,
    paddle: Series,
    script: ChineseScript,
    overwrite: bool,
    provider: LLMProvider | None,
    additional_context: str | None,
    fuser_kw: dict[str, Any] | None,
    output_paths: dict[str, Path],
) -> Series:
    """Load or create fused Chinese OCR output.

    Arguments:
        output_dir_path: OCR output directory
        lens: Google Lens OCR series
        paddle: PaddleOCR series
        script: Chinese script to OCR, either simplified or traditional
        overwrite: whether to overwrite existing workflow outputs
        provider: provider to use for OCR fusion queries
        additional_context: additional context to include in OCR fusion prompts
        fuser_kw: keyword arguments for OCR fuser construction
        output_paths: output paths to update
    Returns:
        fused Chinese OCR series
    """
    kwargs = _get_fuser_kw(fuser_kw, additional_context)
    if script == "traditional":
        kwargs.setdefault("prompt_cls", OcrFusionPromptZhoHant)
    return _load_or_create_series_output(
        output_dir_path,
        "fuse",
        "Fuse OCR output",
        overwrite,
        output_paths,
        lambda: get_zho_ocr_fused(
            lens,
            paddle,
            processor=get_zho_ocr_fuser(
                provider=provider,
                **kwargs,
            ),
        ),
    )


def _get_fuser_kw(
    fuser_kw: dict[str, Any] | None,
    additional_context: str | None,
) -> dict[str, Any]:
    """Get keyword arguments for OCR fuser construction.

    Arguments:
        fuser_kw: caller-provided keyword arguments
        additional_context: additional context to include in OCR fusion prompts
    Returns:
        keyword arguments for OCR fuser construction
    """
    if fuser_kw is None:
        kwargs: dict[str, Any] = {}
    else:
        kwargs = dict(fuser_kw)
    kwargs.setdefault("additional_context", additional_context)
    return kwargs


def _load_or_create_validation_image_series(
    output_dir_path: Path,
    image_series: ImageSeries,
    text_series: Series,
    overwrite: bool,
    output_paths: dict[str, Path],
) -> ImageSeries:
    """Load or create image subtitles with OCR text.

    Arguments:
        output_dir_path: OCR output directory
        image_series: source image subtitle series
        text_series: text subtitle series to copy into image subtitles
        overwrite: whether to overwrite existing workflow outputs
        output_paths: output paths to update
    Returns:
        image subtitle series with OCR text
    """
    image_dir_path = output_dir_path / "image"
    if image_dir_path.exists() and not overwrite:
        logger.info(f"Image OCR output exists: {image_dir_path}")
        stored_image_series = ImageSeries.load(image_dir_path)
        validation_image_series = _get_image_series_with_text(
            stored_image_series, text_series
        )
    else:
        validation_image_series = _get_image_series_with_text(image_series, text_series)
        validation_image_series.save(image_dir_path)
    output_paths["image"] = image_dir_path
    return validation_image_series


def _load_or_create_validation_output(
    output_dir_path: Path,
    image_series: ImageSeries,
    text_series: Series,
    language: str,
    *,
    interactive: bool,
    dev: bool,
    overwrite: bool,
    host: str,
    port: int,
    output_paths: dict[str, Path],
) -> Series:
    """Load or create OCR validation output.

    Arguments:
        output_dir_path: OCR output directory
        image_series: source image subtitle series
        text_series: text subtitle series to validate
        language: OCR validation language
        interactive: whether to launch the OCR validation web UI
        dev: whether validation should write data updates to repo data
        overwrite: whether to overwrite existing workflow outputs
        host: OCR validation web UI host
        port: OCR validation web UI port
        output_paths: output paths to update
    Returns:
        validated text subtitle series
    """
    validate_path = output_dir_path / "fuse_clean_validate.srt"
    if validate_path.exists() and not overwrite:
        logger.info(f"Validated OCR output exists: {validate_path}")
        output_paths["fuse_clean_validate"] = validate_path
        return Series.load(validate_path)

    validation_image_series = _load_or_create_validation_image_series(
        output_dir_path,
        image_series,
        text_series,
        overwrite,
        output_paths,
    )
    if interactive:
        _run_interactive_validation(output_dir_path, validate_path, dev, host, port)
    else:
        validated = _validate_ocr(validation_image_series, language, dev)
        validated.save(validate_path, format_="srt", exist_ok=True)
    output_paths["fuse_clean_validate"] = validate_path
    return Series.load(validate_path)


def _run_interactive_validation(
    output_dir_path: Path,
    outfile_path: Path,
    dev: bool,
    host: str,
    port: int,
):
    """Run interactive OCR validation.

    Arguments:
        output_dir_path: OCR output directory
        outfile_path: validated subtitle output path
        dev: whether validation should write data updates to repo data
        host: OCR validation web UI host
        port: OCR validation web UI port
    """
    from scinoephile.web.ocr_validation import (  # noqa: PLC0415
        OcrValidationSession,
        create_app,
    )

    session = OcrValidationSession.from_dir_path(
        output_dir_path / "image",
        outfile_path=outfile_path,
        dev=dev,
    )
    create_app(session).run(host=host, port=port)


def _source_output_path(source_dir_path: Path | None, output_name: str) -> Path | None:
    """Get source OCR output path if a source directory was provided.

    Arguments:
        source_dir_path: optional source OCR output directory
        output_name: OCR output name
    Returns:
        source OCR output path, if available
    """
    if source_dir_path is None:
        return None
    return source_dir_path / f"{output_name}.srt"


def _validate_ocr(image_series: ImageSeries, language: str, dev: bool) -> Series:
    """Validate OCR subtitles against image subtitles.

    Arguments:
        image_series: image subtitle series with OCR text
        language: OCR validation language
        dev: whether validation should write data updates to repo data
    Returns:
        validated text subtitle series
    """
    if language == "eng":
        return validate_eng_ocr(
            image_series,
            validation_manager=ValidationManager(dev=dev),
        )
    return validate_zho_ocr(image_series, dev=dev)
