#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.cli.list_all_commands_action."""

from __future__ import annotations

from typing import Any

from common.cli import CommandLineInterface, ListAllCommandsAction
from pytest import MonkeyPatch, mark


class EmptyCli(CommandLineInterface):
    """Empty CLI for testing command listing."""

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: additional keyword arguments
        """


class NoncallableSubcommandsCli(CommandLineInterface):
    """CLI with noncallable subcommands for testing command listing."""

    subcommands = {}
    """Noncallable subcommands attribute."""

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: additional keyword arguments
        """


class NonmappingSubcommandsCli(CommandLineInterface):
    """CLI with nonmapping subcommands for testing command listing."""

    @classmethod
    def subcommands(cls) -> list[str]:
        """Get invalid subcommands.

        Returns:
            invalid subcommands
        """
        return []

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: additional keyword arguments
        """


class InvalidSubcommandCli(CommandLineInterface):
    """CLI with invalid subcommand entries for testing command listing."""

    @classmethod
    def subcommands(cls) -> dict[str, object]:
        """Get invalid subcommands.

        Returns:
            invalid subcommands
        """
        return {"invalid": object()}

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: additional keyword arguments
        """


def test_format_all_commands_handles_empty_hierarchy():
    """Test formatting all commands handles CLIs without subcommands."""
    output = ListAllCommandsAction.format_all_commands(EmptyCli)

    assert output == "Available subcommands:"


def test_iter_command_rows_ignores_noncallable_subcommands():
    """Test command row iteration ignores noncallable subcommands attributes."""
    rows = ListAllCommandsAction.iter_command_rows(NoncallableSubcommandsCli)

    assert rows == []


def test_iter_command_rows_ignores_nonmapping_subcommands():
    """Test command row iteration ignores nonmapping subcommands return values."""
    rows = ListAllCommandsAction.iter_command_rows(NonmappingSubcommandsCli)

    assert rows == []


def test_iter_command_rows_ignores_invalid_subcommand_values():
    """Test command row iteration ignores values that are not CLI classes."""
    rows = ListAllCommandsAction.iter_command_rows(InvalidSubcommandCli)

    assert rows == []


@mark.parametrize(("help_position", "width"), [(24, 80), (12, 50)])
def test_format_command_row_wraps_long_command_description_readably(
    help_position: int, width: int, monkeypatch: MonkeyPatch
):
    """Test long command names do not break description wrapping.

    Arguments:
        help_position: configured description indentation
        width: maximum width for wrapped descriptions
        monkeypatch: fixture for configuring the help layout
    """
    monkeypatch.setattr(ListAllCommandsAction, "help_position", help_position)
    monkeypatch.setattr(ListAllCommandsAction, "width", width)
    command_name = "command-name-that-is-longer-than-the-help-position"
    description = (
        "This long description explains the command in enough detail to require "
        "several wrapped lines while keeping every word readable and in order."
    )
    output = ListAllCommandsAction.format_command_row(
        command_name, description, len(command_name)
    )

    command_line, *description_lines = output.splitlines()
    assert command_line == command_name
    assert len(description_lines) > 1
    assert " ".join(line.strip() for line in description_lines) == description
    assert all(
        len(line) - len(line.lstrip()) == help_position for line in description_lines
    )
    assert all(len(line) <= width for line in description_lines)
