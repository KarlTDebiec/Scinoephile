#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Synchronize registered LLM prompts into SQLite."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    output_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.optimization.persistence.prompts.sync import sync_prompts
from scinoephile.workflows.prompt_catalog import PROMPT_SPECS

__all__ = ["OptimizationSyncPromptsCli"]

OPTIMIZATION_SYNC_PROMPTS_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "SQLite database outfile path": "SQLite 数据库输出路径",
        "list prompt and alias changes without writing": (
            "列出提示词和别名变更而不写入"
        ),
        "one or more prompt aliases from the optimization registry": (
            "优化注册表中的一个或多个提示词别名"
        ),
        "synchronize all registered prompts": "同步所有已注册的提示词",
        "synchronize registered LLM prompts into SQLite": (
            "将已注册的大语言模型提示词同步到 SQLite"
        ),
    },
    "zh-hant": {
        "SQLite database outfile path": "SQLite 資料庫輸出路徑",
        "list prompt and alias changes without writing": (
            "列出提示詞和別名變更而不寫入"
        ),
        "one or more prompt aliases from the optimization registry": (
            "最佳化登錄檔中的一個或多個提示詞別名"
        ),
        "synchronize all registered prompts": "同步所有已登錄的提示詞",
        "synchronize registered LLM prompts into SQLite": (
            "將已登錄的大型語言模型提示詞同步到 SQLite"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class OptimizationSyncPromptsCli(ScinoephileCliBase):
    """Synchronize registered LLM prompts into SQLite."""

    localizations = OPTIMIZATION_SYNC_PROMPTS_LOCALIZATIONS
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
            "operation arguments",
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        # Operation arguments
        selection_group = arg_groups[
            "operation arguments"
        ].add_mutually_exclusive_group(required=True)
        selection_group.add_argument(
            "--prompt",
            dest="prompt_aliases",
            nargs="+",
            choices=PROMPT_SPECS,
            help=("one or more prompt aliases from the optimization registry"),
        )
        selection_group.add_argument(
            "--all",
            dest="all_prompts",
            action="store_true",
            help="synchronize all registered prompts",
        )
        arg_groups["operation arguments"].add_argument(
            "--dry-run",
            action="store_true",
            help="list prompt and alias changes without writing",
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
        return "sync-prompts"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        prompt_aliases: list[str] | None,
        all_prompts: bool,
        dry_run: bool,
        outfile_path: Path,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()

        # Perform operations
        selected_prompt_specs = {
            alias: PROMPT_SPECS[alias] for alias in prompt_aliases or ()
        }
        if all_prompts:
            selected_prompt_specs = PROMPT_SPECS
        if not selected_prompt_specs:
            parser.error("One or more prompts must be selected.")
        try:
            report = sync_prompts(
                selected_prompt_specs,
                outfile_path,
                dry_run=dry_run,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write outputs
        if dry_run:
            for alias in report.insert_aliases:
                print({"action": "insert-alias", "alias": alias})
            for alias in report.update_aliases:
                print({"action": "update-alias", "alias": alias})
        else:
            print(
                {
                    "prompts": report.prompt_count,
                    "aliases_inserted": len(report.insert_aliases),
                    "aliases_updated": len(report.update_aliases),
                }
            )
