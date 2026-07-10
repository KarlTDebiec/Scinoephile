#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for LLM operation specifications."""

from __future__ import annotations

from pytest import raises

from scinoephile.core.llms import Manager, OperationSpec, Prompt


class _Manager(Manager):
    """Manager with a base prompt for operation-spec tests."""

    prompt_cls = Prompt


def test_operation_spec_uses_manager_base_prompt():
    """Operation specifications should expose their manager's base prompt."""
    spec = OperationSpec("test", _Manager)

    assert spec.prompt_cls is Prompt


def test_operation_spec_rejects_blank_operation():
    """Operation names should not be empty or contain only whitespace."""
    for operation in ("", " "):
        with raises(ValueError, match="must not be empty"):
            OperationSpec(operation, Manager)


def test_operation_spec_rejects_surrounding_whitespace():
    """Operation names should not contain surrounding whitespace."""
    for operation in (" translation", "translation "):
        with raises(ValueError, match="leading or trailing whitespace"):
            OperationSpec(operation, Manager)
