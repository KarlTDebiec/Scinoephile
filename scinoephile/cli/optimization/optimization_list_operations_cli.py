#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for listing optimization operations."""

from __future__ import annotations

from typing import TypedDict, Unpack

from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.optimization.persistence.operations import operation_names

__all__ = ["OptimizationListOperationsCli"]


class _OptimizationListOperationsCliKwargs(TypedDict, total=False):
    """Keyword arguments for OptimizationListOperationsCli."""


class OptimizationListOperationsCli(ScinoephileCliBase):
    """List available optimization operations."""

    localizations = {
        "zh-hans": {
            "Available operations:": "可用操作：",
            "list available optimization operations": "列出可用优化操作",
        },
        "zh-hant": {
            "Available operations:": "可用操作：",
            "list available optimization operations": "列出可用最佳化操作",
        },
    }
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "list-operations"

    @classmethod
    def _main(cls, **kwargs: Unpack[_OptimizationListOperationsCliKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        del kwargs
        heading = cls.translate_text("Available operations:")
        print(heading)
        for name in operation_names:
            print(f"  {name}")
