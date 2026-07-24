#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for consistent argument-group order across the CLI tree."""

from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction  # noqa: PLC2701
from collections.abc import Iterator
from typing import cast

from scinoephile.cli.scinoephile_cli import ScinoephileCli

_GROUP_ORDER = (
    "positional arguments",
    "input arguments",
    "operation arguments",
    "llm arguments",
    "cache arguments",
    "web arguments",
    "output arguments",
    "additional arguments",
    "additional help",
)
"""Canonical display order for populated CLI argument groups."""


def test_cli_argument_groups_follow_canonical_order():
    """Test every command's populated argument groups use canonical order."""
    for path, parser in _iter_parsers(
        ScinoephileCli.argparser(),
        ("scinoephile",),
    ):
        titles = [
            group.title
            for group in parser._action_groups  # noqa: SLF001
            if group._group_actions  # noqa: SLF001
        ]
        expected = sorted(titles, key=_GROUP_ORDER.index)
        assert titles == expected, f"{' '.join(path)}: {titles}"


def _iter_parsers(
    parser: ArgumentParser,
    path: tuple[str, ...],
) -> Iterator[tuple[tuple[str, ...], ArgumentParser]]:
    """Iterate over a parser and all of its subcommand parsers.

    Arguments:
        parser: current argument parser
        path: command path corresponding to current parser
    Yields:
        command path and corresponding parser
    """
    yield path, parser
    for action in parser._actions:  # noqa: SLF001
        if not isinstance(action, _SubParsersAction):
            continue
        for name, subparser in sorted(action.choices.items()):
            yield from _iter_parsers(
                cast(ArgumentParser, subparser),
                (*path, name),
            )
