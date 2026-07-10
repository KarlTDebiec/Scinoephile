#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for subtitle review audits."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from scinoephile.analysis.review_audit import ReviewAuditFilter, audit_reviews
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    enum_arg,
    enum_metavar,
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase

__all__ = ["AuditCli"]

AUDIT_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
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
        "optional review JSON corresponding to --traditional": (
            "与 --traditional 对应的可选校对 JSON"
        ),
        "optional review JSON corresponding to --traditional-simplified": (
            "与 --traditional-simplified 对应的可选校对 JSON"
        ),
        "optional review JSON corresponding to --simplified": (
            "与 --simplified 对应的可选校对 JSON"
        ),
        "first 1-indexed subtitle number to include, inclusive": (
            "要包含的第一个字幕编号（从 1 开始，包含该编号）"
        ),
        "last 1-indexed subtitle number to include, inclusive": (
            "要包含的最后一个字幕编号（从 1 开始，包含该编号）"
        ),
        (
            "rows to include: all; changes for any review edit or final "
            "discrepancy; discrepancies for final discrepancies only "
            "(default: changes)"
        ): (
            "要包含的行：all 表示全部；changes 表示任何校对更改或最终差异；"
            "discrepancies 仅表示最终差异（默认：changes）"
        ),
        (
            "further limit rows to those containing any listed character in any "
            "input; values may be separated or combined (Yue examples: 些 番 是 着 "
            "喇啦啰 这那; Zho examples: 著 着 甚 什)"
        ): (
            "进一步仅包含任一输入中含有所列字符的行；字符可分开或合并输入"
            "（粤语示例：些 番 是 着 喇啦啰 这那；中文示例：著 着 甚 什）"
        ),
        "Markdown outfile path (default: stdout)": (
            "Markdown 输出文件路径（默认：标准输出）"
        ),
    },
    "zh-hant": {
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
        "optional review JSON corresponding to --traditional": (
            "與 --traditional 對應的選用校對 JSON"
        ),
        "optional review JSON corresponding to --traditional-simplified": (
            "與 --traditional-simplified 對應的選用校對 JSON"
        ),
        "optional review JSON corresponding to --simplified": (
            "與 --simplified 對應的選用校對 JSON"
        ),
        "first 1-indexed subtitle number to include, inclusive": (
            "要包含的第一個字幕編號（從 1 開始，包含該編號）"
        ),
        "last 1-indexed subtitle number to include, inclusive": (
            "要包含的最後一個字幕編號（從 1 開始，包含該編號）"
        ),
        (
            "rows to include: all; changes for any review edit or final "
            "discrepancy; discrepancies for final discrepancies only "
            "(default: changes)"
        ): (
            "要包含的列：all 表示全部；changes 表示任何校對變更或最終差異；"
            "discrepancies 僅表示最終差異（預設：changes）"
        ),
        (
            "further limit rows to those containing any listed character in any "
            "input; values may be separated or combined (Yue examples: 些 番 是 着 "
            "喇啦啰 这那; Zho examples: 著 着 甚 什)"
        ): (
            "進一步僅包含任一輸入中含有所列字元的列；字元可分開或合併輸入"
            "（粵語範例：些 番 是 着 喇啦啰 这那；中文範例：著 着 甚 什）"
        ),
        "Markdown outfile path (default: stdout)": (
            "Markdown 輸出檔路徑（預設：標準輸出）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditCli(ScinoephileCliBase):
    """Audit subtitle review changes and final discrepancies."""

    localizations = AUDIT_LOCALIZATIONS
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
            "output arguments",
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
            help="optional review JSON corresponding to --simplified",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-json",
            dest="traditional_json_path",
            type=input_file_arg(),
            help="optional review JSON corresponding to --traditional",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-simplified-json",
            dest="traditional_simplified_json_path",
            type=input_file_arg(),
            help=("optional review JSON corresponding to --traditional-simplified"),
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--first-index",
            type=int_arg(min_value=1),
            help="first 1-indexed subtitle number to include, inclusive",
        )
        arg_groups["operation arguments"].add_argument(
            "--last-index",
            type=int_arg(min_value=1),
            help="last 1-indexed subtitle number to include, inclusive",
        )
        arg_groups["operation arguments"].add_argument(
            "--filter",
            default=ReviewAuditFilter.changes,
            dest="row_filter",
            metavar=enum_metavar(ReviewAuditFilter),
            type=enum_arg(ReviewAuditFilter),
            help=(
                "rows to include: all; changes for any review edit or final "
                "discrepancy; discrepancies for final discrepancies only "
                "(default: changes)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--characters",
            default=(),
            metavar="CHARACTER",
            nargs="+",
            help=(
                "further limit rows to those containing any listed character in any "
                "input; values may be separated or combined (Yue examples: 些 番 是 "
                "着 喇啦啰 这那; Zho examples: 著 着 甚 什)"
            ),
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            type=output_file_arg(),
            help="Markdown outfile path (default: stdout)",
        )
        parser.set_defaults(_parser=parser)

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
        outfile_path: Path | None,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if (
            first_index is not None
            and last_index is not None
            and first_index > last_index
        ):
            parser.error("--first-index must be less than or equal to --last-index")

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

        # Perform operation
        try:
            report = audit_reviews(
                simplified=simplified,
                simplified_reviewed=simplified_reviewed,
                traditional=traditional,
                traditional_reviewed=traditional_reviewed,
                traditional_simplified=traditional_simplified,
                traditional_simplified_reviewed=traditional_simplified_reviewed,
                simplified_json_path=simplified_json_path,
                traditional_json_path=traditional_json_path,
                traditional_simplified_json_path=traditional_simplified_json_path,
                row_filter=row_filter,
                characters=characters,
                first_index=first_index,
                last_index=last_index,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write output
        if outfile_path is None:
            print(report, end="")
            return
        try:
            outfile_path.write_text(report, encoding="utf-8")
        except OSError as exc:
            parser.error(str(exc))


if __name__ == "__main__":
    AuditCli.main()
