#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Synchronization of registered prompts into SQLite."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from scinoephile.optimization.prompt_spec import PromptSpec

from .persisted_prompt import PersistedPrompt
from .sqlite_store import PromptSqliteStore

__all__ = [
    "PromptSyncReport",
    "sync_prompts",
]


@dataclass(frozen=True, slots=True)
class PromptSyncReport:
    """Summary of a prompt synchronization operation."""

    prompt_count: int
    """Number of prompt aliases included in the synchronization run."""
    insert_aliases: tuple[str, ...]
    """Aliases that would be inserted."""
    update_aliases: tuple[str, ...]
    """Aliases that would be updated to a different prompt."""


def sync_prompts(
    prompt_specs: Mapping[str, PromptSpec],
    output_path: Path,
    *,
    dry_run: bool,
) -> PromptSyncReport:
    """Synchronize registered prompts into SQLite.

    Arguments:
        prompt_specs: registered prompts to synchronize
        output_path: SQLite database output path
        dry_run: if True, report planned changes without writing
    Returns:
        prompt synchronization report
    Raises:
        ScinoephileError: if a prompt is incompatible with its manager
    """
    alias_prompts = {
        alias: PersistedPrompt.from_prompt(
            prompt_spec.prompt,
            prompt_spec.manager_cls,
        )
        for alias, prompt_spec in prompt_specs.items()
    }

    store = PromptSqliteStore(output_path)
    insert_aliases, update_aliases = store.sync_aliases(
        alias_prompts,
        dry_run=dry_run,
    )
    return PromptSyncReport(
        prompt_count=len(alias_prompts),
        insert_aliases=tuple(sorted(insert_aliases)),
        update_aliases=tuple(sorted(update_aliases)),
    )
