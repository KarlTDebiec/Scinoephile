#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Synchronize persisted LLM test cases from JSON into SQLite."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
    str_arg,
)
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.optimization.persistence.operations import (
    get_operation_spec,
    operation_names,
)
from scinoephile.optimization.persistence.test_cases.sqlite_store import (
    TestCaseSqliteStore,
)
from scinoephile.optimization.persistence.test_cases.sync import (
    sync_test_cases_from_json_paths,
)

from .operations import ListOperationsAction

__all__ = ["OptimizationSyncTestCasesCli"]


class OptimizationSyncTestCasesCli(ScinoephileCliBase):
    """Synchronize persisted LLM test cases from JSON into SQLite."""

    localizations = {
        "zh-hans": {
            "additional help": "附加帮助",
            "Available operations:": "可用操作：",
            "list available operations and exit": "列出可用操作并退出",
            "SQLite database outfile path": "SQLite 数据库输出路径",
            "operation to which test case JSON file(s) correspond": (
                "测试用例 JSON 文件对应的操作"
            ),
            "one or more input JSON paths": "一个或多个输入 JSON 路径",
            "synchronize persisted LLM test cases from JSON into SQLite": (
                "将 JSON 测试用例同步到 SQLite"
            ),
        },
        "zh-hant": {
            "additional help": "附加說明",
            "Available operations:": "可用操作：",
            "list available operations and exit": "列出可用操作並結束",
            "SQLite database outfile path": "SQLite 資料庫輸出路徑",
            "operation to which test case JSON file(s) correspond": (
                "測試用例 JSON 檔對應的操作"
            ),
            "one or more input JSON paths": "一個或多個輸入 JSON 路徑",
            "synchronize persisted LLM test cases from JSON into SQLite": (
                "將 JSON 測試用例同步到 SQLite"
            ),
        },
    }
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
            "additional help",
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
            required=True,
            type=str_arg(options=operation_names),
            help="operation to which test case JSON file(s) correspond",
        )
        arg_groups["operation arguments"].add_argument(
            "--dry-run",
            action="store_true",
            help="list rows that would be inserted or deleted without writing",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "--outfile",
            required=True,
            type=output_file_arg(exist_ok=True),
            help="SQLite database outfile path",
        )

        # Additional help
        arg_groups["additional help"].add_argument(
            "--list-operations",
            action=ListOperationsAction,
            help="list available operations and exit",
        )

        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Subcommand name."""
        return "sync-test-cases"

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments."""
        # Validate arguments
        infile_paths = kwargs.pop("infile_paths")
        outfile_path = kwargs.pop("outfile")
        operation = str(kwargs.pop("operation"))
        dry_run = bool(kwargs.pop("dry_run"))

        # Read inputs
        spec = get_operation_spec(operation)
        table_name = spec.table_name
        manager_cls = spec.manager_cls
        prompt_cls = spec.prompt_cls

        # Perform operations
        report = sync_test_cases_from_json_paths(
            database_path=outfile_path,
            table_name=table_name,
            input_paths=infile_paths,
            manager_cls=manager_cls,
            prompt_cls=prompt_cls,
            dry_run=dry_run,
        )

        # Write outputs
        if dry_run:
            store = TestCaseSqliteStore(outfile_path)
            store.create_schema()
            store.ensure_table(table_name)
            for test_case_id in report.insert_ids:
                tc = store.get_test_case(table_name, test_case_id)
                # The row may not exist yet in dry-run; print an ID-only stub if so.
                print(
                    {"action": "insert", "test_case_id": test_case_id}
                    if tc is None
                    else {
                        "action": "insert",
                        "test_case_id": tc.test_case_id,
                        "difficulty": tc.difficulty,
                        "prompt": tc.prompt,
                        "verified": tc.verified,
                        "query": tc.query,
                        "answer": tc.answer,
                    }
                )
            for test_case_id in report.delete_ids:
                print({"action": "delete", "test_case_id": test_case_id})
