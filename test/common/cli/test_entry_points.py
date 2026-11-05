#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for CLI discovery through installed package entry points."""

from __future__ import annotations

from importlib.metadata import EntryPoint
from unittest.mock import patch

import common.cli.entry_points as command_entries
from common.cli import CommandLineInterface
from common.cli.entry_points import get_cli_commands
from pytest import FixtureRequest, fixture, mark, raises


class ExtraCli(CommandLineInterface):
    """Concrete extension command for registration tests."""

    @classmethod
    def _main(cls):
        """Accept a command invocation."""


@fixture
def entry(request: FixtureRequest) -> EntryPoint:
    """Provide a registration with a cache key specific to this test.

    Arguments:
        request: active test case
    """
    return EntryPoint(
        "extra", "extension:ExtraCli", f"test.commands.{request.node.name}"
    )


def test_cache_loads_once_and_returns_independent_registries(entry: EntryPoint):
    """Reuse extension classes without exposing the cached registration collection.

    Arguments:
        entry: registration discovered by both calls
    """
    with (
        patch.object(command_entries, "entry_points", return_value=[entry]),
        patch.object(EntryPoint, "load", return_value=ExtraCli) as load,
    ):
        first = get_cli_commands({}, group=entry.group, base_class=CommandLineInterface)
        first.clear()
        second = get_cli_commands(
            {}, group=entry.group, base_class=CommandLineInterface
        )

    assert second == {"extra": ExtraCli}
    load.assert_called_once_with()


@mark.parametrize("duplicate_builtin", [False, True])
def test_duplicate_names_are_rejected(entry: EntryPoint, duplicate_builtin: bool):
    """Reject extension collisions with built-ins and other extensions.

    Arguments:
        entry: registration that collides with another command
        duplicate_builtin: whether the conflicting name belongs to a built-in
    """
    entries = [entry, entry]
    builtins = {}
    if duplicate_builtin:
        entries = [entry]
        builtins = {"extra": ExtraCli}

    with (
        patch.object(command_entries, "entry_points", return_value=entries),
        patch.object(EntryPoint, "load", return_value=ExtraCli),
        raises(ValueError, match="duplicates command 'extra'"),
    ):
        get_cli_commands(builtins, group=entry.group, base_class=CommandLineInterface)


def test_entry_point_name_must_match_command_name(entry: EntryPoint):
    """Use the same name for parser registration and execution lookup.

    Arguments:
        entry: registration providing an isolated group
    """
    mismatched = EntryPoint("different", entry.value, entry.group)
    with (
        patch.object(command_entries, "entry_points", return_value=[mismatched]),
        patch.object(EntryPoint, "load", return_value=ExtraCli),
        raises(ValueError, match="name must match"),
    ):
        get_cli_commands({}, group=entry.group, base_class=CommandLineInterface)


def test_load_failure_retains_context(entry: EntryPoint):
    """Identify a broken registration and preserve the original import failure.

    Arguments:
        entry: registration that fails to load
    """
    failure = ModuleNotFoundError("missing extension dependency")
    with (
        patch.object(command_entries, "entry_points", return_value=[entry]),
        patch.object(EntryPoint, "load", side_effect=failure),
        raises(ValueError) as raised,
    ):
        get_cli_commands({}, group=entry.group, base_class=CommandLineInterface)

    assert raised.value.__cause__ is failure
    assert entry.name in str(raised.value)
    assert entry.group in str(raised.value)
    assert str(failure) in str(raised.value)


def test_no_extensions_preserves_builtins(entry: EntryPoint):
    """Keep built-in commands available without installed extensions.

    Arguments:
        entry: registration providing an isolated group
    """
    builtins = {"extra": ExtraCli}
    with patch.object(command_entries, "entry_points", return_value=[]):
        commands = get_cli_commands(
            builtins, group=entry.group, base_class=CommandLineInterface
        )

    assert commands == builtins
    assert commands is not builtins


def test_required_base_is_checked_after_caching(entry: EntryPoint):
    """Keep base-class validation specific to each registry's required contract.

    Arguments:
        entry: registration used with both base classes
    """

    class RequiredCli(ExtraCli):
        """More specific contract required by one of the registries."""

    with (
        patch.object(command_entries, "entry_points", return_value=[entry]),
        patch.object(EntryPoint, "load", return_value=ExtraCli),
    ):
        get_cli_commands({}, group=entry.group, base_class=CommandLineInterface)
        with raises(ValueError, match="concrete RequiredCli subclass"):
            get_cli_commands({}, group=entry.group, base_class=RequiredCli)


@mark.parametrize("loaded", [None, object, ExtraCli(), CommandLineInterface])
def test_wrong_or_abstract_types_are_rejected(entry: EntryPoint, loaded: object):
    """Require a concrete CLI class.

    Arguments:
        entry: registration that loads an invalid object
        loaded: invalid object returned by an entry point
    """
    with (
        patch.object(command_entries, "entry_points", return_value=[entry]),
        patch.object(EntryPoint, "load", return_value=loaded),
        raises(ValueError, match="concrete CommandLineInterface subclass"),
    ):
        get_cli_commands({}, group=entry.group, base_class=CommandLineInterface)
