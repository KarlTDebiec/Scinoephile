#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for traditional-simplification review audits."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from scinoephile.analysis.audit.review import (
    ReviewAuditPair,
    audit_review_workflow,
)
from scinoephile.analysis.audit.utils import ChangeAuditFilter
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.lang.zho.script.conversion import get_zho_character_variants

from .audit_cli_base import AuditCliBase
from .utils import load_review_test_cases

__all__ = ["AuditReviewTradCli"]

AUDIT_TRADITIONAL_SIMPLIFICATION_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit traditional review followed by review of its simplified form": (
            "审核繁体字校对及其后续简化形式校对"
        ),
        "traditional-script review input SRT file": "繁体字校对输入 SRT 文件",
        "traditional-script reviewed SRT file": "繁体字校对后 SRT 文件",
        "simplified traditional-script SRT file before review": (
            "校对前由繁体字转换的简体字 SRT 文件"
        ),
        "simplified traditional-script SRT file after review": (
            "校对后由繁体字转换的简体字 SRT 文件"
        ),
        (
            "optional test-case JSON file for the traditional review; required "
            "with --filter unverified"
        ): ("繁体字校对的可选测试用例 JSON 文件；使用 --filter unverified 时为必需"),
        (
            "optional test-case JSON file for the traditional simplification "
            "review; required with --filter unverified"
        ): (
            "繁体字简化校对的可选测试用例 JSON 文件；使用 --filter unverified 时为必需"
        ),
        (
            "rows to include: all, changes, or unverified; all includes every "
            "subtitle; changes includes review edits; unverified includes subtitles "
            "in cases not marked verified (default: %(default)s)"
        ): (
            "要包含的行：all 表示每个字幕，changes 表示校对更改，unverified "
            "表示未标记为已验证的案例中的字幕（默认：%(default)s）"
        ),
        (
            "further limit rows to those containing any listed character in any "
            "input; values may be separated or combined, and simplified and "
            "traditional variants are included automatically (default: no "
            "character filter)"
        ): (
            "进一步仅包含任一输入中含有所列字符的行；字符可分开或合并输入，"
            "并自动包含简繁体变体（默认：无字符筛选）"
        ),
    },
    "zh-hant": {
        "audit traditional review followed by review of its simplified form": (
            "稽核繁體字校對及其後續簡化形式校對"
        ),
        "traditional-script review input SRT file": "繁體字校對輸入 SRT 檔",
        "traditional-script reviewed SRT file": "繁體字校對後 SRT 檔",
        "simplified traditional-script SRT file before review": (
            "校對前由繁體字轉換的簡體字 SRT 檔"
        ),
        "simplified traditional-script SRT file after review": (
            "校對後由繁體字轉換的簡體字 SRT 檔"
        ),
        (
            "optional test-case JSON file for the traditional review; required "
            "with --filter unverified"
        ): ("繁體字校對的選用測試案例 JSON 檔；使用 --filter unverified 時為必需"),
        (
            "optional test-case JSON file for the traditional simplification "
            "review; required with --filter unverified"
        ): ("繁體字簡化校對的選用測試案例 JSON 檔；使用 --filter unverified 時為必需"),
        (
            "rows to include: all, changes, or unverified; all includes every "
            "subtitle; changes includes review edits; unverified includes subtitles "
            "in cases not marked verified (default: %(default)s)"
        ): (
            "要包含的列：all 表示每個字幕，changes 表示校對變更，unverified "
            "表示未標記為已驗證的案例中的字幕（預設：%(default)s）"
        ),
        (
            "further limit rows to those containing any listed character in any "
            "input; values may be separated or combined, and simplified and "
            "traditional variants are included automatically (default: no "
            "character filter)"
        ): (
            "進一步僅包含任一輸入中含有所列字元的列；字元可分開或合併輸入，"
            "並自動包含簡繁體變體（預設：無字元篩選）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditReviewTradCli(AuditCliBase):
    """Audit traditional review followed by review of its simplified form."""

    localizations = AUDIT_TRADITIONAL_SIMPLIFICATION_LOCALIZATIONS
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

        # Input arguments
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
            help="simplified traditional-script SRT file before review",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-simplified-reviewed",
            dest="traditional_simplified_reviewed_path",
            required=True,
            type=input_file_arg(),
            help="simplified traditional-script SRT file after review",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-json",
            dest="traditional_json_path",
            type=input_file_arg(),
            help=(
                "optional test-case JSON file for the traditional review; required "
                "with --filter unverified"
            ),
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-simplified-json",
            dest="traditional_simplified_json_path",
            type=input_file_arg(),
            help=(
                "optional test-case JSON file for the traditional simplification "
                "review; required with --filter unverified"
            ),
        )

        # Operation arguments
        cls.add_row_filter_argument(
            parser,
            ChangeAuditFilter,
            ChangeAuditFilter.changes,
            description=(
                "all includes every subtitle; changes includes review edits; "
                "unverified includes subtitles in cases not marked verified"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--characters",
            default=(),
            metavar="CHARACTER",
            nargs="+",
            help=(
                "further limit rows to those containing any listed character in "
                "any input; values may be separated or combined, and simplified "
                "and traditional variants are included automatically (default: "
                "no character filter)"
            ),
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "review-trad"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        traditional_path: Path,
        traditional_reviewed_path: Path,
        traditional_simplified_path: Path,
        traditional_simplified_reviewed_path: Path,
        traditional_json_path: Path | None,
        traditional_simplified_json_path: Path | None,
        row_filter: ChangeAuditFilter,
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
            traditional_path: traditional-script review input SRT path
            traditional_reviewed_path: traditional-script reviewed SRT path
            traditional_simplified_path: simplified traditional-script SRT path
            traditional_simplified_reviewed_path: reviewed simplified
                traditional-script SRT path
            traditional_json_path: optional traditional-review test-case JSON path
            traditional_simplified_json_path: optional traditional-simplification
                review test-case JSON path
            row_filter: rows to include in the report
            characters: characters used to further limit included rows
            first_index: first subtitle number to include
            last_index: last subtitle number to include
            first_block: first workflow block number to include
            last_block: last workflow block number to include
            outfile_path: optional Markdown output path
            overwrite: whether to overwrite an existing output file
        """
        # Validate arguments
        parser = _parser or cls.argparser()
        if row_filter is ChangeAuditFilter.unverified and (
            traditional_json_path is None or traditional_simplified_json_path is None
        ):
            parser.error(
                "--filter unverified requires --traditional-json and "
                "--traditional-simplified-json"
            )

        # Read inputs
        traditional = read_series(parser, traditional_path)
        traditional_reviewed = read_series(parser, traditional_reviewed_path)
        traditional_simplified = read_series(parser, traditional_simplified_path)
        traditional_simplified_reviewed = read_series(
            parser,
            traditional_simplified_reviewed_path,
        )
        traditional_review_cases = load_review_test_cases(parser, traditional_json_path)
        traditional_simplified_review_cases = load_review_test_cases(
            parser, traditional_simplified_json_path
        )

        # Perform operation
        try:
            report = audit_review_workflow(
                reviews=(
                    ReviewAuditPair(
                        label="Traditional",
                        original=traditional,
                        reviewed=traditional_reviewed,
                        review_cases=traditional_review_cases,
                    ),
                    ReviewAuditPair(
                        label="Traditional simplification",
                        original=traditional_simplified,
                        reviewed=traditional_simplified_reviewed,
                        review_cases=traditional_simplified_review_cases,
                    ),
                ),
                row_filter=row_filter,
                characters=get_zho_character_variants(characters),
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
    AuditReviewTradCli.main()
