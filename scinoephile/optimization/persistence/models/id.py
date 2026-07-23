#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Identifiers for persisted LLM model configurations."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping

from pydantic import JsonValue

__all__ = ["get_model_id"]


def get_model_id(
    provider_name: str,
    model_name: str,
    base_url: str | None,
    settings: Mapping[str, JsonValue],
) -> str:
    """Compute a canonical identifier for a model configuration.

    Arguments:
        provider_name: stable LLM provider name
        model_name: provider model identifier
        base_url: effective provider API base URL
        settings: non-secret inference settings
    Returns:
        deterministic hexadecimal identifier
    """
    payload_json = json.dumps(
        {
            "base_url": base_url,
            "model": model_name,
            "provider": provider_name,
            "settings": dict(settings),
        },
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(payload_json.encode()).hexdigest()
