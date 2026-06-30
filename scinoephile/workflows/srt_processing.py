#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for processing source text SRT subtitles end to end."""

from __future__ import annotations

from collections.abc import Callable
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
        source = self._load_input()
        reference = self._load_reference()

        # Review, timewarp, clean, and flatten
        review = self._review(source)
        timewarp = self._timewarp(review, reference)
        clean = self._clean(timewarp)
        flatten = self._flatten(clean)

        # Romanize written Cantonese outputs
        if self._is_yue:
            if self.language is Language.yue_hans:
                self._romanize(
                    flatten,
                    output_name="review_timewarp_clean_flatten_romanize",
                    log_label=(
                        "Reviewed timewarped cleaned flattened romanized SRT output"
                    ),
                )
            else:
                simplify = self._simplify(flatten)
                simplify_review = self._review(
                    simplify,
                    prompt_cls=BlockReviewPromptZhoHans,
                    output_name="review_timewarp_clean_flatten_simplify_review",
                    test_case_name="simplify_block_review.json",
                    log_label=(
                        "Reviewed timewarped cleaned flattened simplified "
                        "reviewed SRT output"
                    ),
                )
                self._romanize(
                    simplify_review,
                    output_name=(
                        "review_timewarp_clean_flatten_simplify_review_romanize"
                    ),
                    log_label=(
                        "Reviewed timewarped cleaned flattened simplified "
                        "reviewed romanized SRT output"
                    ),
                )

        return SrtProcessingResult(
            infile_path=self.infile_path,
            output_dir_path=self.output_dir_path,
            output_paths=self.output_paths,
        )

    @property
    def _is_yue(self) -> bool:
        """Whether the workflow language is written Cantonese."""
        return self.language in (Language.yue_hans, Language.yue_hant)

    @property
    def _yue_review_prompt_cls(self) -> type[BlockReviewPromptZhoHans]:
        """Block review prompt class for the workflow's Yue language."""
        if self.language is Language.yue_hant:
            return BlockReviewPromptZhoHant
        return BlockReviewPromptZhoHans

    def _clean(self, series: Series) -> Series:
        """Load or create reviewed, timewarped, cleaned output.

        Arguments:
            series: reviewed, timewarped subtitle series
        Returns:
            reviewed, timewarped, cleaned subtitle series
        """

        def create() -> Series:
            """Create cleaned output.

            Returns:
                cleaned subtitle series
            """
            if self.language is Language.eng:
                return get_eng_cleaned(series)
            return get_zho_cleaned(series)

        return self._load_or_create_series(
            "review_timewarp_clean",
            "Reviewed timewarped cleaned SRT output",
            create,
        )

    def _flatten(self, series: Series) -> Series:
        """Load or create reviewed, timewarped, cleaned, flattened output.

        Arguments:
            series: reviewed, timewarped, cleaned subtitle series
        Returns:
            reviewed, timewarped, cleaned, flattened subtitle series
        """

        def create() -> Series:
            """Create flattened output.

            Returns:
                flattened subtitle series
            """
            if self.language is Language.eng:
                return get_eng_flattened(series)
            return get_zho_flattened(series)

        return self._load_or_create_series(
            "review_timewarp_clean_flatten",
            "Reviewed timewarped cleaned flattened SRT output",
            create,
        )

    def _load_input(self) -> Series:
        """Load source SRT input.

        Returns:
            source subtitle series
        """
        return Series.load(self.infile_path)

    def _load_or_create_series(
        self,
        output_name: str,
        log_label: str,
        create: Callable[[], Series],
    ) -> Series:
        """Load an existing step output or create and save it.

        Arguments:
            output_name: output filename stem and output_paths key
            log_label: human-readable output label for logging
            create: callable that creates the output series
        Returns:
            step output subtitle series
        """
        output_path = self.output_dir_path / f"{output_name}.srt"
        if output_path.exists() and not self.overwrite:
            logger.info(f"{log_label} exists: {output_path}")
            series = Series.load(output_path)
        else:
            series = create()
            series.save(output_path, format_="srt")
        self.output_paths[output_name] = output_path
        return series

    def _load_reference(self) -> Series:
        """Load or return the anchor series for timewarping.

        Returns:
            anchor subtitle series
        """
        if isinstance(self.reference, Series):
            return self.reference
        return Series.load(self.reference)

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

        def create() -> Series:
            """Create reviewed output.

            Returns:
                reviewed subtitle series
            """
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
                return get_eng_block_reviewed(series, reviewer)

            selected_prompt_cls = prompt_cls or self._yue_review_prompt_cls
            reviewer = get_zho_reviewer(
                prompt_cls=selected_prompt_cls,
                test_case_path=self.output_dir_path / "lang" / "yue" / test_case_name,
                provider=self.provider,
                **reviewer_kw,
            )
            return get_zho_block_reviewed(series, processor=reviewer)

        return self._load_or_create_series(output_name, log_label, create)

    def _romanize(
        self,
        series: Series,
        *,
        output_name: str,
        log_label: str,
    ) -> Series:
        """Load or create romanized output.

        Arguments:
            series: subtitle series to romanize
            output_name: output filename stem and output_paths key
            log_label: human-readable output label for logging
        Returns:
            romanized subtitle series
        """
        return self._load_or_create_series(
            output_name,
            log_label,
            lambda: get_yue_romanized(series, append=True),
        )

    def _simplify(self, series: Series) -> Series:
        """Load or create simplified output from traditional Yue.

        Arguments:
            series: traditional Yue subtitle series
        Returns:
            simplified subtitle series
        """
        return self._load_or_create_series(
            "review_timewarp_clean_flatten_simplify",
            "Reviewed timewarped cleaned flattened simplified SRT output",
            lambda: get_zho_converted(series, OpenCCConfig.t2s),
        )

    def _timewarp(self, series: Series, reference: Series) -> Series:
        """Load or create reviewed, timewarped output.

        Arguments:
            series: reviewed source subtitle series
            reference: anchor subtitle series
        Returns:
            reviewed, timewarped subtitle series
        """
        return self._load_or_create_series(
            "review_timewarp",
            "Reviewed timewarped SRT output",
            lambda: get_series_timewarped(
                reference,
                series,
                one_start_idx=self.one_start_idx,
                one_end_idx=self.one_end_idx,
                two_start_idx=self.two_start_idx,
                two_end_idx=self.two_end_idx,
            ),
        )
