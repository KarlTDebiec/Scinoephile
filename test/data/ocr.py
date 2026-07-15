#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Functions for processing OCRed subtitles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_converted
from scinoephile.workflows.flatten import flatten
from scinoephile.workflows.ocr_processing import OcrProcessingWorkflow
from scinoephile.workflows.review import review
from scinoephile.workflows.romanize import romanize

__all__ = [
    "process_ocr",
]


def process_ocr(
    title_root_path: Path,
    language: Language,
    sup_path: Path | None = None,
    *,
    fuser_kw: dict[str, Any] | None = None,
    reviewer_kw: dict[str, Any] | None = None,
    overwrite: bool = False,
    interactive: bool = False,
    host: str = "127.0.0.1",
    port: int = 5000,
) -> Series:
    """Process OCR subtitles through validation, review, and flattening.

    Arguments:
        title_root_path: title root directory
        language: OCR language
        sup_path: subtitle image input path
        fuser_kw: keyword arguments for OCR fuser
        reviewer_kw: keyword arguments for OCR reviewer
        overwrite: whether to overwrite existing outputs
        interactive: whether to launch the OCR validation web UI
        host: OCR validation web UI host
        port: OCR validation web UI port
    Returns:
        processed series
    """
    # Validate and configure
    input_dir_path = title_root_path / "input" / f"{language.code}_ocr"
    output_dir_path = title_root_path / "output" / f"{language.code}_ocr"

    # Load, OCR, and validate series
    validated = _ocr(
        input_dir_path,
        output_dir_path,
        language,
        sup_path=sup_path,
        fuser_kw=fuser_kw,
        interactive=interactive,
        host=host,
        port=port,
        overwrite=overwrite,
    )

    # Review series
    reviewed_path = output_dir_path / "fuse_clean_validate_review.srt"
    reviewed = _review(validated, reviewed_path, language, overwrite, reviewer_kw)

    # Flatten series
    flattened_path = output_dir_path / "fuse_clean_validate_review_flatten.srt"
    flattened = _flatten(reviewed, flattened_path, language, overwrite)

    if language.script == "Hans":
        romanized_path = (
            output_dir_path / "fuse_clean_validate_review_flatten_romanize.srt"
        )
        _romanize(flattened, romanized_path, language, overwrite)
    elif language.script == "Hant":
        if language is Language.yue_hant:
            simplified_language = Language.yue_hans
        else:
            simplified_language = Language.zho_hans
        simplified_path = (
            output_dir_path / "fuse_clean_validate_review_flatten_simplify.srt"
        )
        simplified = _simplify(flattened, simplified_path, overwrite)
        simplified_reviewed_path = (
            output_dir_path / "fuse_clean_validate_review_flatten_simplify_review.srt"
        )
        simplify_reviewer_kw = dict(reviewer_kw or {})
        simplify_reviewer_kw.pop("prompt", None)
        simplify_reviewer_kw.pop("reviewer", None)
        simplify_reviewer_kw.pop("test_cases", None)
        simplify_reviewer_kw["test_case_path"] = (
            output_dir_path / "lang" / language.language / "simplify_review.json"
        )
        simplified_reviewed = _review(
            simplified,
            simplified_reviewed_path,
            simplified_language,
            overwrite,
            simplify_reviewer_kw,
        )
        romanized_path = (
            output_dir_path
            / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
        )
        _romanize(simplified_reviewed, romanized_path, simplified_language, overwrite)

    return flattened


def _flatten(
    series: Series,
    output_path: Path,
    language: Language,
    overwrite: bool = False,
) -> Series:
    """Load or create flattened OCR subtitles.

    Arguments:
        series: series to flatten
        output_path: flattened subtitle output path
        language: OCR language
        overwrite: whether to overwrite existing outputs
    Returns:
        flattened series
    """
    # Load file if it exists
    if output_path.exists() and not overwrite:
        return Series.load(output_path)

    # Run and save
    flattened = flatten(series, language=language)
    flattened.save(output_path, exist_ok=True)
    return flattened


def _ocr(
    input_dir_path: Path,
    output_dir_path: Path,
    language: Language,
    *,
    sup_path: Path | None,
    fuser_kw: dict[str, Any] | None,
    interactive: bool,
    host: str,
    port: int,
    overwrite: bool,
) -> Series:
    """Load or create validated OCR subtitles.

    Arguments:
        input_dir_path: title input OCR directory
        output_dir_path: title output OCR directory
        language: OCR language
        sup_path: subtitle image input path
        fuser_kw: keyword arguments for OCR fuser
        interactive: whether to launch the OCR validation web UI
        host: OCR validation web UI host
        port: OCR validation web UI port
        overwrite: whether to overwrite existing outputs
    Returns:
        validated series
    """
    # Resolve infile
    infile_path = output_dir_path / "image"
    if not infile_path.exists():
        infile_path = sup_path or input_dir_path / "source.sup"
    if not infile_path.exists():
        raise ScinoephileError("Could not resolve infile path")

    # Prepare kwargs
    fuser_kw = dict(fuser_kw or {})
    fuser_kw.setdefault(
        "test_case_path",
        output_dir_path / "lang" / language.language / "ocr_fusion.json",
    )
    fuser_kw.setdefault("auto_verify", True)
    # Run workflow
    OcrProcessingWorkflow(
        infile_path,
        output_dir_path,
        language=language,
        clean=True,
        dev=True,
        interactive=interactive,
        host=host,
        port=port,
        overwrite=overwrite,
        fuser_kw=fuser_kw,
    )()

    # Load final result and copy validated text back into image cache
    validated = Series.load(output_dir_path / "fuse_clean_validate.srt")
    image_dir_path = output_dir_path / "image"
    if image_dir_path.exists():
        image_series = ImageSeries.load(image_dir_path, encoding="utf-8")
        image_texts = [subtitle.text for subtitle in image_series]
        validated_texts = [subtitle.text for subtitle in validated]
        if image_texts != validated_texts:
            image_series.copy_text_from(validated)
            image_series.save_html_index(image_dir_path, encoding="utf-8")
    return validated


def _review(
    series: Series,
    output_path: Path,
    language: Language,
    overwrite: bool = False,
    reviewer_kw: dict[str, Any] | None = None,
) -> Series:
    """Load or create reviewed OCR subtitles.

    Arguments:
        series: series to review
        output_path: reviewed subtitle output path
        language: OCR language
        overwrite: whether to overwrite existing outputs
        reviewer_kw: keyword arguments for OCR reviewer
    Returns:
        reviewed series
    """
    # Load file if it exists
    if output_path.exists() and not overwrite:
        return Series.load(output_path)

    # Prepare kwargs
    reviewer_kw = dict(reviewer_kw or {})
    reviewer_kw.setdefault(
        "test_case_path",
        output_path.parent / "lang" / language.language / "review.json",
    )
    reviewer_kw.setdefault("auto_verify", True)

    # Run and save
    reviewed = review(series, language=language, **reviewer_kw)
    reviewed.save(output_path)
    return reviewed


def _romanize(
    series: Series,
    output_path: Path,
    language: Language,
    overwrite: bool = False,
) -> Series:
    """Load or create romanized OCR subtitles.

    Arguments:
        series: series to romanize
        output_path: romanized subtitle output path
        language: OCR language
        overwrite: whether to overwrite existing outputs
    Returns:
        romanized series
    """
    # Load file if it exists
    if output_path.exists() and not overwrite:
        return Series.load(output_path)

    # Run and save
    romanized = romanize(series, language=language, append=True)
    romanized.save(output_path, exist_ok=True)
    return romanized


def _simplify(
    series: Series,
    output_path: Path,
    overwrite: bool = False,
) -> Series:
    """Load or create simplified Chinese-script OCR subtitles.

    Arguments:
        series: series to simplify
        output_path: simplified subtitle output path
        overwrite: whether to overwrite existing outputs
    Returns:
        simplified series
    """
    # Load file if it exists
    if output_path.exists() and not overwrite:
        return Series.load(output_path)

    # Run and save
    simplified = get_zho_converted(series, OpenCCConfig.t2s)
    simplified.save(output_path, exist_ok=True)
    return simplified
