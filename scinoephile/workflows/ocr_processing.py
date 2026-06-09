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
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.cleaning import get_eng_cleaned
from scinoephile.lang.eng.ocr_fusion import get_eng_ocr_fused, get_eng_ocr_fuser
from scinoephile.lang.zho.cleaning import get_zho_cleaned
from scinoephile.lang.zho.ocr_fusion import (
    OcrFusionPromptZhoHant,
    get_zho_ocr_fused,
    get_zho_ocr_fuser,
)
from scinoephile.media.probe import get_subtitle_streams
from scinoephile.media.subtitles.cache import (
    cache_subtitles,
    get_subtitle_cache_path,
)

from .ocr_validation import validate_ocr

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
    output_paths = {}

    # Image
    _export_image_series(image_series, output_dir_path, overwrite, output_paths)

    # Google Lens
    lens = _load_or_create_series_output(
        output_dir_path,
        "lens",
        "Lens OCR output",
        overwrite,
        output_paths,
        lambda: ocr_image_series_with_lens(image_series, language="en"),
    )

    # Tesseract
    tesseract = _load_or_create_series_output(
        output_dir_path,
        "tesseract",
        "Tesseract OCR output",
        overwrite,
        output_paths,
        lambda: ocr_image_series_with_tesseract(image_series, language="eng"),
    )

    # Clean provider outputs
    if clean:
        lens = _load_or_create_series_output(
            output_dir_path,
            "lens_clean",
            "Cleaned Lens OCR output",
            overwrite,
            output_paths,
            lambda: get_eng_cleaned(lens, remove_empty=False),
        )
        tesseract = _load_or_create_series_output(
            output_dir_path,
            "tesseract_clean",
            "Cleaned Tesseract OCR output",
            overwrite,
            output_paths,
            lambda: get_eng_cleaned(tesseract, remove_empty=False),
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
    fuse_clean = _load_or_create_series_output(
        output_dir_path,
        "fuse_clean",
        "Cleaned fused OCR output",
        overwrite,
        output_paths,
        lambda: get_eng_cleaned(fuse, remove_empty=False),
    )

    # Validation
    if validate:
        _validate_fuse_clean_output(
            output_dir_path,
            fuse_clean,
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
    output_paths = {}

    # Image
    _export_image_series(image_series, output_dir_path, overwrite, output_paths)

    # Google Lens
    lens = _load_or_create_series_output(
        output_dir_path,
        "lens",
        "Lens OCR output",
        overwrite,
        output_paths,
        lambda: ocr_image_series_with_lens(image_series, language=lens_language),
    )

    # PaddleOCR
    paddle = _load_or_create_series_output(
        output_dir_path,
        "paddle",
        "PaddleOCR output",
        overwrite,
        output_paths,
        lambda: ocr_image_series_with_paddle(image_series, language=paddle_language),
    )

    # Clean provider outputs
    if clean:
        lens = _load_or_create_series_output(
            output_dir_path,
            "lens_clean",
            "Cleaned Lens OCR output",
            overwrite,
            output_paths,
            lambda: get_zho_cleaned(lens, remove_empty=False),
        )
        paddle = _load_or_create_series_output(
            output_dir_path,
            "paddle_clean",
            "Cleaned PaddleOCR output",
            overwrite,
            output_paths,
            lambda: get_zho_cleaned(paddle, remove_empty=False),
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
    fuse_clean = _load_or_create_series_output(
        output_dir_path,
        "fuse_clean",
        "Cleaned fused OCR output",
        overwrite,
        output_paths,
        lambda: get_zho_cleaned(fuse, remove_empty=False),
    )

    # Validation
    if validate:
        _validate_fuse_clean_output(
            output_dir_path,
            fuse_clean,
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

    try:
        streams = get_subtitle_streams(infile_path)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to inspect subtitle streams in {infile_path}: {exc}"
        ) from exc

    for stream in streams:
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
    try:
        if infile_path.is_dir() or infile_path.suffix.lower() == ".sup":
            return ImageSeries.load(infile_path)

        stream = _get_media_subtitle_stream(infile_path, stream_index)
        cache_subtitles(infile_path, [stream], cache_dir_path=cache_dir_path)
        stream_path = get_subtitle_cache_path(
            infile_path, stream, cache_dir_path=cache_dir_path
        )
        return ImageSeries.load(stream_path)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to load OCR image subtitles from {infile_path}: {exc}"
        ) from exc


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
            processor=get_eng_ocr_fuser(provider=provider, **kwargs),
        ),
    )


def _load_or_create_series_output(
    output_dir_path: Path,
    output_name: str,
    display_name: str,
    overwrite: bool,
    output_paths: dict[str, Path],
    create_series: Callable[[], Series],
) -> Series:
    """Load or create a text subtitle output.

    Arguments:
        output_dir_path: OCR output directory
        output_name: output name
        display_name: output display name for logs
        overwrite: whether to overwrite existing workflow outputs
        output_paths: output paths to update
        create_series: function that creates the series when needed
    Returns:
        text subtitle series
    """
    output_path = output_dir_path / f"{output_name}.srt"
    try:
        if output_path.exists() and not overwrite:
            logger.info(f"{display_name} exists: {output_path}")
            series = Series.load(output_path)
        else:
            series = create_series()
            series.save(output_path, format_="srt")
    except (OSError, RuntimeError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to load or create {display_name} at {output_path}: {exc}"
        ) from exc
    output_paths[output_name] = output_path
    return series


def _validate_fuse_clean_output(
    output_dir_path: Path,
    text_series: Series,
    *,
    interactive: bool,
    dev: bool,
    overwrite: bool,
    host: str,
    port: int,
    output_paths: dict[str, Path],
):
    """Validate cleaned fused OCR output.

    Arguments:
        output_dir_path: OCR output directory
        text_series: cleaned fused OCR output
        interactive: whether to launch the OCR validation web UI
        dev: whether validation should write data updates to repo data
        overwrite: whether to overwrite existing workflow outputs
        host: OCR validation web UI host
        port: OCR validation web UI port
        output_paths: output paths to update
    """
    validate_path = output_dir_path / "fuse_clean_validate.srt"
    if validate_path.exists() and not overwrite:
        logger.info(f"Validated OCR output exists: {validate_path}")
        Series.load(validate_path)
        output_paths["fuse_clean_validate"] = validate_path
        return

    image_dir_path = output_dir_path / "image"
    # Validation reads OCR text from the image index, so write fused text there
    image_series = ImageSeries.load(image_dir_path)
    image_series.copy_text_from(text_series)
    image_series.save(image_dir_path)

    validate_ocr(
        image_dir_path,
        validate_path,
        interactive=interactive,
        dev=dev,
        overwrite=overwrite,
        host=host,
        port=port,
    )
    output_paths["fuse_clean_validate"] = validate_path


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
            processor=get_zho_ocr_fuser(provider=provider, **kwargs),
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
