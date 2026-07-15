#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for transcription punctuation audits."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import cast

from scinoephile.analysis.punctuation_audit import (
    PunctuationAuditFilter,
    audit_punctuation,
)
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    enum_arg,
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.llms.punctuation import PunctuationManager, PunctuationTestCase

__all__ = ["AuditPunctuationCli"]

AUDIT_PUNCTUATION_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit transcription punctuation decisions": "审核转写字幕标点决策",
        "reference subtitle SRT file used to guide punctuation": (
            "用于指导标点的参考字幕 SRT 文件"
        ),
        "punctuated target subtitle SRT file": "已加标点的目标字幕 SRT 文件",
        "punctuation test-case JSON file": "字幕标点测试用例 JSON 文件",
        "first 1-indexed subtitle number to include, inclusive": (
            "要包含的第一个字幕编号（从 1 开始，包含该编号）"
        ),
        "last 1-indexed subtitle number to include, inclusive": (
            "要包含的最后一个字幕编号（从 1 开始，包含该编号）"
        ),
        "rows to include: all or changes (default: all)": (
            "要包含的行：all 表示全部，changes 表示标点调整（默认：all）"
        ),
        "Markdown outfile path (default: stdout)": (
            "Markdown 输出文件路径（默认：标准输出）"
        ),
    },
    "zh-hant": {
        "audit transcription punctuation decisions": "稽核轉寫字幕標點決策",
        "reference subtitle SRT file used to guide punctuation": (
            "用於指導標點的參考字幕 SRT 檔"
        ),
        "punctuated target subtitle SRT file": "已加標點的目標字幕 SRT 檔",
        "punctuation test-case JSON file": "字幕標點測試案例 JSON 檔",
        "first 1-indexed subtitle number to include, inclusive": (
            "要包含的第一個字幕編號（從 1 開始，包含該編號）"
        ),
        "last 1-indexed subtitle number to include, inclusive": (
            "要包含的最後一個字幕編號（從 1 開始，包含該編號）"
        ),
        "rows to include: all or changes (default: all)": (
            "要包含的列：all 表示全部，changes 表示標點調整（預設：all）"
        ),
        "Markdown outfile path (default: stdout)": (
            "Markdown 輸出檔路徑（預設：標準輸出）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditPunctuationCli(ScinoephileCliBase):
    """Audit transcription punctuation decisions."""

    localizations = AUDIT_PUNCTUATION_LOCALIZATIONS
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
        arg_groups["input arguments"].add_argument(
            "--reference",
            dest="reference_path",
            required=True,
            type=input_file_arg(),
            help="reference subtitle SRT file used to guide punctuation",
        )
        arg_groups["input arguments"].add_argument(
            "--target",
            dest="target_path",
            required=True,
            type=input_file_arg(),
            help="punctuated target subtitle SRT file",
        )
        arg_groups["input arguments"].add_argument(
            "--json",
            dest="json_path",
            required=True,
            type=input_file_arg(),
            help="punctuation test-case JSON file",
        )
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
            choices=tuple(PunctuationAuditFilter),
            default=PunctuationAuditFilter.all,
            dest="row_filter",
            metavar="{all,changes}",
            type=enum_arg(PunctuationAuditFilter),
            help="rows to include: all or changes (default: all)",
        )
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            type=output_file_arg(),
            help="Markdown outfile path (default: stdout)",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return "punctuation"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        reference_path: Path,
        target_path: Path,
        json_path: Path,
        row_filter: PunctuationAuditFilter,
        first_index: int | None,
        last_index: int | None,
        outfile_path: Path | None,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        if (
            first_index is not None
            and last_index is not None
            and first_index > last_index
        ):
            parser.error("--first-index must be less than or equal to --last-index")
        reference = read_series(parser, reference_path)
        target = read_series(parser, target_path)
        try:
            loaded_test_cases = load_test_cases_from_json(
                json_path,
                PunctuationManager,
                PunctuationManager.base_prompt,
            )
        except (KeyError, OSError, TypeError, UnicodeError, ValueError) as exc:
            parser.error(f"Unable to load punctuation JSON: {exc}")

        test_cases = [
            cast(PunctuationTestCase, test_case) for test_case in loaded_test_cases
        ]

        try:
            report = audit_punctuation(
                reference,
                target,
                test_cases,
                row_filter=row_filter,
                first_index=first_index,
                last_index=last_index,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        if outfile_path is None:
            print(report, end="")
            return
        try:
            outfile_path.write_text(report, encoding="utf-8")
        except OSError as exc:
            parser.error(str(exc))


if __name__ == "__main__":
    AuditPunctuationCli.main()
