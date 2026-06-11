#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Functions for processing OCRed subtitles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.lang.cmn.romanization import get_cmn_romanized
from scinoephile.lang.eng.block_review import (
    get_eng_block_reviewed,
    get_eng_block_reviewer,
)
from scinoephile.lang.eng.flattening import get_eng_flattened
from scinoephile.lang.yue.romanization import get_yue_romanized
from scinoephile.lang.zho.block_review import (
    BlockReviewPromptZhoHans,
    BlockReviewPromptZhoHant,
    get_zho_block_reviewed,
    get_zho_reviewer,
)
from scinoephile.lang.zho.flattening import get_zho_flattened
from scinoephile.lang.zho.ocr_fusion import OcrFusionPromptZhoHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_converted
from scinoephile.workflows.ocr_processing import OcrProcessingWorkflow

__all__ = [
    "process_eng_ocr",
    "process_yue_hans_ocr",
    "process_yue_hant_ocr",
    "process_zho_hans_ocr",
    "process_zho_hant_ocr",
]


def process_eng_ocr(
    title_root_path: Path,
    sup_path: Path | None = None,
    **kwargs: Any,
) -> Series:
    """Process eng OCR subtitles into validated output.

    Arguments:
        title_root_path: title root directory
        sup_path: subtitle image input path
        kwargs: keyword arguments for OCR processing
    Returns:
        processed series
    """
    return _process_ocr(title_root_path, "eng", sup_path=sup_path, **kwargs)


def process_yue_hans_ocr(
    title_root_path: Path,
    sup_path: Path | None = None,
    **kwargs: Any,
) -> Series:
    """Process yue-Hans OCR subtitles into validated output.

    Arguments:
        title_root_path: title root directory
        sup_path: subtitle image input path
        kwargs: keyword arguments for OCR processing
    Returns:
        processed series
    """
    return _process_ocr(title_root_path, "yue-Hans", sup_path=sup_path, **kwargs)


def process_yue_hant_ocr(
    title_root_path: Path,
    sup_path: Path | None = None,
    **kwargs: Any,
) -> Series:
    """Process yue-Hant OCR subtitles into validated output.

    Arguments:
        title_root_path: title root directory
        sup_path: subtitle image input path
        kwargs: keyword arguments for OCR processing
    Returns:
        processed series
    """
    return _process_ocr(title_root_path, "yue-Hant", sup_path=sup_path, **kwargs)


def process_zho_hans_ocr(
    title_root_path: Path,
    sup_path: Path | None = None,
    **kwargs: Any,
) -> Series:
    """Process zho-Hans OCR subtitles into validated output.

    Arguments:
        title_root_path: title root directory
        sup_path: subtitle image input path
        kwargs: keyword arguments for OCR processing
    Returns:
        processed series
    """
    return _process_ocr(title_root_path, "zho-Hans", sup_path=sup_path, **kwargs)


def process_zho_hant_ocr(
    title_root_path: Path,
    sup_path: Path | None = None,
    **kwargs: Any,
) -> Series:
    """Process zho-Hant OCR subtitles into validated output.

    Arguments:
        title_root_path: title root directory
        sup_path: subtitle image input path
        kwargs: keyword arguments for OCR processing
    Returns:
        processed series
    """
    return _process_ocr(title_root_path, "zho-Hant", sup_path=sup_path, **kwargs)


def _flatten(path: Path, lang: str, series: Series, overwrite: bool) -> Series:
    """Load or create flattened OCR subtitles.

    Arguments:
        path: flattened subtitle output path
        lang: language tag
        series: reviewed OCR series
        overwrite: whether to overwrite existing outputs
    Returns:
        flattened series
    """
    # Load file if it exists
    if path.exists() and not overwrite:
        return Series.load(path)

    # Run and save
    if lang == "eng":
        flatten = get_eng_flattened(series)
    else:
        flatten = get_zho_flattened(series)
    flatten.save(path, exist_ok=True)
    return flatten


def _ocr(
    input_dir_path: Path,
    output_dir_path: Path,
    lang: str,
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
        lang: language tag
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
        output_dir_path / "lang" / lang[:3] / "ocr_fusion.json",
    )
    if lang.endswith("-Hant"):
        fuser_kw.setdefault("prompt_cls", OcrFusionPromptZhoHant)
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
    if lang == "eng":
        language = Language.eng
    elif lang.endswith("-Hans"):
        language = Language.zho_hans
    else:
        language = Language.zho_hant
    OcrProcessingWorkflow(language=language, **workflow_kw)()

    # Load and return final result
    return Series.load(output_dir_path / "fuse_clean_validate.srt")


def _process_ocr(
    title_root_path: Path,
    lang: str,
    *,
    sup_path: Path | None = None,
    fuser_kw: Any | None = None,
    reviewer_kw: Any | None = None,
    overwrite: bool = False,
    overwrite_srt: bool = False,
    overwrite_img: bool = False,
    force_validation: bool = False,
    interactive: bool = False,
    host: str = "127.0.0.1",
    port: int = 5000,
) -> Series:
    """Process OCR subtitles through validation, review, and flattening.

    Arguments:
        title_root_path: title root directory
        lang: language tag to use in input and output filenames
        sup_path: subtitle image input path
        fuser_kw: keyword arguments for OCR fuser
        reviewer_kw: keyword arguments for OCR block reviewer
        overwrite: whether to overwrite existing outputs
        overwrite_srt: legacy alias for overwriting subtitle outputs
        overwrite_img: legacy alias for overwriting image outputs
        force_validation: legacy alias for overwriting validation output
        interactive: whether to launch the OCR validation web UI
        host: OCR validation web UI host
        port: OCR validation web UI port
    Returns:
        flattened reviewed series
    """
    # Validate and configure
    if lang not in ("eng", "yue-Hans", "yue-Hant", "zho-Hans", "zho-Hant"):
        raise ValueError(
            f"lang must be eng, yue-Hans, yue-Hant, zho-Hans, or zho-Hant, not {lang}"
        )
    input_dir_path = title_root_path / "input" / f"{lang}_ocr"
    output_dir_path = title_root_path / "output" / f"{lang}_ocr"
    overwrite = overwrite or overwrite_srt or overwrite_img or force_validation

    # Load, OCR, and validate series
    validated = _ocr(
        input_dir_path,
        output_dir_path,
        lang,
        sup_path=sup_path,
        fuser_kw=fuser_kw,
        interactive=interactive,
        host=host,
        port=port,
        overwrite=overwrite,
    )

    # Review series
    review_path = output_dir_path / "fuse_clean_validate_review.srt"
    review = _review(review_path, lang, validated, overwrite, reviewer_kw)

    # Flatten series
    flatten_path = output_dir_path / "fuse_clean_validate_review_flatten.srt"
    flatten = _flatten(flatten_path, lang, review, overwrite)

    if lang.endswith("-Hans"):
        romanize_path = (
            output_dir_path / "fuse_clean_validate_review_flatten_romanize.srt"
        )
        _romanize(romanize_path, lang, flatten, overwrite)
    elif lang.endswith("-Hant"):
        simplify_path = (
            output_dir_path / "fuse_clean_validate_review_flatten_simplify.srt"
        )
        simplify = _simplify(simplify_path, flatten, overwrite)
        review_path = (
            output_dir_path / "fuse_clean_validate_review_flatten_simplify_review.srt"
        )
        simplify_reviewer_kw = dict(reviewer_kw or {})
        simplify_reviewer_kw["prompt_cls"] = BlockReviewPromptZhoHans
        simplify_reviewer_kw["test_case_path"] = (
            output_dir_path / "lang" / lang[:3] / "simplify_block_review.json"
        )
        simplify_review = _review(
            review_path,
            lang,
            simplify,
            overwrite,
            simplify_reviewer_kw,
        )
        romanize_path = (
            output_dir_path
            / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
        )
        _romanize(romanize_path, lang, simplify_review, overwrite)

    return flatten


def _review(
    path: Path,
    lang: str,
    series: Series,
    overwrite: bool,
    reviewer_kw: Any | None,
) -> Series:
    """Load or create block-reviewed OCR subtitles.

    Arguments:
        path: reviewed subtitle output path
        lang: language tag
        series: series to review
        overwrite: whether to overwrite existing outputs
        reviewer_kw: keyword arguments for OCR reviewer
    Returns:
        reviewed series
    """
    # Load file if it exists
    if path.exists() and not overwrite:
        return Series.load(path)

    # Prepare kwargs
    reviewer_kw = dict(reviewer_kw or {})
    reviewer_kw.setdefault(
        "test_case_path",
        path.parent / "lang" / lang[:3] / "block_review.json",
    )
    reviewer_kw.setdefault("auto_verify", True)

    # Run and save
    if lang == "eng":
        reviewer = get_eng_block_reviewer(**reviewer_kw)
        review = get_eng_block_reviewed(series, reviewer)
    else:
        if lang.endswith("-Hant"):
            reviewer_kw.setdefault("prompt_cls", BlockReviewPromptZhoHant)
        reviewer = get_zho_reviewer(**reviewer_kw)
        review = get_zho_block_reviewed(series, reviewer)
    review.save(path)
    return review


def _romanize(
    path: Path,
    lang: str,
    series: Series,
    overwrite: bool,
) -> Series:
    """Load or create romanized OCR subtitles.

    Arguments:
        path: romanized subtitle output path
        lang: language tag
        series: series to romanize
        overwrite: whether to overwrite existing outputs
    Returns:
        romanized series
    """
    # Load file if it exists
    if path.exists() and not overwrite:
        return Series.load(path)

    # Run and save
    if lang[:3] == "yue":
        romanized = get_yue_romanized(series, append=True)
    else:
        romanized = get_cmn_romanized(series, append=True)
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
