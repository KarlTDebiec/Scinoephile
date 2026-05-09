#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.cli.list_all_commands_action."""

from __future__ import annotations

from scinoephile.common.cli import CommandLineInterface, ListAllCommandsAction


class EmptyCli(CommandLineInterface):
    """Empty CLI for testing command listing."""

    @classmethod
    def _main(cls, **kwargs):
        """Execute with provided keyword arguments."""


class NoncallableSubcommandsCli(CommandLineInterface):
    """CLI with noncallable subcommands for testing command listing."""

    subcommands = {}
    """Noncallable subcommands attribute."""

    @classmethod
    def _main(cls, **kwargs):
        """Execute with provided keyword arguments."""


class NonmappingSubcommandsCli(CommandLineInterface):
    """CLI with nonmapping subcommands for testing command listing."""

    @classmethod
    def subcommands(cls) -> list[str]:
        """Get invalid subcommands."""
        return []

    @classmethod
    def _main(cls, **kwargs):
        """Execute with provided keyword arguments."""


class InvalidSubcommandCli(CommandLineInterface):
    """CLI with invalid subcommand entries for testing command listing."""

    @classmethod
    def subcommands(cls) -> dict[str, object]:
        """Get invalid subcommands."""
        return {"invalid": object()}

    @classmethod
    def _main(cls, **kwargs):
        """Execute with provided keyword arguments."""


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


def test_format_command_row_wraps_long_command_description_readably():
    """Test long command names do not break description wrapping."""
    command_name = "command-name-that-is-longer-than-the-help-position"
    output = ListAllCommandsAction.format_command_row(
        command_name,
        "description text that should stay readable",
        len(command_name),
    )

    assert output.startswith(f"{command_name}\n")
    assert (
        "                        description text that should stay readable" in output
    )
