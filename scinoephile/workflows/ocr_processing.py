#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for processing image subtitle OCR end to end."""

from __future__ import annotations

from dataclasses import dataclass
from logging import getLogger, info
from pathlib import Path
from typing import Literal

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.core.media import SubtitleStream
from scinoephile.core.subtitles import Series
from scinoephile.image.ocr.lens import ocr_image_series_with_lens
from scinoephile.image.ocr.paddle import ocr_image_series_with_paddle
from scinoephile.image.ocr.tesseract import ocr_image_series_with_tesseract
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.ocr_fusion import get_eng_ocr_fused, get_eng_ocr_fuser
from scinoephile.lang.zho.ocr_fusion import get_zho_ocr_fused, get_zho_ocr_fuser
from scinoephile.media.probe import get_subtitle_streams
from scinoephile.media.subtitles.cache import (
    cache_subtitles,
    get_subtitle_cache_path,
)

__all__ = [
    "ChineseScript",
    "OcrProcessingResult",
    "process_eng_ocr",
    "process_zho_ocr",
]

logger = getLogger(__name__)

type ChineseScript = Literal["simplified", "traditional"]
"""Chinese script supported by standard Chinese OCR processing."""


@dataclass(frozen=True)
class OcrProcessingResult:
    """Result of an OCR processing workflow run."""

    infile_path: Path
    """Input path processed by the workflow."""
    output_dir_path: Path
    """Directory containing workflow outputs."""
    output_paths: dict[str, Path]
    """Output paths keyed by output name."""


def process_eng_ocr(  # noqa: PLR0912
    infile_path: Path,
    output_dir_path: Path,
    *,
    stream_index: int | None = None,
    cache_dir_path: Path | None = None,
    export_images: bool = False,
    overwrite: bool = False,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
) -> OcrProcessingResult:
    """Process English image subtitle OCR and fuse the OCR outputs.

    Arguments:
        infile_path: SUP, image subtitle directory, or media input path
        output_dir_path: directory where OCR outputs are written
        stream_index: media subtitle stream index when infile is media
        cache_dir_path: media subtitle cache directory path
        export_images: whether to export OCR outputs as image subtitle directories
        overwrite: whether to overwrite existing workflow outputs
        provider: provider to use for OCR fusion queries
        additional_context: additional context to include in OCR fusion prompts
    Returns:
        OCR processing result
    """
    # Read inputs
    image_series = _load_image_series(infile_path, stream_index, cache_dir_path)

    # Write outputs
    if not output_dir_path.exists():
        output_dir_path.mkdir(parents=True, exist_ok=True)
        info(f"Created output directory: {output_dir_path}")
    output_paths = {}

    # Image
    if export_images:
        image_dir_path = output_dir_path / "image"
        if image_dir_path.exists() and not overwrite:
            logger.info(f"Image OCR output exists: {image_dir_path}")
        else:
            image_series.save(image_dir_path)
        output_paths["image"] = image_dir_path

    # Google Lens
    lens_path = output_dir_path / "lens.srt"
    if lens_path.exists() and not overwrite:
        logger.info(f"Lens OCR output exists: {lens_path}")
        lens = Series.load(lens_path)
    else:
        lens = ocr_image_series_with_lens(image_series, language="en")
        lens.save(lens_path, format_="srt")
    output_paths["lens"] = lens_path

    # Tesseract
    tesseract_path = output_dir_path / "tesseract.srt"
    if tesseract_path.exists() and not overwrite:
        logger.info(f"Tesseract OCR output exists: {tesseract_path}")
        tesseract = Series.load(tesseract_path)
    else:
        tesseract = ocr_image_series_with_tesseract(image_series, language="eng")
        tesseract.save(tesseract_path, format_="srt")
    output_paths["tesseract"] = tesseract_path

    # Fusion
    fuse_path = output_dir_path / "fuse.srt"
    if fuse_path.exists() and not overwrite:
        logger.info(f"Fuse OCR output exists: {fuse_path}")
    else:
        fuser = get_eng_ocr_fuser(
            provider=provider,
            additional_context=additional_context,
        )
        fuse = get_eng_ocr_fused(lens, tesseract, processor=fuser)
        fuse.save(fuse_path, format_="srt")
    output_paths["fuse"] = fuse_path

    return OcrProcessingResult(
        infile_path=infile_path,
        output_dir_path=output_dir_path,
        output_paths=output_paths,
    )


def process_zho_ocr(  # noqa: PLR0912
    infile_path: Path,
    output_dir_path: Path,
    *,
    stream_index: int | None = None,
    cache_dir_path: Path | None = None,
    script: ChineseScript = "simplified",
    export_images: bool = False,
    overwrite: bool = False,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
) -> OcrProcessingResult:
    """Process standard Chinese image subtitle OCR and fuse the OCR outputs.

    Arguments:
        infile_path: SUP, image subtitle directory, or media input path
        output_dir_path: directory where OCR outputs are written
        stream_index: media subtitle stream index when infile is media
        cache_dir_path: media subtitle cache directory path
        script: Chinese script to OCR, either simplified or traditional
        export_images: whether to export OCR outputs as image subtitle directories
        overwrite: whether to overwrite existing workflow outputs
        provider: provider to use for OCR fusion queries
        additional_context: additional context to include in OCR fusion prompts
    Returns:
        OCR processing result
    """
    if script == "simplified":
        lens_language = "zh-CN"
        paddle_language = "ch"
    elif script == "traditional":
        lens_language = "zh-TW"
        paddle_language = "chinese_cht"
    else:
        raise ValueError(
            f"{script!r} is not one of the supported Chinese scripts: "
            "simplified, traditional"
        )

    # Read inputs
    image_series = _load_image_series(infile_path, stream_index, cache_dir_path)

    # Write outputs
    if not output_dir_path.exists():
        output_dir_path.mkdir(parents=True, exist_ok=True)
        info(f"Created output directory: {output_dir_path}")
    output_paths = {}

    # Image
    if export_images:
        image_dir_path = output_dir_path / "image"
        if image_dir_path.exists() and not overwrite:
            logger.info(f"Image OCR output exists: {image_dir_path}")
        else:
            image_series.save(image_dir_path)
        output_paths["image"] = image_dir_path

    # Google Lens
    lens_path = output_dir_path / "lens.srt"
    if lens_path.exists() and not overwrite:
        logger.info(f"Lens OCR output exists: {lens_path}")
        lens = Series.load(lens_path)
    else:
        lens = ocr_image_series_with_lens(image_series, language=lens_language)
        lens.save(lens_path, format_="srt")
    output_paths["lens"] = lens_path

    # PaddleOCR
    paddle_path = output_dir_path / "paddle.srt"
    if paddle_path.exists() and not overwrite:
        logger.info(f"PaddleOCR output exists: {paddle_path}")
        paddle = Series.load(paddle_path)
    else:
        paddle = ocr_image_series_with_paddle(image_series, language=paddle_language)
        paddle.save(paddle_path, format_="srt")
    output_paths["paddle"] = paddle_path

    # Fusion
    fuse_path = output_dir_path / "fuse.srt"
    if fuse_path.exists() and not overwrite:
        logger.info(f"Fuse OCR output exists: {fuse_path}")
    else:
        fuser = get_zho_ocr_fuser(
            provider=provider,
            additional_context=additional_context,
        )
        fuse = get_zho_ocr_fused(lens, paddle, processor=fuser)
        fuse.save(fuse_path, format_="srt")
    output_paths["fuse"] = fuse_path

    return OcrProcessingResult(
        infile_path=infile_path,
        output_dir_path=output_dir_path,
        output_paths=output_paths,
    )


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
