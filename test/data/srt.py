#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Functions for processing source text SRT subtitles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series

from .helpers import (
    load_or_clean_series,
    load_or_flatten_series,
    load_or_review_series,
    load_or_romanize_series,
    load_or_simplify_series,
    load_or_timewarp_series,
)

__all__ = [
    "process_srt",
]


def process_srt(
    title_root_path: Path,
    language: Language,
    *,
    reference_path: Path,
    infile_path: Path | None = None,
    output_dir_path: Path | None = None,
    one_start_idx: int | None = None,
    one_end_idx: int | None = None,
    two_start_idx: int | None = None,
    two_end_idx: int | None = None,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    reviewer_kw: dict[str, Any] | None = None,
    overwrite: bool = False,
) -> Series:
    """Process source text SRT subtitles through review, timewarp, and cleanup.

    Arguments:
        title_root_path: title root directory
        language: source text SRT language
        reference_path: anchor subtitle path for timewarping
        infile_path: source SRT path; defaults to `input/{language.code}.srt`
        output_dir_path: output directory; defaults to `output/{language.code}`
        one_start_idx: 1-based start index in the anchor series
        one_end_idx: 1-based end index in the anchor series
        two_start_idx: 1-based start index in the source series
        two_end_idx: 1-based end index in the source series
        provider: provider to use for review queries
        additional_context: additional context to include in review prompts
        reviewer_kw: keyword arguments for reviewer construction
        overwrite: whether to overwrite existing outputs
    Returns:
        processed series
    Raises:
        ScinoephileError: if the language is unsupported
    """
    if language not in (
        Language.eng,
        Language.yue_hans,
        Language.yue_hant,
    ):
        raise ScinoephileError(
            "SRT processing only supports eng, yue-Hans, and yue-Hant"
        )

    # Resolve inputs and output directory
    if infile_path is None:
        infile_path = title_root_path / "input" / f"{language.code}.srt"
    if output_dir_path is None:
        output_dir_path = title_root_path / "output" / language.code
    source = Series.load(infile_path)
    reference = Series.load(reference_path)

    # Prepare shared review configuration
    reviewer_kw = dict(reviewer_kw or {})
    if provider is not None:
        reviewer_kw.setdefault("provider", provider)
    if additional_context is not None:
        reviewer_kw.setdefault("additional_context", additional_context)

    # Clean, review, flatten, and timewarp
    cleaned_path = output_dir_path / "clean.srt"
    cleaned = load_or_clean_series(source, cleaned_path, language, overwrite)

    reviewed_path = output_dir_path / "clean_review.srt"
    reviewed = load_or_review_series(
        cleaned,
        reviewed_path,
        language,
        overwrite,
        reviewer_kw,
    )

    flattened_path = output_dir_path / "clean_review_flatten.srt"
    flattened = load_or_flatten_series(
        reviewed,
        flattened_path,
        language,
        overwrite,
    )

    timewarped_path = output_dir_path / "clean_review_flatten_timewarp.srt"
    timewarped = load_or_timewarp_series(
        flattened,
        reference,
        timewarped_path,
        one_start_idx=one_start_idx,
        one_end_idx=one_end_idx,
        two_start_idx=two_start_idx,
        two_end_idx=two_end_idx,
        overwrite=overwrite,
    )

    # Create derived Chinese-script outputs
    if language is Language.yue_hans:
        romanized_path = output_dir_path / "clean_review_flatten_timewarp_romanize.srt"
        load_or_romanize_series(timewarped, romanized_path, language, overwrite)
    elif language is Language.yue_hant:
        simplified_path = output_dir_path / "clean_review_flatten_timewarp_simplify.srt"
        simplified = load_or_simplify_series(timewarped, simplified_path, overwrite)

        simplified_reviewed_path = (
            output_dir_path / "clean_review_flatten_timewarp_simplify_review.srt"
        )
        simplify_reviewer_kw = dict(reviewer_kw)
        simplify_reviewer_kw.pop("prompt", None)
        simplify_reviewer_kw.pop("reviewer", None)
        simplify_reviewer_kw.pop("test_cases", None)
        simplify_reviewer_kw["test_case_path"] = (
            output_dir_path / "lang" / "yue" / "simplify_review.json"
        )
        simplified_reviewed = load_or_review_series(
            simplified,
            simplified_reviewed_path,
            Language.yue_hans,
            overwrite,
            simplify_reviewer_kw,
        )

        romanized_path = (
            output_dir_path
            / "clean_review_flatten_timewarp_simplify_review_romanize.srt"
        )
        load_or_romanize_series(
            simplified_reviewed,
            romanized_path,
            Language.yue_hans,
            overwrite,
        )

    return timewarped
