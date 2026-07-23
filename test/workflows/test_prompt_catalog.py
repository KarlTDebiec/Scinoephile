#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the application prompt catalog."""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType

import scinoephile.lang.review.guided as guided_review
import scinoephile.lang.review.standard as review
import scinoephile.lang.transcription.guided as guided_transcription
import scinoephile.lang.translation.gap as gap_translation
import scinoephile.lang.translation.guided as guided_translation
import scinoephile.lang.translation.standard as translation
from scinoephile.core import Language
from scinoephile.lang import ocr_fusion
from scinoephile.optimization.operations import OPERATIONS
from scinoephile.optimization.persistence.prompts import (
    PersistedPrompt,
    PromptSqliteStore,
)
from scinoephile.optimization.persistence.prompts.sync import sync_prompts
from scinoephile.workflows.prompt_catalog import PROMPT_SPECS


def test_prompt_catalog_and_domain_mappings_are_read_only():
    """The composed catalog and source mappings should reject mutation."""
    mappings = (
        PROMPT_SPECS,
        guided_review.DEFAULT_PROMPTS,
        gap_translation.DEFAULT_PROMPTS,
        guided_translation.DEFAULT_PROMPTS,
        translation.DEFAULT_PROMPTS,
        ocr_fusion.DEFAULT_PROMPTS,
        review.DEFAULT_PROMPTS,
        guided_transcription.DEFAULT_SPECS,
    )

    assert all(isinstance(mapping, MappingProxyType) for mapping in mappings)


def test_prompt_catalog_is_stable_and_manager_compatible():
    """Registered prompts should be compatible with their managers."""
    for prompt_spec in PROMPT_SPECS.values():
        assert OPERATIONS[prompt_spec.manager_cls.operation] is prompt_spec.manager_cls
        assert isinstance(prompt_spec.prompt, type(prompt_spec.manager_cls.base_prompt))
        persisted = PersistedPrompt.from_prompt(
            prompt_spec.prompt,
            prompt_spec.manager_cls,
        )
        assert isinstance(persisted.language, Language)


def test_prompt_catalog_contains_registered_transcription_prompts():
    """Each guided transcription spec should contribute its prompts to the catalog."""
    for (
        language,
        reference_language,
    ), spec in guided_transcription.DEFAULT_SPECS.items():
        reference_code = reference_language.language.lower()
        delineation_alias = f"delineation-{language.code.lower()}-vs-{reference_code}"
        punctuation_alias = f"punctuation-{language.code.lower()}-vs-{reference_code}"
        assert PROMPT_SPECS[delineation_alias].prompt is spec.delineation_prompt
        assert PROMPT_SPECS[punctuation_alias].prompt is spec.punctuation_prompt


def test_prompt_catalog_synchronizes(tmp_path: Path):
    """The complete application catalog should synchronize.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"

    report = sync_prompts(PROMPT_SPECS, database_path, dry_run=False)
    store = PromptSqliteStore(database_path)

    assert report.prompt_count == len(PROMPT_SPECS)
    assert report.insert_aliases == tuple(PROMPT_SPECS)
    assert store.get_prompt_by_alias("review-eng")
    assert store.get_prompt_by_alias("translation-yue-hans-to-eng")
