#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared CLI inspection helpers for tests."""

from __future__ import annotations

from argparse import Action, ArgumentParser

from scinoephile.common import CommandLineInterface

__all__ = [
    "get_cli_action",
    "get_cli_action_group_title",
    "get_parser_action",
]


def get_cli_action(cli: type[CommandLineInterface], option: str) -> Action:
    """Get a CLI parser action by option string.

    Arguments:
        cli: CLI class to inspect
        option: option string to inspect
    Returns:
        matching argparse action
    """
    return get_parser_action(cli.argparser(), option)


def get_cli_action_group_title(cli: type[CommandLineInterface], option: str) -> str:
    """Get the group title for a CLI parser option.

    Arguments:
        cli: CLI class to inspect
        option: option string to inspect
    Returns:
        title of the argument group containing the option
    Raises:
        AssertionError: if the option is not assigned to a group
    """
    parser = cli.argparser()
    action = get_parser_action(parser, option)
    for group in parser._action_groups:  # noqa: SLF001
        if action in group._group_actions:  # noqa: SLF001
            if group.title is not None:
                return group.title
            break
    raise AssertionError(f"{option} is not assigned to an argument group")


def get_parser_action(parser: ArgumentParser, option: str) -> Action:
    """Get a parser action by option string.

    Arguments:
        parser: parser to inspect
        option: option string to inspect
    Returns:
        matching argparse action
    Raises:
        AssertionError: if the option is not present
    """
    for action in parser._actions:  # noqa: SLF001
        if option in action.option_strings:
            return action
    raise AssertionError(f"{option} not found in {parser.prog}")
