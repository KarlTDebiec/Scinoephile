#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared command-line support for subtitle audits."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.helpers.blocks import add_block_range_args
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    int_arg,
    output_file_arg,
)
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.llms import Manager, TestCase
from scinoephile.core.llms.utils import load_test_cases_from_json

__all__ = ["AuditCliBase"]

AUDIT_CLI_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "first 1-indexed subtitle number to include, inclusive": (
            "要包含的第一个字幕编号（从 1 开始，包含该编号）"
        ),
        "last 1-indexed subtitle number to include, inclusive": (
            "要包含的最后一个字幕编号（从 1 开始，包含该编号）"
        ),
        "first 1-indexed workflow block number to include, inclusive": (
            "要包含的第一个工作流区块编号（从 1 开始，包含该编号）"
        ),
        "last 1-indexed workflow block number to include, inclusive": (
            "要包含的最后一个工作流区块编号（从 1 开始，包含该编号）"
        ),
        "Markdown outfile path (default: stdout)": (
            "Markdown 输出文件路径（默认：标准输出）"
        ),
        "overwrite outfile if it exists": "覆盖已存在的输出文件",
    },
    "zh-hant": {
        "first 1-indexed subtitle number to include, inclusive": (
            "要包含的第一個字幕編號（從 1 開始，包含該編號）"
        ),
        "last 1-indexed subtitle number to include, inclusive": (
            "要包含的最後一個字幕編號（從 1 開始，包含該編號）"
        ),
        "first 1-indexed workflow block number to include, inclusive": (
            "要包含的第一個工作流程區塊編號（從 1 開始，包含該區塊）"
        ),
        "last 1-indexed workflow block number to include, inclusive": (
            "要包含的最後一個工作流程區塊編號（從 1 開始，包含該區塊）"
        ),
        "Markdown outfile path (default: stdout)": (
            "Markdown 輸出檔路徑（預設：標準輸出）"
        ),
        "overwrite outfile if it exists": "覆寫已存在的輸出檔",
    },
}
"""Localized shared help text keyed by locale and English source text."""


class AuditCliBase(ScinoephileCliBase):
    """Shared command-line support for subtitle audits."""

    localizations = AUDIT_CLI_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add shared range and output arguments to a parser.

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
        add_block_range_args(
            arg_groups["operation arguments"],
            first_help=("first 1-indexed workflow block number to include, inclusive"),
            last_help="last 1-indexed workflow block number to include, inclusive",
        )
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            type=output_file_arg(exist_ok=True),
            help="Markdown outfile path (default: stdout)",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @staticmethod
    def load_test_cases[TTestCase: TestCase](
        parser: ArgumentParser,
        json_path: Path,
        manager_cls: type[Manager[TTestCase]],
        *,
        workflow_name: str,
    ) -> list[TTestCase]:
        """Load test cases from workflow JSON.

        Arguments:
            parser: parser used to report user-facing errors
            json_path: test-case JSON path
            manager_cls: manager defining the test-case model
            workflow_name: workflow name used in errors
        Returns:
            loaded test cases
        """
        try:
            return load_test_cases_from_json(
                json_path,
                manager_cls,
                manager_cls.base_prompt,
            )
        except (KeyError, OSError, TypeError, UnicodeError, ValueError) as exc:
            parser.error(f"Unable to load {workflow_name} JSON: {exc}")

    @staticmethod
    def write_report(
        parser: ArgumentParser,
        report: str,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Write a report to stdout or a file.

        Arguments:
            parser: parser used to report user-facing errors
            report: Markdown report
            outfile_path: optional output file path
            overwrite: whether to overwrite an existing output file
        """
        if outfile_path is None:
            if overwrite:
                parser.error("--overwrite may only be used with --outfile")
            print(report, end="")
            return
        if outfile_path.exists() and not overwrite:
            parser.error(f"File exists: {outfile_path}; use --overwrite to replace it")
        try:
            outfile_path.write_text(report, encoding="utf-8")
        except OSError as exc:
            parser.error(str(exc))
