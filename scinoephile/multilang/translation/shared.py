#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared helpers for translation processors."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.dictionaries import DictionaryToolPrompt
from scinoephile.core.llms import LLMProvider, OperationSpec, Prompt, TestCase, ToolBox
from scinoephile.dictionaries.dictionary_tools import get_dictionary_tools
from scinoephile.llms.default_test_cases import load_default_test_cases
from scinoephile.llms.dual_n_minus_m_to_n import (
    DualNMinusMToNProcessor,
    DualNMinusMToNPrompt,
)
from scinoephile.llms.dual_n_to_m import DualNToMProcessor, DualNToMPrompt
from scinoephile.llms.providers.registry import get_provider

__all__ = [
    "TranslationRoute",
    "get_dual_n_minus_m_to_n_processor",
    "get_dual_n_to_m_processor",
    "get_route",
]

type TranslationRoute = tuple[tuple[Path, ...], type[Prompt]]
"""Route metadata for a supported translation pair."""


def get_dual_n_minus_m_to_n_processor(
    operation_spec: OperationSpec,
    route: TranslationRoute,
    *,
    prompt_cls: type[DualNMinusMToNPrompt] | None,
    test_cases: list[TestCase] | None,
    use_dictionary_tool: bool,
    provider: LLMProvider | None,
    test_case_path: Path | None,
    additional_context: str | None,
    auto_verify: bool,
) -> DualNMinusMToNProcessor:
    """Get a DualNMinusMToNProcessor from route and caller configuration."""
    json_paths, route_prompt_cls = route
    selected_prompt_cls = prompt_cls
    if selected_prompt_cls is None:
        selected_prompt_cls = cast(type[DualNMinusMToNPrompt], route_prompt_cls)
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                operation_spec.manager_cls,
                selected_prompt_cls,
                json_paths,
            )
        )
    if provider is None:
        provider = get_provider()
    return DualNMinusMToNProcessor(
        prompt_cls=selected_prompt_cls,
        test_cases=test_cases,
        test_case_path=test_case_path,
        provider=provider,
        additional_context=additional_context,
        auto_verify=auto_verify,
        tool_box=_get_tool_box(selected_prompt_cls, use_dictionary_tool),
    )


def get_dual_n_to_m_processor(
    operation_spec: OperationSpec,
    route: TranslationRoute,
    *,
    prompt_cls: type[DualNToMPrompt] | None,
    test_cases: list[TestCase] | None,
    use_dictionary_tool: bool,
    provider: LLMProvider | None,
    test_case_path: Path | None,
    additional_context: str | None,
    auto_verify: bool,
) -> DualNToMProcessor:
    """Get a DualNToMProcessor from route and caller configuration."""
    json_paths, route_prompt_cls = route
    selected_prompt_cls = prompt_cls
    if selected_prompt_cls is None:
        selected_prompt_cls = cast(type[DualNToMPrompt], route_prompt_cls)
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                operation_spec.manager_cls,
                selected_prompt_cls,
                json_paths,
            )
        )
    if provider is None:
        provider = get_provider()
    return DualNToMProcessor(
        prompt_cls=selected_prompt_cls,
        test_cases=test_cases,
        test_case_path=test_case_path,
        provider=provider,
        additional_context=additional_context,
        auto_verify=auto_verify,
        tool_box=_get_tool_box(selected_prompt_cls, use_dictionary_tool),
    )


def get_route(
    routes: dict[tuple[Language, Language], TranslationRoute],
    source_language: Language,
    target_language: Language,
) -> TranslationRoute:
    """Get the route for a supported source and target language."""
    route = routes.get((source_language, target_language))
    if route is None:
        raise ScinoephileError(
            f"Unsupported translation pair: {source_language.tag} to "
            f"{target_language.tag}"
        )
    return route


def _get_tool_box(
    prompt_cls: type[Prompt],
    use_dictionary_tool: bool,
) -> ToolBox | None:
    """Get dictionary tools for compatible prompts when requested."""
    if not use_dictionary_tool:
        return None
    if not _has_dictionary_tool_prompt(prompt_cls):
        return None
    return get_dictionary_tools(cast(type[DictionaryToolPrompt], prompt_cls))


def _has_dictionary_tool_prompt(prompt_cls: type[Prompt]) -> bool:
    """Return whether a prompt class provides dictionary tool text."""
    return (
        hasattr(prompt_cls, "dictionary_tool_name")
        and hasattr(prompt_cls, "dictionary_tool_description")
        and hasattr(prompt_cls, "dictionary_tool_query_description")
    )
