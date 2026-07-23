#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for regular and guided subtitle review audits."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from scinoephile.analysis.audit.guided_review import audit_guided_review
from scinoephile.analysis.audit.review import (
    ReviewAuditFilter,
    ReviewAuditPair,
    audit_review_workflow,
)
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core import Language
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.lang.id import get_series_language
from scinoephile.lang.zho.script.conversion import get_zho_character_variants
from scinoephile.llms.guided_review import GuidedReviewManager

from .audit_review_cli_base import AuditReviewCliBase

__all__ = ["AuditReviewCli"]

AUDIT_REVIEW_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit regular or guided subtitle reviews": "审核常规或引导式字幕校对",
        "original subtitle SRT file before review": "校对前的原始字幕 SRT 文件",
        "subtitle SRT file after regular review": "常规校对后的字幕 SRT 文件",
        "guide subtitle SRT file used for guided review": (
            "用于引导式校对的参考字幕 SRT 文件"
        ),
        "test-case JSON file; required with --guide or --filter unverified": (
            "测试用例 JSON 文件；与 --guide 或 --filter unverified 一同使用时为必需"
        ),
        "rows to include: all, changes, or unverified (default: %(default)s)": (
            "要包含的行：all、changes 或 unverified（默认：%(default)s）"
        ),
        (
            "characters to match in regular-review input; values may be separated "
            "or combined, and simplified and traditional variants are included "
            "automatically (default: no character filter)"
        ): (
            "要在常规校对输入中匹配的字符；字符可分开或合并输入，并自动包含"
            "简繁体变体（默认：无字符筛选）"
        ),
    },
    "zh-hant": {
        "audit regular or guided subtitle reviews": "稽核常規或引導式字幕校對",
        "original subtitle SRT file before review": "校對前的原始字幕 SRT 檔",
        "subtitle SRT file after regular review": "常規校對後的字幕 SRT 檔",
        "guide subtitle SRT file used for guided review": (
            "用於引導式校對的參考字幕 SRT 檔"
        ),
        "test-case JSON file; required with --guide or --filter unverified": (
            "測試案例 JSON 檔；與 --guide 或 --filter unverified 一同使用時為必需"
        ),
        "rows to include: all, changes, or unverified (default: %(default)s)": (
            "要包含的列：all、changes 或 unverified（預設：%(default)s）"
        ),
        (
            "characters to match in regular-review input; values may be separated "
            "or combined, and simplified and traditional variants are included "
            "automatically (default: no character filter)"
        ): (
            "要在常規校對輸入中搜尋的字元；字元可分開或合併輸入，並自動包含"
            "簡繁體變體（預設：無字元篩選）"
        ),
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


class AuditReviewCli(AuditReviewCliBase):
    """Audit regular or guided subtitle reviews."""

    localizations = AUDIT_REVIEW_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""
    characters_help = (
        "characters to match in regular-review input; values may be separated "
        "or combined, and simplified and traditional variants are included "
        "automatically (default: no character filter)"
    )
    """Help text for the workflow's character filter."""

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

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--original",
            dest="original_path",
            required=True,
            type=input_file_arg(),
            help="original subtitle SRT file before review",
        )
        workflow_inputs = arg_groups["input arguments"].add_mutually_exclusive_group(
            required=True
        )
        workflow_inputs.add_argument(
            "--reviewed",
            dest="reviewed_path",
            type=input_file_arg(),
            help="subtitle SRT file after regular review",
        )
        workflow_inputs.add_argument(
            "--guide",
            dest="guide_path",
            type=input_file_arg(),
            help="guide subtitle SRT file used for guided review",
        )
        arg_groups["input arguments"].add_argument(
            "--json",
            dest="json_path",
            type=input_file_arg(),
            help=("test-case JSON file; required with --guide or --filter unverified"),
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "review"

    @classmethod
    def _audit_guided(
        cls,
        parser: ArgumentParser,
        target_path: Path,
        guide_path: Path,
        json_path: Path,
        *,
        row_filter: ReviewAuditFilter,
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
    ) -> str:
        """Load and audit one guided-review workflow.

        Arguments:
            parser: parser used to report user-facing errors
            target_path: target subtitle SRT path
            guide_path: guide subtitle SRT path
            json_path: guided-review test-case JSON path
            row_filter: rows to include in the report
            first_index: first target subtitle number to include
            last_index: last target subtitle number to include
            first_block: first paired block number to include
            last_block: last paired block number to include
        Returns:
            Markdown audit report
        """
        # Read inputs
        target = read_series(parser, target_path)
        guide = read_series(parser, guide_path)

        # Load guided-review JSON
        test_cases = cls.load_test_cases(
            parser,
            json_path,
            GuidedReviewManager,
            workflow_name="guided review",
        )

        # Perform operation
        return audit_guided_review(
            target,
            guide,
            test_cases,
            row_filter=row_filter,
            first_index=first_index,
            last_index=last_index,
            first_block=first_block,
            last_block=last_block,
        )

    @classmethod
    def _audit_regular(
        cls,
        parser: ArgumentParser,
        original_path: Path,
        reviewed_path: Path,
        json_path: Path | None,
        *,
        row_filter: ReviewAuditFilter,
        characters: Sequence[str],
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
    ) -> str:
        """Load and audit one regular-review workflow.

        Arguments:
            parser: parser used to report user-facing errors
            original_path: original subtitle SRT path
            reviewed_path: reviewed subtitle SRT path
            json_path: optional regular-review test-case JSON path
            row_filter: rows to include in the report
            characters: characters used to further limit included rows
            first_index: first subtitle number to include
            last_index: last subtitle number to include
            first_block: first workflow block number to include
            last_block: last workflow block number to include
        Returns:
            Markdown audit report
        """
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
                sorted(language.code for language in detected_languages)
            )
            parser.error(f"Subtitle inputs have conflicting languages: {languages}")
        if not detected_languages:
            parser.error("Unable to detect the language and script of subtitle inputs")
        language = detected_languages.pop()

        # Load regular-review JSON
        review_cases = ()
        if json_path is not None:
            review_cases = cls.load_review_test_cases(
                parser,
                json_path,
            )

        # Perform operation
        return audit_review_workflow(
            reviews=(
                ReviewAuditPair(
                    label=_LANGUAGE_LABELS[language],
                    original=original,
                    reviewed=reviewed,
                    review_cases=review_cases,
                ),
            ),
            row_filter=row_filter,
            characters=get_zho_character_variants(characters),
            first_index=first_index,
            last_index=last_index,
            first_block=first_block,
            last_block=last_block,
        )

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        original_path: Path,
        reviewed_path: Path | None,
        guide_path: Path | None,
        json_path: Path | None,
        row_filter: ReviewAuditFilter,
        characters: Sequence[str],
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments.

        Arguments:
            _parser: parser used to report user-facing errors
            original_path: original subtitle SRT path
            reviewed_path: optional reviewed subtitle SRT path
            guide_path: optional guide subtitle SRT path
            json_path: optional review test-case JSON path
            row_filter: rows to include in the report
            characters: characters used to further limit included regular rows
            first_index: first subtitle number to include
            last_index: last subtitle number to include
            first_block: first workflow block number to include
            last_block: last workflow block number to include
            outfile_path: optional Markdown output path
            overwrite: whether to overwrite an existing output file
        """
        # Validate arguments
        parser = _parser or cls.argparser()
        if row_filter is ReviewAuditFilter.unverified and json_path is None:
            parser.error("--filter unverified requires --json")
        if guide_path is not None:
            if json_path is None:
                parser.error("--json is required with --guide")
            if characters:
                parser.error("--characters may only be used with --reviewed")

        # Perform operation
        try:
            if guide_path is not None:
                assert json_path is not None
                report = cls._audit_guided(
                    parser,
                    original_path,
                    guide_path,
                    json_path,
                    row_filter=row_filter,
                    first_index=first_index,
                    last_index=last_index,
                    first_block=first_block,
                    last_block=last_block,
                )
            else:
                assert reviewed_path is not None
                report = cls._audit_regular(
                    parser,
                    original_path,
                    reviewed_path,
                    json_path,
                    row_filter=row_filter,
                    characters=characters,
                    first_index=first_index,
                    last_index=last_index,
                    first_block=first_block,
                    last_block=last_block,
                )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write output
        cls.write_report(parser, report, outfile_path, overwrite)


if __name__ == "__main__":
    AuditReviewCli.main()
