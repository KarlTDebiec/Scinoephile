#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Synchronize persisted LLM test cases from JSON into SQLite."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.llms import Manager
from scinoephile.optimization.persistence.test_cases.sync import (
    sync_test_cases,
)

from .argument_types import operation_arg

__all__ = ["OptimizationSyncTestCasesCli"]

OPTIMIZATION_SYNC_TEST_CASES_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "SQLite database outfile path": "SQLite 数据库输出路径",
        "LLM operation name from the optimization registry for these test case JSON "
        "file(s)": ("这些测试用例 JSON 文件对应的优化注册表 LLM 操作名称"),
        "list source associations that would be inserted or deleted without writing": (
            "列出将插入或删除的来源关联而不写入"
        ),
        "one or more input JSON paths": "一个或多个输入 JSON 路径",
        "synchronize persisted LLM test cases from JSON into SQLite": (
            "将 JSON 测试用例同步到 SQLite"
        ),
    },
    "zh-hant": {
        "SQLite database outfile path": "SQLite 資料庫輸出路徑",
        "LLM operation name from the optimization registry for these test case JSON "
        "file(s)": ("這些測試用例 JSON 檔對應的最佳化登錄檔 LLM 操作名稱"),
        "list source associations that would be inserted or deleted without writing": (
            "列出將插入或刪除的來源關聯而不寫入"
        ),
        "one or more input JSON paths": "一個或多個輸入 JSON 路徑",
        "synchronize persisted LLM test cases from JSON into SQLite": (
            "將 JSON 測試用例同步到 SQLite"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class OptimizationSyncTestCasesCli(ScinoephileCliBase):
    """Synchronize persisted LLM test cases from JSON into SQLite."""

    localizations = OPTIMIZATION_SYNC_TEST_CASES_LOCALIZATIONS
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
            "--infile",
            required=True,
            nargs="+",
            dest="infile_paths",
            type=input_file_arg(),
            help="one or more input JSON paths",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--operation",
            dest="manager_cls",
            required=True,
            type=operation_arg,
            help=(
                "LLM operation name from the optimization registry for these test "
                "case JSON file(s)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "list source associations that would be inserted or deleted without "
                "writing"
            ),
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "--outfile",
            dest="outfile_path",
            required=True,
            type=output_file_arg(exist_ok=True),
            help="SQLite database outfile path",
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "sync-test-cases"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_paths: list[Path],
        manager_cls: type[Manager],
        dry_run: bool,
        outfile_path: Path,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()

        # Perform operations
        try:
            report = sync_test_cases(
                infile_paths,
                outfile_path,
                manager_cls,
                dry_run=dry_run,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write outputs
        if dry_run:
            for test_case_id in report.insert_ids:
                print({"action": "insert", "test_case_id": test_case_id})
            for test_case_id in report.delete_ids:
                print({"action": "delete", "test_case_id": test_case_id})
        else:
            print(
                {
                    "operation": report.operation,
                    "sources": len(report.input_paths),
                    "inserted": len(report.insert_ids),
                    "deleted": len(report.delete_ids),
                }
            )
