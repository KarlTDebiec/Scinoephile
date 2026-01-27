#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.argument_parsing."""

from __future__ import annotations

from argparse import ArgumentParser

from common.argument_parsing import (  # ty:ignore[unresolved-import]
    get_arg_groups_by_name,
    get_optional_args_group,
    get_required_args_group,
)


def test_get_optional_args_group():
    """Test retrieving the optional arguments group."""
    parser = ArgumentParser()

    optional_group = get_optional_args_group(parser)
    assert optional_group is not None
    assert optional_group.title in ["optional arguments", "options"]


def test_get_required_args_group_new():
    """Test creating a new required arguments group."""
    parser = ArgumentParser()
    required_group = get_required_args_group(parser)

    assert required_group is not None
    assert required_group.title == "required arguments"


def test_get_required_args_group_existing():
    """Test retrieving an existing required arguments group."""
    parser = ArgumentParser()

    # Create the group first
    first_group = get_required_args_group(parser)

    # Get it again
    second_group = get_required_args_group(parser)

    # Should be the same object
    assert first_group is second_group


def test_get_arg_groups_by_name_new():
    """Test creating new argument groups by name."""
    parser = ArgumentParser()

    groups = get_arg_groups_by_name(
        parser, "input arguments", "operation arguments", "output arguments"
    )

    assert "input arguments" in groups
    assert "operation arguments" in groups
    assert "output arguments" in groups
    assert "optional arguments" in groups


def test_get_arg_groups_by_name_existing():
    """Test getting existing argument groups by name."""
    parser = ArgumentParser()

    # Create groups
    parser.add_argument_group("input arguments")

    groups = get_arg_groups_by_name(parser, "input arguments", "output arguments")

    assert "input arguments" in groups
    assert "output arguments" in groups


def test_get_arg_groups_by_name_order():
    """Test that argument groups are ordered correctly."""
    parser = ArgumentParser()

    get_arg_groups_by_name(parser, "first", "second", "third")

    group_titles = [ag.title for ag in parser._action_groups]

    # Specified groups should come before optional arguments
    first_idx = group_titles.index("first")
    second_idx = group_titles.index("second")
    third_idx = group_titles.index("third")
    optional_idx = group_titles.index("optional arguments")

    assert first_idx < second_idx < third_idx < optional_idx


def test_get_arg_groups_by_name_rename_optional():
    """Test renaming optional arguments group."""
    parser = ArgumentParser()

    groups = get_arg_groups_by_name(
        parser, "input arguments", optional_arguments_name="other arguments"
    )

    assert "other arguments" in groups
    assert "optional arguments" not in groups
