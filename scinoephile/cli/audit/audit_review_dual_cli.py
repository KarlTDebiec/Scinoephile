#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for dual-script subtitle review audits."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from scinoephile.analysis.audit.dual_review import (
    DualReviewAuditFilter,
    audit_dual_review,
)
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.lang.zho.script.conversion import get_zho_character_variants

from .audit_cli_base import AuditCliBase
from .utils import load_review_test_cases

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
            "optional test-case JSON file for the simplified review; required "
            "with --filter unverified"
        ): ("简体字校对的可选测试用例 JSON 文件；使用 --filter unverified 时为必需"),
        "first 1-indexed subtitle number to include, inclusive": (
            "要包含的第一个字幕编号（从 1 开始，包含该编号）"
        ),
        "last 1-indexed subtitle number to include, inclusive": (
            "要包含的最后一个字幕编号（从 1 开始，包含该编号）"
        ),
        (
            "rows to include: all, changes, discrepancies, or unverified; "
            "all includes every subtitle; changes includes any review edit or final "
            "discrepancy; discrepancies includes final discrepancies only; "
            "unverified includes subtitles in cases not marked verified (default: "
            "%(default)s)"
        ): (
            "要包含的行：all 表示每个字幕，changes 表示任何校对更改或最终差异，"
            "discrepancies 仅表示最终差异，unverified 表示未标记为已验证的案例"
            "中的字幕（默认：%(default)s）"
        ),
        (
            "further limit rows to those containing any listed character in any "
            "input; values may be separated or combined, and simplified and "
            "traditional variants are included automatically; Yue examples: 些 番 "
            "是 着 喇啦啰 这那; Zho examples: 著 着 甚 什 (default: no character "
            "filter)"
        ): (
            "进一步仅包含任一输入中含有所列字符的行；字符可分开或合并输入，"
            "并自动包含简繁体变体（粤语示例：些 番 是 着 喇啦啰 这那；中文"
            "示例：著 着 甚 什；默认：无字符筛选）"
        ),
        "Markdown outfile path (default: stdout)": (
            "Markdown 输出文件路径（默认：标准输出）"
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
        (
            "optional test-case JSON file for the traditional review; required "
            "with --filter unverified"
        ): ("繁體字校對的選用測試案例 JSON 檔；使用 --filter unverified 時為必需"),
        (
            "optional test-case JSON file for the traditional simplification "
            "review; required with --filter unverified"
        ): ("繁體字簡化校對的選用測試案例 JSON 檔；使用 --filter unverified 時為必需"),
        (
            "optional test-case JSON file for the simplified review; required "
            "with --filter unverified"
        ): ("簡體字校對的選用測試案例 JSON 檔；使用 --filter unverified 時為必需"),
        "first 1-indexed subtitle number to include, inclusive": (
            "要包含的第一個字幕編號（從 1 開始，包含該編號）"
        ),
        "last 1-indexed subtitle number to include, inclusive": (
            "要包含的最後一個字幕編號（從 1 開始，包含該編號）"
        ),
        (
            "rows to include: all, changes, discrepancies, or unverified; "
            "all includes every subtitle; changes includes any review edit or final "
            "discrepancy; discrepancies includes final discrepancies only; "
            "unverified includes subtitles in cases not marked verified (default: "
            "%(default)s)"
        ): (
            "要包含的列：all 表示每個字幕，changes 表示任何校對變更或最終差異，"
            "discrepancies 僅表示最終差異，unverified 表示未標記為已驗證的案例"
            "中的字幕（預設：%(default)s）"
        ),
        (
            "further limit rows to those containing any listed character in any "
            "input; values may be separated or combined, and simplified and "
            "traditional variants are included automatically; Yue examples: 些 番 "
            "是 着 喇啦啰 这那; Zho examples: 著 着 甚 什 (default: no character "
            "filter)"
        ): (
            "進一步僅包含任一輸入中含有所列字元的列；字元可分開或合併輸入，"
            "並自動包含簡繁體變體（粵語範例：些 番 是 着 喇啦啰 这那；中文"
            "範例：著 着 甚 什；預設：無字元篩選）"
        ),
        "Markdown outfile path (default: stdout)": (
            "Markdown 輸出檔路徑（預設：標準輸出）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditReviewDualCli(AuditCliBase):
    """Audit parallel simplified and traditional-to-simplified review paths."""

    localizations = AUDIT_REVIEW_DUAL_LOCALIZATIONS
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
            help=(
                "optional test-case JSON file for the simplified review; required "
                "with --filter unverified"
            ),
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
            DualReviewAuditFilter,
            DualReviewAuditFilter.changes,
            description=(
                "all includes every subtitle; changes includes any review edit or "
                "final discrepancy; discrepancies includes final discrepancies only; "
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
                "and traditional variants are included automatically; Yue "
                "examples: 些 番 是 着 喇啦啰 这那; Zho examples: 著 着 甚 什 "
                "(default: no character filter)"
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
        row_filter: DualReviewAuditFilter,
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
            simplified_path: simplified-script review input SRT path
            simplified_reviewed_path: simplified-script reviewed SRT path
            traditional_path: traditional-script review input SRT path
            traditional_reviewed_path: traditional-script reviewed SRT path
            traditional_simplified_path: simplified traditional-script SRT path
            traditional_simplified_reviewed_path: reviewed simplified
                traditional-script SRT path
            simplified_json_path: optional simplified-review test-case JSON path
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
        if row_filter is DualReviewAuditFilter.unverified and any(
            json_path is None
            for json_path in (
                simplified_json_path,
                traditional_json_path,
                traditional_simplified_json_path,
            )
        ):
            parser.error(
                "--filter unverified requires --simplified-json, "
                "--traditional-json, and --traditional-simplified-json"
            )
        characters = get_zho_character_variants(characters)

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
        simplified_review_cases = load_review_test_cases(parser, simplified_json_path)
        traditional_review_cases = load_review_test_cases(parser, traditional_json_path)
        traditional_simplified_review_cases = load_review_test_cases(
            parser, traditional_simplified_json_path
        )

        # Perform operation
        try:
            report = audit_dual_review(
                simplified=simplified,
                simplified_reviewed=simplified_reviewed,
                traditional=traditional,
                traditional_reviewed=traditional_reviewed,
                traditional_simplified=traditional_simplified,
                traditional_simplified_reviewed=traditional_simplified_reviewed,
                simplified_review_cases=simplified_review_cases,
                traditional_review_cases=traditional_review_cases,
                traditional_simplified_review_cases=traditional_simplified_review_cases,
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
