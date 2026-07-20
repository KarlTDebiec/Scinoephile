#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for dual-script subtitle review audits."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from scinoephile.analysis.review_audit import ReviewAuditFilter, audit_reviews
from scinoephile.cli.helpers.blocks import validate_block_range
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core import ScinoephileError

from .audit_workflow_cli_base import AuditWorkflowCliBase

__all__ = ["AuditReviewDualCli"]

AUDIT_REVIEW_DUAL_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit parallel simplified and traditional-to-simplified review paths": (
            "审核并行的简体字及繁体转简体校对路径"
        ),
        "audit subtitle review changes and final discrepancies": (
            "审核字幕校对更改和最终差异"
        ),
        "traditional-script review input SRT file": "繁体字校对输入 SRT 文件",
        "traditional-script reviewed SRT file": "繁体字校对后 SRT 文件",
        "simplified traditional-script SRT file before its final review": (
            "最终校对前由繁体字转换的简体字 SRT 文件"
        ),
        "simplified traditional-script SRT file after its final review": (
            "最终校对后由繁体字转换的简体字 SRT 文件"
        ),
        "simplified-script review input SRT file": "简体字校对输入 SRT 文件",
        "simplified-script reviewed SRT file": "简体字校对后 SRT 文件",
        "optional test-case JSON file for the traditional review": (
            "繁体字校对的可选测试用例 JSON 文件"
        ),
        "optional test-case JSON file for the traditional simplification review": (
            "繁体字简化校对的可选测试用例 JSON 文件"
        ),
        "optional test-case JSON file for the simplified review": (
            "简体字校对的可选测试用例 JSON 文件"
        ),
        (
            "rows to include: all, changes, or discrepancies; changes includes "
            "review edits and final discrepancies (default: changes)"
        ): (
            "要包含的行：all、changes 或 discrepancies；changes 包含校对更改"
            "和最终差异（默认：changes）"
        ),
    },
    "zh-hant": {
        "audit parallel simplified and traditional-to-simplified review paths": (
            "稽核並行的簡體字及繁體轉簡體校對路徑"
        ),
        "audit subtitle review changes and final discrepancies": (
            "稽核字幕校對變更與最終差異"
        ),
        "traditional-script review input SRT file": "繁體字校對輸入 SRT 檔",
        "traditional-script reviewed SRT file": "繁體字校對後 SRT 檔",
        "simplified traditional-script SRT file before its final review": (
            "最終校對前由繁體字轉換的簡體字 SRT 檔"
        ),
        "simplified traditional-script SRT file after its final review": (
            "最終校對後由繁體字轉換的簡體字 SRT 檔"
        ),
        "simplified-script review input SRT file": "簡體字校對輸入 SRT 檔",
        "simplified-script reviewed SRT file": "簡體字校對後 SRT 檔",
        "optional test-case JSON file for the traditional review": (
            "繁體字校對的選用測試案例 JSON 檔"
        ),
        "optional test-case JSON file for the traditional simplification review": (
            "繁體字簡化校對的選用測試案例 JSON 檔"
        ),
        "optional test-case JSON file for the simplified review": (
            "簡體字校對的選用測試案例 JSON 檔"
        ),
        (
            "rows to include: all, changes, or discrepancies; changes includes "
            "review edits and final discrepancies (default: changes)"
        ): (
            "要包含的列：all、changes 或 discrepancies；changes 包含校對變更"
            "與最終差異（預設：changes）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditReviewDualCli(AuditWorkflowCliBase):
    """Audit parallel simplified and traditional-to-simplified review paths."""

    localizations = AUDIT_REVIEW_DUAL_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""
    row_filter_help = (
        "rows to include: all, changes, or discrepancies; changes includes review "
        "edits and final discrepancies (default: changes)"
    )
    """Help text for the workflow's supported row filters."""
    row_filters = tuple(ReviewAuditFilter)
    """Row filters supported by the workflow."""

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
            "--simplified",
            dest="simplified_path",
            required=True,
            type=input_file_arg(),
            help="simplified-script review input SRT file",
        )
        arg_groups["input arguments"].add_argument(
            "--simplified-reviewed",
            dest="simplified_reviewed_path",
            required=True,
            type=input_file_arg(),
            help="simplified-script reviewed SRT file",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional",
            dest="traditional_path",
            required=True,
            type=input_file_arg(),
            help="traditional-script review input SRT file",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-reviewed",
            dest="traditional_reviewed_path",
            required=True,
            type=input_file_arg(),
            help="traditional-script reviewed SRT file",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-simplified",
            dest="traditional_simplified_path",
            required=True,
            type=input_file_arg(),
            help="simplified traditional-script SRT file before its final review",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-simplified-reviewed",
            dest="traditional_simplified_reviewed_path",
            required=True,
            type=input_file_arg(),
            help="simplified traditional-script SRT file after its final review",
        )
        arg_groups["input arguments"].add_argument(
            "--simplified-json",
            dest="simplified_json_path",
            type=input_file_arg(),
            help="optional test-case JSON file for the simplified review",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-json",
            dest="traditional_json_path",
            type=input_file_arg(),
            help="optional test-case JSON file for the traditional review",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-simplified-json",
            dest="traditional_simplified_json_path",
            type=input_file_arg(),
            help=(
                "optional test-case JSON file for the traditional simplification review"
            ),
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "review-dual"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        simplified_path: Path,
        simplified_reviewed_path: Path,
        traditional_path: Path,
        traditional_reviewed_path: Path,
        traditional_simplified_path: Path,
        traditional_simplified_reviewed_path: Path,
        simplified_json_path: Path | None,
        traditional_json_path: Path | None,
        traditional_simplified_json_path: Path | None,
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
        # Validate arguments
        parser = _parser or cls.argparser()
        cls.validate_range(parser, first_index, last_index)
        validate_block_range(parser, first_block, last_block)
        characters = cls.get_character_variants(characters)

        # Read inputs
        simplified = read_series(parser, simplified_path)
        simplified_reviewed = read_series(parser, simplified_reviewed_path)
        traditional = read_series(parser, traditional_path)
        traditional_reviewed = read_series(parser, traditional_reviewed_path)
        traditional_simplified = read_series(parser, traditional_simplified_path)
        traditional_simplified_reviewed = read_series(
            parser,
            traditional_simplified_reviewed_path,
        )
        input_series = (
            simplified,
            simplified_reviewed,
            traditional,
            traditional_reviewed,
            traditional_simplified,
            traditional_simplified_reviewed,
        )
        if len(set(map(len, input_series))) != 1:
            parser.error("Subtitle inputs must contain the same number of subtitles")

        # Load review JSON
        review_cases = {
            "simplified": cls.load_review_cases(parser, simplified_json_path),
            "traditional": cls.load_review_cases(parser, traditional_json_path),
            "traditional_simplified": cls.load_review_cases(
                parser,
                traditional_simplified_json_path,
            ),
        }

        # Perform operation
        try:
            report = audit_reviews(
                simplified=simplified,
                simplified_reviewed=simplified_reviewed,
                traditional=traditional,
                traditional_reviewed=traditional_reviewed,
                traditional_simplified=traditional_simplified,
                traditional_simplified_reviewed=traditional_simplified_reviewed,
                simplified_review_cases=review_cases["simplified"],
                traditional_review_cases=review_cases["traditional"],
                traditional_simplified_review_cases=(
                    review_cases["traditional_simplified"]
                ),
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
    AuditReviewDualCli.main()
