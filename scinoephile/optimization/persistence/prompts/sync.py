#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Synchronization of registered zero-shot prompts into SQLite."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.optimization.prompt_specs import PromptSpec

from .persisted_prompt import PersistedPrompt
from .sqlite_store import PromptSqliteStore

__all__ = [
    "PromptSyncReport",
    "sync_prompts",
]


@dataclass(frozen=True, slots=True)
class PromptSyncReport:
    """Summary of a prompt synchronization operation."""

    aliases: tuple[str, ...]
    """Prompt aliases included in the synchronization run."""
    insert_ids: tuple[str, ...]
    """Prompt identifiers that would be inserted."""
    insert_aliases: tuple[str, ...]
    """Aliases that would be inserted."""
    update_aliases: tuple[str, ...]
    """Aliases that would be updated to a different prompt."""


def sync_prompts(
    prompt_specs: Iterable[PromptSpec],
    output_path: Path,
    *,
    dry_run: bool,
) -> PromptSyncReport:
    """Synchronize registered zero-shot prompts into SQLite.

    Arguments:
        prompt_specs: registered prompts to synchronize
        output_path: SQLite database output path
        dry_run: if True, report planned changes without writing
    Returns:
        prompt synchronization report
    Raises:
        ScinoephileError: if a prompt alias is provided more than once
    """
    alias_prompts: dict[str, PersistedPrompt] = {}
    for prompt_spec in prompt_specs:
        if prompt_spec.alias in alias_prompts:
            raise ScinoephileError(
                f"Prompt alias {prompt_spec.alias} was provided more than once."
            )
        alias_prompts[prompt_spec.alias] = PersistedPrompt.from_prompt_cls(
            prompt_spec.prompt_cls,
            prompt_spec.manager_cls,
        )

    store = PromptSqliteStore(output_path)
    insert_ids, insert_aliases, update_aliases = store.sync_aliases(
        alias_prompts,
        dry_run=dry_run,
    )
    return PromptSyncReport(
        aliases=tuple(sorted(alias_prompts)),
        insert_ids=tuple(sorted(insert_ids)),
        insert_aliases=tuple(sorted(insert_aliases)),
        update_aliases=tuple(sorted(update_aliases)),
    )
