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
    ReviewAuditMode,
    ReviewAuditPair,
    audit_review_workflow,
)
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    enum_arg,
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core import Language
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.lang.id import get_series_language
from scinoephile.lang.zho.script.conversion import get_zho_character_variants
from scinoephile.llms.guided_review import GuidedReviewManager
from scinoephile.llms.review import ReviewManager

from .audit_cli_base import AuditCliBase

__all__ = ["AuditReviewCli"]

AUDIT_REVIEW_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit regular or guided subtitle reviews": "审核常规或引导式字幕校对",
        "review workflow to audit: regular or guided (default: regular)": (
            "要审核的校对工作流：regular 或 guided（默认：regular）"
        ),
        "target subtitle SRT file before review": "校对前的目标字幕 SRT 文件",
        "subtitle SRT file after regular review": "常规校对后的字幕 SRT 文件",
        "guide subtitle SRT file used for guided review": (
            "用于引导式校对的参考字幕 SRT 文件"
        ),
        "test-case JSON file; required in guided mode": (
            "测试用例 JSON 文件；guided 模式下为必需"
        ),
        "rows to include: all, changes, or unverified (default: changes)": (
            "要包含的行：all、changes 或 unverified（默认：changes）"
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
        "review workflow to audit: regular or guided (default: regular)": (
            "要稽核的校對工作流程：regular 或 guided（預設：regular）"
        ),
        "target subtitle SRT file before review": "校對前的目標字幕 SRT 檔",
        "subtitle SRT file after regular review": "常規校對後的字幕 SRT 檔",
        "guide subtitle SRT file used for guided review": (
            "用於引導式校對的參考字幕 SRT 檔"
        ),
        "test-case JSON file; required in guided mode": (
            "測試案例 JSON 檔；guided 模式下為必需"
        ),
        "rows to include: all, changes, or unverified (default: changes)": (
            "要包含的列：all、changes 或 unverified（預設：changes）"
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


class AuditReviewCli(AuditCliBase):
    """Audit regular or guided subtitle reviews."""

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
            "operation arguments",
            optional_arguments_name="additional arguments",
        )
        arg_groups["input arguments"].add_argument(
            "--original",
            "--target",
            dest="original_path",
            required=True,
            type=input_file_arg(),
            help="target subtitle SRT file before review",
        )
        arg_groups["input arguments"].add_argument(
            "--reviewed",
            dest="reviewed_path",
            type=input_file_arg(),
            help="subtitle SRT file after regular review",
        )
        arg_groups["input arguments"].add_argument(
            "--guide",
            dest="guide_path",
            type=input_file_arg(),
            help="guide subtitle SRT file used for guided review",
        )
        arg_groups["input arguments"].add_argument(
            "--json",
            dest="json_path",
            type=input_file_arg(),
            help="test-case JSON file; required in guided mode",
        )
        arg_groups["operation arguments"].add_argument(
            "--mode",
            choices=tuple(ReviewAuditMode),
            default=ReviewAuditMode.regular,
            type=enum_arg(ReviewAuditMode),
            help="review workflow to audit: regular or guided (default: regular)",
        )
        arg_groups["operation arguments"].add_argument(
            "--filter",
            choices=(
                ReviewAuditFilter.all,
                ReviewAuditFilter.changes,
                ReviewAuditFilter.unverified,
            ),
            default=ReviewAuditFilter.changes,
            dest="row_filter",
            metavar="{all,changes,unverified}",
            type=enum_arg(ReviewAuditFilter),
            help="rows to include: all, changes, or unverified (default: changes)",
        )
        arg_groups["operation arguments"].add_argument(
            "--characters",
            default=(),
            metavar="CHARACTER",
            nargs="+",
            help=(
                "characters to match in regular-review input; values may be "
                "separated or combined, and simplified and traditional variants "
                "are included automatically (default: no character filter)"
            ),
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
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
        """Load and audit one guided-review workflow."""
        target = read_series(parser, target_path)
        guide = read_series(parser, guide_path)
        test_cases = cls.load_test_cases(
            parser,
            json_path,
            GuidedReviewManager,
            workflow_name="guided review",
        )
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
        """Load and audit one regular-review workflow."""
        original = read_series(parser, original_path)
        reviewed = read_series(parser, reviewed_path)
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

        review_cases = ()
        if json_path is not None:
            review_cases = cls.load_test_cases(
                parser,
                json_path,
                ReviewManager,
                workflow_name="regular review",
            )
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
        mode: ReviewAuditMode,
        row_filter: ReviewAuditFilter,
        characters: Sequence[str],
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        cls.validate_unverified_filter(parser, row_filter, json_path)
        cls._validate_mode_inputs(
            parser,
            mode,
            reviewed_path=reviewed_path,
            guide_path=guide_path,
            json_path=json_path,
            characters=characters,
        )

        try:
            if mode is ReviewAuditMode.guided:
                assert guide_path is not None and json_path is not None
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
        cls.write_report(parser, report, outfile_path, overwrite)

    @staticmethod
    def _validate_mode_inputs(
        parser: ArgumentParser,
        mode: ReviewAuditMode,
        *,
        reviewed_path: Path | None,
        guide_path: Path | None,
        json_path: Path | None,
        characters: Sequence[str],
    ):
        """Validate mode-specific review inputs and filters."""
        if mode is ReviewAuditMode.guided:
            if guide_path is None:
                parser.error("--guide is required in guided mode")
            if json_path is None:
                parser.error("--json is required in guided mode")
            if reviewed_path is not None:
                parser.error("--reviewed is only supported in regular mode")
            if characters:
                parser.error("--characters is only supported in regular mode")
            return

        if reviewed_path is None:
            parser.error("--reviewed is required in regular mode")
        if guide_path is not None:
            parser.error("--guide is only supported in guided mode")


if __name__ == "__main__":
    AuditReviewCli.main()
