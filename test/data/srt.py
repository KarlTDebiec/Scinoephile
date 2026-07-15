#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Functions for processing source text SRT subtitles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.workflows.srt_processing import SrtProcessingWorkflow

__all__ = [
    "process_srt",
]


def process_srt(
    title_root_path: Path,
    language: Language,
    reference_path: Path,
    *,
    infile_path: Path | None = None,
    output_dir_path: Path | None = None,
    one_start_idx: int | None = None,
    one_end_idx: int | None = None,
    two_start_idx: int | None = None,
    two_end_idx: int | None = None,
    overwrite: bool = False,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    reviewer_kw: dict[str, Any] | None = None,
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
        overwrite: whether to overwrite existing outputs
        provider: provider to use for review queries
        additional_context: additional context to include in review prompts
        reviewer_kw: keyword arguments for reviewer construction
    Returns:
        processed series
    """
    if infile_path is None:
        infile_path = title_root_path / "input" / f"{language.code}.srt"
    if output_dir_path is None:
        output_dir_path = title_root_path / "output" / language.code

    result = SrtProcessingWorkflow(
        infile_path,
        reference_path,
        output_dir_path,
        language=language,
        one_start_idx=one_start_idx,
        one_end_idx=one_end_idx,
        two_start_idx=two_start_idx,
        two_end_idx=two_end_idx,
        overwrite=overwrite,
        provider=provider,
        additional_context=additional_context,
        reviewer_kw=reviewer_kw,
    )()
    return Series.load(result.output_paths["clean_review_flatten_timewarp"])
