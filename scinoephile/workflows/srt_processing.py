#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for processing source text SRT subtitles end to end."""

from __future__ import annotations

from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Any

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.core.timing import get_series_timewarped
from scinoephile.lang.eng.block_review import (
    get_eng_block_reviewed,
    get_eng_block_reviewer,
)
from scinoephile.lang.eng.cleaning import get_eng_cleaned
from scinoephile.lang.eng.flattening import get_eng_flattened
from scinoephile.lang.yue.romanization import get_yue_romanized
from scinoephile.lang.zho.block_review import (
    BlockReviewPromptZhoHans,
    BlockReviewPromptZhoHant,
    get_zho_block_reviewed,
    get_zho_reviewer,
)
from scinoephile.lang.zho.cleaning import get_zho_cleaned
from scinoephile.lang.zho.flattening import get_zho_flattened
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_converted

__all__ = [
    "SrtProcessingResult",
    "SrtProcessingWorkflow",
]

logger = getLogger(__name__)


@dataclass(frozen=True)
class SrtProcessingResult:
    """Result of an SRT processing workflow run."""

    infile_path: Path
    """Input SRT path processed by the workflow."""
    output_dir_path: Path
    """Directory containing workflow outputs."""
    output_paths: dict[str, Path]
    """Output paths keyed by output name."""


class SrtProcessingWorkflow:
    """Workflow for processing source text SRT subtitles end to end."""

    def __init__(
        self,
        infile_path: Path,
        reference: Series | Path,
        output_dir_path: Path,
        *,
        language: Language,
        one_start_idx: int | None = None,
        one_end_idx: int | None = None,
        two_start_idx: int | None = None,
        two_end_idx: int | None = None,
        overwrite: bool = False,
        provider: LLMProvider | None = None,
        additional_context: str | None = None,
        reviewer_kw: dict[str, Any] | None = None,
    ):
        """Initialize.

        Arguments:
            infile_path: source SRT input path
            reference: anchor subtitle series or SRT path for timewarping
            output_dir_path: directory where workflow outputs are written
            language: SRT text language to process
            one_start_idx: 1-based start index in the anchor series
            one_end_idx: 1-based end index in the anchor series
            two_start_idx: 1-based start index in the source series
            two_end_idx: 1-based end index in the source series
            overwrite: whether to overwrite existing workflow outputs
            provider: provider to use for block review queries
            additional_context: additional context to include in review prompts
            reviewer_kw: keyword arguments for block reviewer construction
        """
        self.infile_path = infile_path
        self.reference = reference
        self.output_dir_path = output_dir_path
        self.language = language
        self.one_start_idx = one_start_idx
        self.one_end_idx = one_end_idx
        self.two_start_idx = two_start_idx
        self.two_end_idx = two_end_idx
        self.overwrite = overwrite
        self.provider = provider
        self.additional_context = additional_context
        if reviewer_kw is None:
            self.reviewer_kw: dict[str, Any] = {}
        else:
            self.reviewer_kw = dict(reviewer_kw)
        self.output_paths: dict[str, Path] = {}

    def __call__(self) -> SrtProcessingResult:
        """Run SRT processing workflow.

        Returns:
            SRT processing result
        """
        if self.language not in (
            Language.eng,
            Language.yue_hans,
            Language.yue_hant,
        ):
            raise ScinoephileError(
                "SRT processing only supports eng, yue-Hans, and yue-Hant"
            )

        # Load inputs
        source = Series.load(self.infile_path)
        if isinstance(self.reference, Series):
            reference = self.reference
        else:
            reference = Series.load(self.reference)

        # Review, timewarp, clean, and flatten
        review = self._review(source)
        timewarp = self._timewarp(review, reference)
        clean = self._clean(timewarp)
        flatten = self._flatten(clean)

        # English is complete at this point
        if self.language is Language.eng:
            return SrtProcessingResult(
                infile_path=self.infile_path,
                output_dir_path=self.output_dir_path,
                output_paths=self.output_paths,
            )

        # Yue-Hans needs to be romanized
        if self.language is Language.yue_hans:
            self._romanize(flatten)
            return SrtProcessingResult(
                infile_path=self.infile_path,
                output_dir_path=self.output_dir_path,
                output_paths=self.output_paths,
            )

        # Yue-Hant needs to be simplified, review, and then romanized
        simplify = self._simplify(flatten)
        simplify_review = self._review(
            simplify,
            prompt_cls=BlockReviewPromptZhoHans,
            output_name="review_timewarp_clean_flatten_simplify_review",
            test_case_name="simplify_block_review.json",
            log_label=(
                "Reviewed timewarped cleaned flattened simplified reviewed SRT output"
            ),
        )
        self._romanize(
            simplify_review,
            output_name="review_timewarp_clean_flatten_simplify_review_romanize",
            log_label=(
                "Reviewed timewarped cleaned flattened simplified reviewed romanized "
                "SRT output"
            ),
        )
        return SrtProcessingResult(
            infile_path=self.infile_path,
            output_dir_path=self.output_dir_path,
            output_paths=self.output_paths,
        )

    def _clean(self, series: Series) -> Series:
        """Load or create reviewed, timewarped, cleaned output.

        Arguments:
            series: reviewed, timewarped subtitle series
        Returns:
            reviewed, timewarped, cleaned subtitle series
        """
        clean_path = self.output_dir_path / "review_timewarp_clean.srt"
        if clean_path.exists() and not self.overwrite:
            logger.info(f"Reviewed timewarped cleaned SRT output exists: {clean_path}")
            clean = Series.load(clean_path)
        else:
            if self.language is Language.eng:
                clean = get_eng_cleaned(series)
            else:
                clean = get_zho_cleaned(series)
            clean.save(clean_path, format_="srt")
        self.output_paths["review_timewarp_clean"] = clean_path
        return clean

    def _flatten(self, series: Series) -> Series:
        """Load or create reviewed, timewarped, cleaned, flattened output.

        Arguments:
            series: reviewed, timewarped, cleaned subtitle series
        Returns:
            reviewed, timewarped, cleaned, flattened subtitle series
        """
        flatten_path = self.output_dir_path / "review_timewarp_clean_flatten.srt"
        if flatten_path.exists() and not self.overwrite:
            logger.info(
                f"Reviewed timewarped cleaned flattened SRT output exists: "
                f"{flatten_path}"
            )
            flatten = Series.load(flatten_path)
        else:
            if self.language is Language.eng:
                flatten = get_eng_flattened(series)
            else:
                flatten = get_zho_flattened(series)
            flatten.save(flatten_path, format_="srt")
        self.output_paths["review_timewarp_clean_flatten"] = flatten_path
        return flatten

    def _review(
        self,
        series: Series,
        *,
        prompt_cls: type[BlockReviewPromptZhoHans] | None = None,
        output_name: str = "review",
        test_case_name: str = "block_review.json",
        log_label: str = "Reviewed SRT output",
    ) -> Series:
        """Load or create reviewed output.

        Arguments:
            series: source subtitle series
            prompt_cls: Yue review prompt class
            output_name: output filename stem and output_paths key
            test_case_name: review test case JSON filename
            log_label: human-readable output label for logging
        Returns:
            reviewed subtitle series
        """
        review_path = self.output_dir_path / f"{output_name}.srt"
        if review_path.exists() and not self.overwrite:
            logger.info(f"{log_label} exists: {review_path}")
            review = Series.load(review_path)
        else:
            reviewer_kw = dict(self.reviewer_kw)
            reviewer_kw["auto_verify"] = True
            reviewer_kw.setdefault("additional_context", self.additional_context)
            if self.language is Language.eng:
                reviewer = get_eng_block_reviewer(
                    test_case_path=self.output_dir_path
                    / "lang"
                    / "eng"
                    / "block_review.json",
                    provider=self.provider,
                    **reviewer_kw,
                )
                review = get_eng_block_reviewed(series, reviewer)
            else:
                if prompt_cls is None:
                    if self.language is Language.yue_hant:
                        prompt_cls = BlockReviewPromptZhoHant
                    else:
                        prompt_cls = BlockReviewPromptZhoHans

                reviewer = get_zho_reviewer(
                    prompt_cls=prompt_cls,
                    test_case_path=(
                        self.output_dir_path / "lang" / "yue" / test_case_name
                    ),
                    provider=self.provider,
                    **reviewer_kw,
                )
                review = get_zho_block_reviewed(series, processor=reviewer)
            review.save(review_path, format_="srt")
        self.output_paths[output_name] = review_path
        return review

    def _romanize(
        self,
        series: Series,
        *,
        output_name: str = "review_timewarp_clean_flatten_romanize",
        log_label: str = "Reviewed timewarped cleaned flattened romanized SRT output",
    ) -> Series:
        """Load or create romanized output.

        Arguments:
            series: subtitle series to romanize
            output_name: output filename stem and output_paths key
            log_label: human-readable output label for logging
        Returns:
            romanized subtitle series
        """
        romanize_path = self.output_dir_path / f"{output_name}.srt"
        if romanize_path.exists() and not self.overwrite:
            logger.info(f"{log_label} exists: {romanize_path}")
            romanize = Series.load(romanize_path)
        else:
            romanize = get_yue_romanized(series, append=True)
            romanize.save(romanize_path, format_="srt")
        self.output_paths[output_name] = romanize_path
        return romanize

    def _simplify(self, series: Series) -> Series:
        """Load or create simplified output from traditional Yue.

        Arguments:
            series: traditional Yue subtitle series
        Returns:
            simplified subtitle series
        """
        simplify_path = (
            self.output_dir_path / "review_timewarp_clean_flatten_simplify.srt"
        )
        if simplify_path.exists() and not self.overwrite:
            logger.info(
                f"Reviewed timewarped cleaned flattened simplified SRT output exists: "
                f"{simplify_path}"
            )
            simplify = Series.load(simplify_path)
        else:
            simplify = get_zho_converted(series, OpenCCConfig.t2s)
            simplify.save(simplify_path, format_="srt")
        self.output_paths["review_timewarp_clean_flatten_simplify"] = simplify_path
        return simplify

    def _timewarp(self, series: Series, reference: Series) -> Series:
        """Load or create reviewed, timewarped output.

        Arguments:
            series: reviewed source subtitle series
            reference: anchor subtitle series
        Returns:
            reviewed, timewarped subtitle series
        """
        timewarp_path = self.output_dir_path / "review_timewarp.srt"
        if timewarp_path.exists() and not self.overwrite:
            logger.info(f"Reviewed timewarped SRT output exists: {timewarp_path}")
            timewarp = Series.load(timewarp_path)
        else:
            timewarp = get_series_timewarped(
                reference,
                series,
                one_start_idx=self.one_start_idx,
                one_end_idx=self.one_end_idx,
                two_start_idx=self.two_start_idx,
                two_end_idx=self.two_end_idx,
            )
            timewarp.save(timewarp_path, format_="srt")
        self.output_paths["review_timewarp"] = timewarp_path
        return timewarp
