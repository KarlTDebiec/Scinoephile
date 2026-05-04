#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Optimization-related tools."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import TypedDict, Unpack

from scinoephile.common import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .optimization_list_operations_cli import OptimizationListOperationsCli
from .optimization_test_cases_cli import OptimizationSyncTestCasesCli

__all__ = ["OptimizationCli"]


class _OptimizationCliKwargs(TypedDict, total=False):
    """Keyword arguments for OptimizationCli."""

    optimization_subcommand: str
    """Selected optimization subcommand."""


class OptimizationCli(ScinoephileCliBase):
    """Prompt optimization utilities and persistence."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="optimization_subcommand",
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
    def _main(cls, **kwargs: Unpack[_OptimizationCliKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        subcommand_name = kwargs.pop("optimization_subcommand")
        subcommand_cli_class = cls.subcommands()[subcommand_name]
        subcommand_cli_class._main(**kwargs)


if __name__ == "__main__":
    OptimizationCli.main()
