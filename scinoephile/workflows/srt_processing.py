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
from scinoephile.lang.yue.review import ReviewPromptYueHans, ReviewPromptYueHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_converted
from scinoephile.llms.review import ReviewPrompt

from .cleaning import clean_series
from .flattening import flatten_series
from .review import review_series
from .romanization import romanize_series

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
            provider: provider to use for review queries
            additional_context: additional context to include in review prompts
            reviewer_kw: keyword arguments for reviewer construction
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

        # Clean, review, flatten, and timewarp
        source_clean = self._clean(source)
        review = self._review(source_clean)
        flatten = self._flatten(review)
        timewarp = self._timewarp(flatten, reference)

        # English is complete at this point
        if self.language is Language.eng:
            return SrtProcessingResult(
                infile_path=self.infile_path,
                output_dir_path=self.output_dir_path,
                output_paths=self.output_paths,
            )

        # Yue-Hans needs to be romanized
        if self.language is Language.yue_hans:
            self._romanize(timewarp)
            return SrtProcessingResult(
                infile_path=self.infile_path,
                output_dir_path=self.output_dir_path,
                output_paths=self.output_paths,
            )

        # Yue-Hant needs to be simplified, review, and then romanized
        simplify = self._simplify(timewarp)
        simplify_review = self._review(
            simplify,
            language=Language.yue_hans,
            prompt=ReviewPromptYueHans,
            output_name="clean_review_flatten_timewarp_simplify_review",
            test_case_name="simplify_review.json",
            log_label=(
                "Cleaned reviewed flattened timewarped simplified reviewed SRT output"
            ),
        )
        self._romanize(
            simplify_review,
            output_name="clean_review_flatten_timewarp_simplify_review_romanize",
            log_label=(
                "Cleaned reviewed flattened timewarped simplified reviewed "
                "romanized SRT output"
            ),
        )
        return SrtProcessingResult(
            infile_path=self.infile_path,
            output_dir_path=self.output_dir_path,
            output_paths=self.output_paths,
        )

    def _clean(
        self,
        series: Series,
    ) -> Series:
        """Load or create cleaned output.

        Arguments:
            series: subtitle series to clean
        Returns:
            cleaned subtitle series
        """
        clean_path = self.output_dir_path / "clean.srt"
        if clean_path.exists() and not self.overwrite:
            logger.info(f"Cleaned SRT output exists: {clean_path}")
            clean = Series.load(clean_path)
        else:
            clean = clean_series(series, language=self.language)
            clean.save(clean_path, format_="srt")
        self.output_paths["clean"] = clean_path
        return clean

    def _flatten(self, series: Series) -> Series:
        """Load or create cleaned, reviewed, flattened output.

        Arguments:
            series: cleaned, reviewed subtitle series
        Returns:
            cleaned, reviewed, flattened subtitle series
        """
        flatten_path = self.output_dir_path / "clean_review_flatten.srt"
        if flatten_path.exists() and not self.overwrite:
            logger.info(f"Cleaned reviewed flattened SRT output exists: {flatten_path}")
            flatten = Series.load(flatten_path)
        else:
            flatten = flatten_series(series, language=self.language)
            flatten.save(flatten_path, format_="srt")
        self.output_paths["clean_review_flatten"] = flatten_path
        return flatten

    def _review(
        self,
        series: Series,
        *,
        language: Language | None = None,
        prompt: ReviewPrompt | None = None,
        output_name: str = "clean_review",
        test_case_name: str = "review.json",
        log_label: str = "Cleaned reviewed SRT output",
    ) -> Series:
        """Load or create reviewed output.

        Arguments:
            series: source subtitle series
            language: language to use for review
            prompt: review prompt
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
            review_language = language or self.language
            if review_language is Language.eng:
                test_case_language_dir_name = "eng"
            else:
                if prompt is None:
                    if review_language is Language.yue_hant:
                        prompt = ReviewPromptYueHant
                    else:
                        prompt = ReviewPromptYueHans
                test_case_language_dir_name = "yue"

            review = review_series(
                series,
                language=review_language,
                prompt=prompt,
                test_case_path=(
                    self.output_dir_path
                    / "lang"
                    / test_case_language_dir_name
                    / test_case_name
                ),
                provider=self.provider,
                **reviewer_kw,
            )
            review.save(review_path, format_="srt")
        self.output_paths[output_name] = review_path
        return review

    def _romanize(
        self,
        series: Series,
        *,
        output_name: str = "clean_review_flatten_timewarp_romanize",
        log_label: str = ("Cleaned reviewed flattened timewarped romanized SRT output"),
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
            romanize = romanize_series(
                series,
                language=self.language,
                append=True,
            )
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
            self.output_dir_path / "clean_review_flatten_timewarp_simplify.srt"
        )
        if simplify_path.exists() and not self.overwrite:
            logger.info(
                f"Cleaned reviewed flattened timewarped simplified SRT "
                f"output exists: {simplify_path}"
            )
            simplify = Series.load(simplify_path)
        else:
            simplify = get_zho_converted(series, OpenCCConfig.t2s)
            simplify.save(simplify_path, format_="srt")
        self.output_paths["clean_review_flatten_timewarp_simplify"] = simplify_path
        return simplify

    def _timewarp(self, series: Series, reference: Series) -> Series:
        """Load or create cleaned, reviewed, flattened, timewarped output.

        Arguments:
            series: cleaned, reviewed, flattened source subtitle series
            reference: anchor subtitle series
        Returns:
            cleaned, reviewed, flattened, timewarped subtitle series
        """
        timewarp_path = self.output_dir_path / "clean_review_flatten_timewarp.srt"
        if timewarp_path.exists() and not self.overwrite:
            logger.info(
                f"Cleaned reviewed flattened timewarped SRT output exists: "
                f"{timewarp_path}"
            )
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
        self.output_paths["clean_review_flatten_timewarp"] = timewarp_path
        return timewarp
