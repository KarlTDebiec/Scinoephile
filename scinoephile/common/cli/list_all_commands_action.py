#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Argparse action for listing a complete command hierarchy."""

from __future__ import annotations

import sys
from argparse import Action, ArgumentParser, Namespace
from collections.abc import Callable
from textwrap import fill
from typing import Any

from .command_line_interface import CommandLineInterface

__all__ = ["ListAllCommandsAction"]


class ListAllCommandsAction(Action):
    """Print all subcommands beneath a root CLI class and exit."""

    help_position = 24
    """Column at which command descriptions begin."""
    width = 80
    """Maximum output width."""
    root_cli_class: type[CommandLineInterface]
    """CLI class whose subcommand hierarchy should be listed."""

    def __init__(
        self,
        option_strings: list[str],
        dest: str,
        *,
        root_cli_class: type[CommandLineInterface],
        **kwargs: Any,
    ):
        """Initialize.

        Arguments:
            option_strings: option strings
            dest: argparse destination name
            root_cli_class: CLI class whose subcommands should be listed
            **kwargs: additional keyword arguments
        """
        kwargs.setdefault("nargs", 0)
        super().__init__(option_strings=option_strings, dest=dest, **kwargs)
        self.root_cli_class = root_cli_class

    def __call__(  # noqa: PLR6301
        self,
        parser: ArgumentParser,
        namespace: Namespace,  # noqa: ARG002
        values: object,  # noqa: ARG002
        option_string: str | None = None,  # noqa: ARG002
    ):
        """Handle the action.

        Arguments:
            parser: active argument parser
            namespace: parsed namespace
            values: parsed argument value
            option_string: option string used
        """
        parser._print_message(  # noqa: SLF001
            f"{self.format_all_commands(self.root_cli_class)}\n",
            sys.stdout,
        )
        parser.exit(0)

    @staticmethod
    def format_all_commands(root_cli_class: type[CommandLineInterface]) -> str:
        """Format all subcommands for CLI output.

        Arguments:
            root_cli_class: CLI class whose subcommands should be listed
        Returns:
            formatted command hierarchy
        """
        rows = list(ListAllCommandsAction.iter_command_rows(root_cli_class))
        command_width = max(len(command_name) for command_name, _ in rows)
        heading = ListAllCommandsAction.translate_text(
            root_cli_class, "Available subcommands:"
        )
        lines = [heading, ""]
        lines.extend(
            ListAllCommandsAction.format_command_row(
                command_name, description, command_width
            )
            for command_name, description in rows
        )
        return "\n".join(lines)

    @staticmethod
    def iter_command_rows(
        cli: type[CommandLineInterface],
        level: int = 0,
    ) -> list[tuple[str, str]]:
        """Get all command names and descriptions below a CLI.

        Arguments:
            cli: CLI class to inspect
            level: indentation level of subcommands below the CLI
        Returns:
            command names paired with short descriptions
        """
        rows: list[tuple[str, str]] = []
        subcommands = getattr(cli, "subcommands", None)
        if subcommands is None:
            return rows

        for name, subcommand in sorted(subcommands().items()):
            command_name = f"{' ' * (4 * level)}{name}"
            rows.append(
                (
                    command_name,
                    ListAllCommandsAction.format_command_description(subcommand.help()),
                )
            )
            rows.extend(ListAllCommandsAction.iter_command_rows(subcommand, level + 1))
        return rows

    @staticmethod
    def format_command_description(description: str) -> str:
        """Format a command description for a single-line command list.

        Arguments:
            description: raw command description
        Returns:
            first non-empty line from the description
        """
        for line in description.splitlines():
            stripped_line = line.strip()
            if stripped_line:
                return stripped_line
        return ""

    @staticmethod
    def format_command_row(
        command_name: str,
        description: str,
        command_width: int,
    ) -> str:
        """Format one command row with wrapped description text.

        Arguments:
            command_name: command name with indentation
            description: single-line command description
            command_width: width of the command column
        Returns:
            formatted command row
        """
        command_column_width = max(
            command_width,
            ListAllCommandsAction.help_position - 2,
        )
        if len(command_name) > command_column_width:
            command_line = command_name
            description_indent = " " * ListAllCommandsAction.help_position
            description_lines = fill(
                description,
                width=ListAllCommandsAction.width,
                initial_indent=description_indent,
                subsequent_indent=description_indent,
            )
            return f"{command_line}\n{description_lines}"

        return fill(
            description,
            width=ListAllCommandsAction.width,
            initial_indent=f"{command_name:<{command_column_width}}  ",
            subsequent_indent=" " * ListAllCommandsAction.help_position,
        )

    @staticmethod
    def translate_text(root_cli_class: type[CommandLineInterface], text: str) -> str:
        """Translate text through a root CLI class when supported.

        Arguments:
            root_cli_class: CLI class that may provide a translation method
            text: source text
        Returns:
            translated text when the CLI class supports localization
        """
        translate_text = getattr(root_cli_class, "translate_text", None)
        if not isinstance(translate_text, Callable):
            return text
        translated_text = translate_text(text)
        if not isinstance(translated_text, str):
            return text
        return translated_text
