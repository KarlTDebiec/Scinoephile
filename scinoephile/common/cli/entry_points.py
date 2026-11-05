#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Discover command-line extensions advertised by installed distributions."""

from __future__ import annotations

from collections.abc import Mapping
from functools import cache
from importlib.metadata import entry_points
from inspect import isabstract

from .command_line_interface import CommandLineInterface

__all__ = ["get_cli_commands"]


def get_cli_commands[T: CommandLineInterface](
    builtins: Mapping[str, type[T]], *, group: str, base_class: type[T]
) -> dict[str, type[T]]:
    """Combine built-in commands with installed CLI extensions.

    Extension classes are loaded once per group and required base class per
    process. Each call returns a fresh registry.

    Arguments:
        builtins: built-in commands whose names extensions cannot replace
        group: package entry-point group to discover
        base_class: required CLI base class for the group
    Returns:
        built-in and extension commands keyed by command name
    Raises:
        ValueError: if an extension cannot load, violates the CLI contract, or
          duplicates a command name
    """
    commands = dict(builtins)
    for name, command, source in _load_cli_commands(group, base_class):
        if name in commands:
            raise ValueError(f"CLI extension {source} duplicates command {name!r}")
        commands[name] = command
    return commands


@cache
def _load_cli_commands[T: CommandLineInterface](
    group: str, base_class: type[T]
) -> tuple[tuple[str, type[T], str], ...]:
    """Load and validate extension classes while retaining their origins.

    Arguments:
        group: package entry-point group to discover
        base_class: required CLI base class for the group
    Returns:
        immutable registrations containing name, CLI class, and source description
    Raises:
        ValueError: if a command cannot load or is not a correctly named concrete
          subclass of the required base class
    """
    commands = []
    for entry in sorted(
        entry_points(group=group), key=lambda item: (item.name, item.value)
    ):
        distribution = "unknown distribution"
        if entry.dist is not None:
            distribution = entry.dist.name
        source = f"{entry.name!r} from {distribution!r} in {group!r}"
        try:
            command = entry.load()
            if (
                not isinstance(command, type)
                or not issubclass(command, base_class)
                or isabstract(command)
            ):
                raise TypeError(f"expected a concrete {base_class.__name__} subclass")
            if not entry.name or command.name() != entry.name:
                raise ValueError("entry-point name must match the CLI class name()")
        except Exception as exc:
            raise ValueError(f"Cannot load CLI extension {source}: {exc}") from exc
        commands.append((entry.name, command, source))
    return tuple(commands)
