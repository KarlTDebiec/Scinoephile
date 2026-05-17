#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for processing image subtitle OCR end to end."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import cast

from scinoephile.common import DirectoryNotFoundError
from scinoephile.core import ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.core.media import SubtitleStream
from scinoephile.core.subtitles import Series
from scinoephile.image.ocr.lens import ocr_image_series_with_lens
from scinoephile.image.ocr.paddle import ocr_image_series_with_paddle
from scinoephile.image.ocr.tesseract import ocr_image_series_with_tesseract
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from scinoephile.lang.eng.ocr_fusion import get_eng_ocr_fused, get_eng_ocr_fuser
from scinoephile.lang.zho.ocr_fusion import get_zho_ocr_fused, get_zho_ocr_fuser
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
    infile_path = _resolve_input_path(infile_path)
    output_dir_path = output_dir_path.resolve()
    output_dir_path.mkdir(parents=True, exist_ok=True)

    image_series = _load_image_series(infile_path, stream_index, cache_dir_path)
    image_dir_path = output_dir_path / "image"
    _save_image_series(image_series, image_dir_path, overwrite)

    # Process OCR outputs
    lens_path = output_dir_path / "lens.srt"
    lens_dir_path = output_dir_path / "lens"
    tesseract_path = output_dir_path / "tesseract.srt"
    tesseract_dir_path = output_dir_path / "tesseract"
    fuse_path = output_dir_path / "fuse.srt"
    fuse_dir_path = output_dir_path / "fuse"

    def lens_builder() -> Series:
        """Build English Google Lens OCR output."""
        return ocr_image_series_with_lens(image_series, language="en")

    def tesseract_builder() -> Series:
        """Build English Tesseract OCR output."""
        return ocr_image_series_with_tesseract(
            image_series,
            detect_italics=False,
            language="eng",
        )

    lens = _get_or_build_series(lens_path, lens_builder, overwrite)
    if export_images:
        _save_text_image_series(image_series, lens, lens_dir_path, overwrite)
    tesseract = _get_or_build_series(tesseract_path, tesseract_builder, overwrite)
    if export_images:
        _save_text_image_series(image_series, tesseract, tesseract_dir_path, overwrite)

    # Fuse OCR outputs
    if provider is None and additional_context is None:
        fuser = None
    else:
        fuser = get_eng_ocr_fuser(
            provider=provider,
            additional_context=additional_context,
        )
    if fuser is None:

        def fuse_builder() -> Series:
            """Build fused English OCR output."""
            return get_eng_ocr_fused(lens, tesseract)
    else:

        def fuse_builder() -> Series:
            """Build fused English OCR output with a configured processor."""
            return get_eng_ocr_fused(lens, tesseract, processor=fuser)

    fuse = _get_or_build_series(fuse_path, fuse_builder, overwrite)
    if export_images:
        _save_text_image_series(image_series, fuse, fuse_dir_path, overwrite)

    output_paths = {
        "image": image_dir_path,
        "lens": lens_path,
        "tesseract": tesseract_path,
        "fuse": fuse_path,
    }
    if export_images:
        output_paths.update(
            {
                "lens-images": lens_dir_path,
                "tesseract-images": tesseract_dir_path,
                "fuse-images": fuse_dir_path,
            }
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
        export_images: whether to export OCR outputs as image subtitle directories
        overwrite: whether to overwrite existing workflow outputs
        provider: provider to use for OCR fusion queries
        additional_context: additional context to include in OCR fusion prompts
    Returns:
        OCR processing result
    """
    infile_path = _resolve_input_path(infile_path)
    output_dir_path = output_dir_path.resolve()
    output_dir_path.mkdir(parents=True, exist_ok=True)

    image_series = _load_image_series(infile_path, stream_index, cache_dir_path)
    image_dir_path = output_dir_path / "image"
    _save_image_series(image_series, image_dir_path, overwrite)

    # Process OCR outputs
    lens_path = output_dir_path / "lens.srt"
    lens_dir_path = output_dir_path / "lens"
    paddle_path = output_dir_path / "paddle.srt"
    paddle_dir_path = output_dir_path / "paddle"
    fuse_path = output_dir_path / "fuse.srt"
    fuse_dir_path = output_dir_path / "fuse"

    def lens_builder() -> Series:
        """Build Chinese Google Lens OCR output."""
        return ocr_image_series_with_lens(image_series, language="zh-CN")

    def paddle_builder() -> Series:
        """Build Chinese PaddleOCR output."""
        return ocr_image_series_with_paddle(image_series, language="ch")

    lens = _get_or_build_series(lens_path, lens_builder, overwrite)
    if export_images:
        _save_text_image_series(image_series, lens, lens_dir_path, overwrite)
    paddle = _get_or_build_series(paddle_path, paddle_builder, overwrite)
    if export_images:
        _save_text_image_series(image_series, paddle, paddle_dir_path, overwrite)

    # Fuse OCR outputs
    if provider is None and additional_context is None:
        fuser = None
    else:
        fuser = get_zho_ocr_fuser(
            provider=provider,
            additional_context=additional_context,
        )
    if fuser is None:

        def fuse_builder() -> Series:
            """Build fused Chinese OCR output."""
            return get_zho_ocr_fused(lens, paddle)
    else:

        def fuse_builder() -> Series:
            """Build fused Chinese OCR output with a configured processor."""
            return get_zho_ocr_fused(lens, paddle, processor=fuser)

    fuse = _get_or_build_series(fuse_path, fuse_builder, overwrite)
    if export_images:
        _save_text_image_series(image_series, fuse, fuse_dir_path, overwrite)

    output_paths = {
        "image": image_dir_path,
        "lens": lens_path,
        "paddle": paddle_path,
        "fuse": fuse_path,
    }
    if export_images:
        output_paths.update(
            {
                "lens-images": lens_dir_path,
                "paddle-images": paddle_dir_path,
                "fuse-images": fuse_dir_path,
            }
        )

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
        raise ScinoephileError("--stream-index is required for media OCR input")

    for stream in get_subtitle_streams(infile_path):
        if stream.index == stream_index:
            if stream.extension != "sup":
                raise ScinoephileError(
                    f"Subtitle stream {stream_index} is not an image-based SUP stream"
                )
            return stream
    raise ScinoephileError(f"No subtitle stream {stream_index} found in {infile_path}")


def _get_or_build_series(
    outfile_path: Path,
    builder: Callable[[], Series],
    overwrite: bool,
) -> Series:
    """Load an existing series or build and save it.

    Arguments:
        outfile_path: output subtitle path
        builder: function that builds the subtitle series
        overwrite: whether to overwrite existing outputs
    Returns:
        loaded or built subtitle series
    """
    if outfile_path.exists() and not overwrite:
        logger.info(f"Loaded existing OCR output: {outfile_path}")
        return Series.load(outfile_path)

    series = builder()
    series.save(outfile_path, format_="srt")
    return series


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
    cache_subtitles(
        infile_path,
        [stream],
        cache_dir_path=cache_dir_path,
    )
    stream_path = get_subtitle_cache_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    return ImageSeries.load(stream_path)


def _resolve_input_path(infile_path: Path) -> Path:
    """Resolve and validate an OCR workflow input path.

    Arguments:
        infile_path: input path
    Returns:
        resolved input path
    """
    resolved_path = infile_path.resolve()
    if not resolved_path.exists():
        raise FileNotFoundError(resolved_path)
    return resolved_path


def _save_image_series(
    image_series: ImageSeries,
    output_dir_path: Path,
    overwrite: bool,
):
    """Save image subtitle series when needed.

    Arguments:
        image_series: image subtitle series
        output_dir_path: output directory path
        overwrite: whether to overwrite existing image output
    """
    if output_dir_path.exists() and not overwrite:
        logger.info(f"Loaded existing image subtitle output: {output_dir_path}")
        return

    try:
        image_series.save(output_dir_path)
    except (DirectoryNotFoundError, FileNotFoundError, NotADirectoryError) as exc:
        raise ScinoephileError(
            f"Could not save image subtitle output to {output_dir_path}"
        ) from exc


def _save_text_image_series(
    image_series: ImageSeries,
    text_series: Series,
    output_dir_path: Path,
    overwrite: bool,
):
    """Save OCR text overlaid beneath subtitle images as HTML image subtitles.

    Arguments:
        image_series: source image subtitle series
        text_series: OCR text subtitle series
        output_dir_path: output directory path
        overwrite: whether to overwrite existing image output
    """
    if output_dir_path.exists() and not overwrite:
        logger.info(f"Loaded existing OCR HTML output: {output_dir_path}")
        return
    if len(image_series) != len(text_series):
        raise ScinoephileError(
            f"Cannot save OCR HTML output with length mismatch: "
            f"{len(image_series)} images vs {len(text_series)} text subtitles"
        )

    events = []
    for raw_image_subtitle, text_subtitle in zip(image_series, text_series):
        image_subtitle = cast(ImageSubtitle, raw_image_subtitle)
        events.append(
            ImageSubtitle(
                start=image_subtitle.start,
                end=image_subtitle.end,
                img=image_subtitle.img.copy(),
                bboxes=image_subtitle.bboxes,
                text=text_subtitle.text,
            )
        )
    ImageSeries(events=events).save(output_dir_path)
