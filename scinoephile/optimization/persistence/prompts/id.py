#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Identifiers for persisted LLM prompts."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping

from scinoephile.core import Language

__all__ = ["get_prompt_id"]


def get_prompt_id(
    attributes: Mapping[str, str] | Iterable[tuple[str, str]],
    operation: str,
    language: Language,
) -> str:
    """Compute a canonical identifier for a prompt.

    Arguments:
        attributes: effective prompt attributes
        operation: stable operation identifier
        language: language in which the prompt corresponds with the LLM
    Returns:
        deterministic hexadecimal identifier
    """
    payload_json = json.dumps(
        {
            "attributes": dict(attributes),
            "language": language.code,
            "operation": operation,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(payload_json.encode()).hexdigest()
