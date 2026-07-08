#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared types for translation helpers."""

from __future__ import annotations

from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.llms.dual_n_minus_m_to_n import DualNMinusMToNPrompt
from scinoephile.llms.dual_n_to_m import DualNToMPrompt
from scinoephile.llms.mono_n import MonoNPrompt

__all__ = [
    "DualNMinusMToNTranslationProcessorKwargs",
    "DualNToMTranslationProcessorKwargs",
    "MonoNTranslationProcessorKwargs",
]


class DualNMinusMToNTranslationProcessorKwargs(
    ProcessorKwargs,
    total=False,
):
    """Keyword arguments for DualNMinusMToN translation processors."""

    prompt_cls: type[DualNMinusMToNPrompt] | None
    """Prompt class override."""

    test_cases: list[TestCase] | None
    """Test cases."""

    provider: LLMProvider | None
    """Provider to use for queries."""


class MonoNTranslationProcessorKwargs(ProcessorKwargs, total=False):
    """Keyword arguments for MonoN translation processors."""

    prompt_cls: type[MonoNPrompt] | None
    """Prompt class override."""

    test_cases: list[TestCase] | None
    """Test cases."""

    provider: LLMProvider | None
    """Provider to use for queries."""


class DualNToMTranslationProcessorKwargs(ProcessorKwargs, total=False):
    """Keyword arguments for DualNToM translation processors."""

    prompt_cls: type[DualNToMPrompt] | None
    """Prompt class override."""

    test_cases: list[TestCase] | None
    """Test cases."""

    provider: LLMProvider | None
    """Provider to use for queries."""
