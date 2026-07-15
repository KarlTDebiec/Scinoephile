#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for prompt metadata ownership and content-addressed identities."""

from __future__ import annotations

import hashlib
import json
from dataclasses import fields
from pathlib import Path
from typing import Any, Final, cast
from unittest.mock import Mock

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, Manager, Prompt, Queryer
from scinoephile.llms.guided_review import GuidedReviewManager, GuidedReviewPrompt
from scinoephile.llms.pairwise_review import PairwiseReviewManager, PairwiseReviewPrompt
from scinoephile.llms.review import ReviewManager, ReviewPrompt
from scinoephile.workflows.prompt_catalog import PROMPT_SPECS

_LEGACY_TEST_CASE_PROMPT_FIELDS: Final = {
    "difficulty_description": (
        "Difficulty level of the test case, used for filtering."
    ),
    "few_shot_description": "Whether to include test case in few-shot examples.",
    "verified_description": (
        "Whether to include test case in the verified answers cache."
    ),
}
"""Prompt fields removed when test-case metadata became static."""


def test_registered_prompt_model_and_cache_identities_change_once(
    tmp_path: Path,
):
    """Removing metadata should change prompt, model, and cache identities."""
    provider = Mock(spec=LLMProvider)
    provider.cache_identity = {"implementation": "test.provider"}

    for manager_cls, prompt in _get_registered_prompts():
        legacy_prompt = _get_legacy_prompt(prompt)
        test_case_cls = manager_cls.get_test_case_cls(prompt)
        legacy_test_case_cls = manager_cls.get_test_case_cls(legacy_prompt)

        assert prompt.name != legacy_prompt.name
        assert test_case_cls.__name__ != legacy_test_case_cls.__name__
        assert (
            test_case_cls.query_cls.__name__ != legacy_test_case_cls.query_cls.__name__
        )
        assert (
            test_case_cls.answer_cls.__name__
            != legacy_test_case_cls.answer_cls.__name__
        )

        queryer = Queryer(test_case_cls, provider=provider)
        legacy_queryer = Queryer(legacy_test_case_cls, provider=provider)
        system_prompt = queryer.system_prompt
        legacy_system_prompt = legacy_queryer.system_prompt

        assert system_prompt == legacy_system_prompt

        queryer.cache_dir_path = tmp_path
        legacy_queryer.cache_dir_path = tmp_path
        tools_json = queryer.tool_box.to_json()
        query_json = '{"same":"query"}'
        cache_path = queryer._get_cache_path(system_prompt, tools_json, query_json)
        legacy_cache_path = legacy_queryer._get_cache_path(
            legacy_system_prompt,
            tools_json,
            query_json,
        )

        assert cache_path is not None
        assert legacy_cache_path is not None
        assert cache_path != legacy_cache_path


def test_registered_query_and_answer_schemas_change_only_model_identifiers():
    """Prompt hash changes should leave every correspondence schema structural."""
    for manager_cls, prompt in _get_registered_prompts():
        legacy_prompt = _get_legacy_prompt(prompt)
        test_case_cls = manager_cls.get_test_case_cls(prompt)
        legacy_test_case_cls = manager_cls.get_test_case_cls(legacy_prompt)

        schema_pairs = [
            (
                test_case_cls.query_cls.model_json_schema(by_alias=True),
                legacy_test_case_cls.query_cls.model_json_schema(by_alias=True),
            ),
            (
                test_case_cls.answer_cls.model_json_schema(by_alias=True),
                legacy_test_case_cls.answer_cls.model_json_schema(by_alias=True),
            ),
        ]
        for schema, legacy_schema in schema_pairs:
            assert schema != legacy_schema
            assert json.dumps(
                _normalize_schema_identifiers(schema),
                ensure_ascii=False,
                separators=(",", ":"),
            ) == json.dumps(
                _normalize_schema_identifiers(legacy_schema),
                ensure_ascii=False,
                separators=(",", ":"),
            )


def test_registered_review_prompts_specify_note_language():
    """Review prompts should request notes in the reviewed subtitle language."""
    note_language_markers = {
        Language.eng: "English",
        Language.yue_hans: "粤文",
        Language.yue_hant: "粵文",
        Language.zho_hans: "中文",
        Language.zho_hant: "中文",
    }
    review_manager_classes = {
        GuidedReviewManager,
        PairwiseReviewManager,
        ReviewManager,
    }

    for alias, prompt_spec in PROMPT_SPECS.items():
        if prompt_spec.manager_cls not in review_manager_classes:
            continue
        review_prompt = cast(
            "GuidedReviewPrompt | PairwiseReviewPrompt | ReviewPrompt",
            prompt_spec.prompt,
        )
        note_language = note_language_markers[review_prompt.language]
        assert note_language in review_prompt.base_system_prompt, alias
        assert note_language in review_prompt.note_desc, alias


def _get_legacy_prompt(prompt: Prompt) -> Prompt:
    """Get an equivalent prompt using its identity before metadata removal.

    Arguments:
        prompt: current prompt
    Returns:
        equivalent prompt whose name includes the removed metadata fields
    """
    prompt_cls = type(prompt)
    legacy_prompt_cls = cast(
        "type[Prompt]",
        type(
            prompt_cls.__name__,
            (prompt_cls,),
            {
                "__module__": prompt_cls.__module__,
                "name": property(_get_legacy_prompt_name),
            },
        ),
    )
    prompt_fields = {
        field.name: getattr(prompt, field.name) for field in fields(prompt)
    }
    return legacy_prompt_cls(**prompt_fields)


def _get_legacy_prompt_name(prompt: Prompt) -> str:
    """Get a prompt's content-addressed name before metadata removal.

    Arguments:
        prompt: prompt whose name should be calculated
    Returns:
        legacy content-addressed name
    """
    prompt_fields = {
        field.name: getattr(prompt, field.name)
        for field in fields(prompt)
        if field.name != "language"
    }
    prompt_fields.update(_LEGACY_TEST_CASE_PROMPT_FIELDS)
    payload_json = json.dumps(
        {
            "fields": prompt_fields,
            "language": prompt.language.code,
            "type": type(prompt).__name__,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    digest = hashlib.sha256(payload_json.encode()).hexdigest()[:12]
    language_name = prompt.language.code.replace("-", "_")
    return f"{type(prompt).__name__}_{language_name}_{digest}"


def _get_registered_prompts() -> list[tuple[type[Manager], Prompt]]:
    """Get unique registered manager and prompt pairs.

    Returns:
        registered manager and prompt pairs in deterministic order
    """
    prompt_pairs = {
        (prompt_spec.manager_cls, prompt_spec.prompt)
        for prompt_spec in PROMPT_SPECS.values()
    }
    return sorted(
        prompt_pairs,
        key=lambda pair: (pair[0].operation, pair[1].name),
    )


def _normalize_schema_identifiers(schema: dict[str, Any]) -> dict[str, Any]:
    """Normalize content-addressed model identifiers in a JSON schema.

    Field titles remain unchanged; only root/definition model titles, definition keys,
    and references to those definitions are normalized.

    Arguments:
        schema: Pydantic JSON schema
    Returns:
        schema with content-addressed model identifiers normalized
    """
    definitions = schema.get("$defs", {})
    assert isinstance(definitions, dict)
    definition_names = {
        name: f"definition_{idx}" for idx, name in enumerate(definitions)
    }
    title_names = dict(definition_names)
    root_title = schema.get("title")
    if isinstance(root_title, str):
        title_names[root_title] = "root"

    def normalize(value: Any) -> Any:
        """Normalize schema identifiers recursively.

        Arguments:
            value: schema value
        Returns:
            normalized schema value
        """
        if isinstance(value, dict):
            normalized: dict[str, Any] = {}
            for key, child in value.items():
                if key == "$defs":
                    normalized[key] = {
                        definition_names[name]: normalize(definition)
                        for name, definition in child.items()
                    }
                elif key == "title" and child in title_names:
                    normalized[key] = title_names[child]
                else:
                    normalized[key] = normalize(child)
            return normalized
        if isinstance(value, list):
            return [normalize(child) for child in value]
        if isinstance(value, str) and value.startswith("#/$defs/"):
            definition_name = value.removeprefix("#/$defs/")
            return f"#/$defs/{definition_names[definition_name]}"
        return value

    return normalize(schema)
