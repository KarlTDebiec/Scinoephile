#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Functions for processing OCRed subtitles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.yue.review import ReviewPromptYueHans, ReviewPromptYueHant
from scinoephile.lang.zho.review import ReviewPromptZhoHans, ReviewPromptZhoHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_converted
from scinoephile.workflows.flattening import flatten_series
from scinoephile.workflows.ocr_processing import OcrProcessingWorkflow
from scinoephile.workflows.review import review_series
from scinoephile.workflows.romanization import romanize_series

__all__ = [
    "process_ocr",
]


def process_ocr(
    title_root_path: Path,
    language: Language,
    sup_path: Path | None = None,
    *,
    fuser_kw: Any | None = None,
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
    review_path = output_dir_path / "fuse_clean_validate_review.srt"
    review = _review(validated, language, review_path, overwrite, reviewer_kw)

    # Flatten series
    flatten_path = output_dir_path / "fuse_clean_validate_review_flatten.srt"
    flatten = _flatten(flatten_path, language, review, overwrite)

    if language.script == "Hans":
        romanize_path = (
            output_dir_path / "fuse_clean_validate_review_flatten_romanize.srt"
        )
        _romanize(romanize_path, language, flatten, overwrite)
    elif language.script == "Hant":
        simplify_path = (
            output_dir_path / "fuse_clean_validate_review_flatten_simplify.srt"
        )
        simplify = _simplify(simplify_path, flatten, overwrite)
        review_path = (
            output_dir_path / "fuse_clean_validate_review_flatten_simplify_review.srt"
        )
        simplify_reviewer_kw = dict(reviewer_kw or {})
        if language is Language.yue_hant:
            simplify_reviewer_kw["prompt"] = ReviewPromptYueHans
        else:
            simplify_reviewer_kw["prompt"] = ReviewPromptZhoHans
        simplify_reviewer_kw["test_case_path"] = (
            output_dir_path / "lang" / language.language / "simplify_review.json"
        )
        simplify_review = _review(
            simplify,
            language,
            review_path,
            overwrite,
            simplify_reviewer_kw,
        )
        romanize_path = (
            output_dir_path
            / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
        )
        _romanize(romanize_path, language, simplify_review, overwrite)

    return flatten


def _flatten(
    path: Path,
    language: Language,
    series: Series,
    overwrite: bool,
) -> Series:
    """Load or create flattened OCR subtitles.

    Arguments:
        path: flattened subtitle output path
        language: OCR language
        series: reviewed OCR series
        overwrite: whether to overwrite existing outputs
    Returns:
        flattened series
    """
    # Load file if it exists
    if path.exists() and not overwrite:
        return Series.load(path)

    # Run and save
    flatten = flatten_series(series, language=language)
    flatten.save(path, exist_ok=True)
    return flatten


def _ocr(
    input_dir_path: Path,
    output_dir_path: Path,
    language: Language,
    *,
    sup_path: Path | None,
    fuser_kw: Any | None,
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
    workflow_kw: dict[str, Any] = {
        "infile_path": infile_path,
        "output_dir_path": output_dir_path,
        "clean": True,
        "dev": True,
        "interactive": interactive,
        "host": host,
        "port": port,
        "overwrite": overwrite,
        "fuser_kw": fuser_kw,
    }
    # Run workflow
    OcrProcessingWorkflow(language=language, **workflow_kw)()

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
    input_series: Series,
    language: Language,
    output_path: Path,
    overwrite: bool = False,
    reviewer_kw: dict[str, Any] | None = None,
) -> Series:
    """Load or create guided-reviewed OCR subtitles.

    Arguments:
        input_series: series to review
        language: OCR language
        output_path: reviewed subtitle output path
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
    if language is Language.yue_hant:
        reviewer_kw.setdefault("prompt", ReviewPromptYueHant)
    elif language is Language.zho_hant:
        reviewer_kw.setdefault("prompt", ReviewPromptZhoHant)
    review = review_series(input_series, language=language, **reviewer_kw)
    review.save(output_path)
    return review


def _romanize(
    path: Path,
    language: Language,
    series: Series,
    overwrite: bool,
) -> Series:
    """Load or create romanized OCR subtitles.

    Arguments:
        path: romanized subtitle output path
        language: OCR language
        series: series to romanize
        overwrite: whether to overwrite existing outputs
    Returns:
        romanized series
    """
    # Load file if it exists
    if path.exists() and not overwrite:
        return Series.load(path)

    # Run and save
    romanized = romanize_series(series, language=language, append=True)
    romanized.save(path, exist_ok=True)
    return romanized


def _simplify(
    path: Path,
    series: Series,
    overwrite: bool,
) -> Series:
    """Load or create simplified Chinese-script OCR subtitles.

    Arguments:
        path: simplified subtitle output path
        series: series to simplify
        overwrite: whether to overwrite existing outputs
    Returns:
        simplified series
    """
    # Load file if it exists
    if path.exists() and not overwrite:
        return Series.load(path)

    # Run and save
    simplify = get_zho_converted(series, OpenCCConfig.t2s)
    simplify.save(path, exist_ok=True)
    return simplify
