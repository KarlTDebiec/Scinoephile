#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CLI helpers for optimization operations."""

from __future__ import annotations

import sys
from argparse import Action, ArgumentParser, Namespace

from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.optimization.persistence.operations import operation_names

__all__ = [
    "ListOperationsAction",
]


class ListOperationsAction(Action):
    """Print available operations and exit."""

    def __init__(self, option_strings, dest, **kwargs):
        """Initialize.

        Arguments:
            option_strings: option strings
            dest: argparse destination name
            **kwargs: additional keyword arguments
        """
        kwargs.setdefault("nargs", 0)
        super().__init__(option_strings=option_strings, dest=dest, **kwargs)

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values,
        option_string: str | None = None,
    ):
        """Handle the action.

        Arguments:
            parser: active argument parser
            namespace: parsed namespace
            values: parsed argument value
            option_string: option string used
        """
        del namespace, values, option_string
        heading = ScinoephileCliBase.translate_text("Available operations:")
        lines = [heading]
        lines.extend(f"  {name}" for name in operation_names)
        parser._print_message("\n".join(lines) + "\n", sys.stdout)  # noqa: SLF001
        parser.exit(0)
