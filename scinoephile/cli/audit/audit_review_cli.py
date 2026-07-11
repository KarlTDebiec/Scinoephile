#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for one subtitle review audit."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from scinoephile.analysis.review_audit import (
    ReviewAuditFilter,
    ReviewAuditPair,
    audit_review_workflow,
)
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import get_arg_groups_by_name, input_file_arg
from scinoephile.core import Language, ScinoephileError
from scinoephile.lang.id import get_series_language

from .audit_workflow_cli_base import AuditWorkflowCliBase

__all__ = ["AuditReviewCli"]

AUDIT_REVIEW_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit one subtitle review with automatic language and script detection": (
            "通过自动语言和文字检测审核一次字幕校对"
        ),
        "subtitle SRT file before review": "校对前的字幕 SRT 文件",
        "subtitle SRT file after review": "校对后的字幕 SRT 文件",
        "optional JSON corresponding to this review": "与此次校对对应的可选 JSON",
    },
    "zh-hant": {
        "audit one subtitle review with automatic language and script detection": (
            "透過自動語言與文字偵測稽核一次字幕校對"
        ),
        "subtitle SRT file before review": "校對前的字幕 SRT 檔",
        "subtitle SRT file after review": "校對後的字幕 SRT 檔",
        "optional JSON corresponding to this review": "與此次校對對應的選用 JSON",
    },
}
"""Localized help text keyed by locale and English source text."""

_LANGUAGE_LABELS = {
    Language.eng: "English",
    Language.yue_hans: "Simplified Cantonese",
    Language.yue_hant: "Traditional Cantonese",
    Language.zho_hans: "Simplified Chinese",
    Language.zho_hant: "Traditional Chinese",
}
"""Report labels keyed by automatically detected language."""


class AuditReviewCli(AuditWorkflowCliBase):
    """Audit one subtitle review with automatic language and script detection."""

    localizations = AUDIT_REVIEW_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)
        arg_groups = get_arg_groups_by_name(
            parser,
            "input arguments",
            optional_arguments_name="additional arguments",
        )
        arg_groups["input arguments"].add_argument(
            "--original",
            dest="original_path",
            required=True,
            type=input_file_arg(),
            help="subtitle SRT file before review",
        )
        arg_groups["input arguments"].add_argument(
            "--reviewed",
            dest="reviewed_path",
            required=True,
            type=input_file_arg(),
            help="subtitle SRT file after review",
        )
        arg_groups["input arguments"].add_argument(
            "--json",
            dest="json_path",
            type=input_file_arg(),
            help="optional JSON corresponding to this review",
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "review"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        original_path: Path,
        reviewed_path: Path,
        json_path: Path | None,
        row_filter: ReviewAuditFilter,
        characters: Sequence[str],
        first_index: int | None,
        last_index: int | None,
        outfile_path: Path | None,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        cls.validate_range(parser, first_index, last_index)

        # Read inputs
        original = read_series(parser, original_path)
        reviewed = read_series(parser, reviewed_path)

        # Detect language
        detected_languages = {
            language
            for series in (original, reviewed)
            if (language := get_series_language(series)) is not None
        }
        if len(detected_languages) > 1:
            languages = ", ".join(
                sorted(language.tag for language in detected_languages)
            )
            parser.error(f"Subtitle inputs have conflicting languages: {languages}")
        if not detected_languages:
            parser.error("Unable to detect the language and script of subtitle inputs")
        language = detected_languages.pop()

        # Perform operation
        try:
            report = audit_review_workflow(
                reviews=(
                    ReviewAuditPair(
                        label=_LANGUAGE_LABELS[language],
                        original=original,
                        reviewed=reviewed,
                        review_cases=cls.load_review_cases(parser, json_path),
                    ),
                ),
                row_filter=row_filter,
                characters=cls.get_character_variants(characters),
                first_index=first_index,
                last_index=last_index,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write output
        cls.write_report(parser, report, outfile_path)


if __name__ == "__main__":
    AuditReviewCli.main()
