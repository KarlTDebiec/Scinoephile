#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Optimization-related tools."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .optimization_list_operations_cli import OptimizationListOperationsCli
from .optimization_test_cases_cli import OptimizationSyncTestCasesCli

__all__ = ["OptimizationCli"]


class OptimizationCli(ScinoephileCliBase):
    """Prompt optimization utilities and persistence."""

    localizations = {
        "zh-hans": {
            "optimization-related tools": "优化相关工具",
            "prompt optimization utilities and persistence": "提示词优化工具与持久化",
        },
        "zh-hant": {
            "optimization-related tools": "最佳化相關工具",
            "prompt optimization utilities and persistence": "提示詞最佳化工具與持久化",
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

        subparsers = parser.add_subparsers(
            dest="optimization_subcommand_name",
            help="subcommand",
            required=True,
        )
        subcommands = cls.subcommands()
        for name in sorted(subcommands):
            subcommands[name].argparser(subparsers=subparsers)

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface.

        Returns:
            mapping of subcommand names to CLI classes
        """
        return {
            OptimizationListOperationsCli.name(): OptimizationListOperationsCli,
            OptimizationSyncTestCasesCli.name(): OptimizationSyncTestCasesCli,
        }

    @classmethod
    def _main(
        cls,
        *,
        optimization_subcommand_name: str,
        **kwargs: Any,
    ):
        """Execute with provided keyword arguments."""
        cls.subcommands()[optimization_subcommand_name]._main(**kwargs)


if __name__ == "__main__":
    OptimizationCli.main()
