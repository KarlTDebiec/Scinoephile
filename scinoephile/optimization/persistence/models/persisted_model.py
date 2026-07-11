#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Persisted LLM model configuration."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast
from urllib.parse import parse_qsl, urlsplit

from pydantic import JsonValue

from scinoephile.core.exceptions import ScinoephileError

from .id import get_model_id

__all__ = ["PersistedModel"]


@dataclass(frozen=True, slots=True)
class PersistedModel:
    """An immutable model configuration loaded from SQLite."""

    model_id: str
    """Deterministic identifier derived from the complete model configuration."""
    provider_name: str
    """Stable LLM provider name."""
    model_name: str
    """Provider model identifier."""
    base_url: str | None
    """Effective provider API base URL, if explicitly configured."""
    settings: dict[str, JsonValue]
    """Non-secret inference settings that affect model behavior."""

    @classmethod
    def from_config(
        cls,
        provider_name: str,
        model_name: str,
        *,
        base_url: str | None = None,
        settings: Mapping[str, JsonValue] | None = None,
    ) -> PersistedModel:
        """Create a persisted model from an effective runtime configuration.

        Arguments:
            provider_name: stable LLM provider name
            model_name: resolved provider model identifier
            base_url: effective provider API base URL
            settings: non-secret inference settings
        Returns:
            content-addressed model configuration
        Raises:
            ScinoephileError: if the configuration is empty, invalid, or contains
                credentials
        """
        provider_name = provider_name.strip()
        model_name = model_name.strip()
        if not provider_name:
            raise ScinoephileError("Persisted model provider name must not be empty.")
        if not model_name:
            raise ScinoephileError("Persisted model name must not be empty.")

        if base_url is not None:
            base_url = base_url.strip()
            if not base_url:
                base_url = None
        _validate_base_url(base_url)

        try:
            settings_json = json.dumps(
                dict(settings or {}),
                allow_nan=False,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            loaded_settings: JsonValue = json.loads(settings_json)
        except (TypeError, ValueError) as exc:
            raise ScinoephileError(
                "Persisted model settings must be valid JSON."
            ) from exc
        if not isinstance(loaded_settings, dict):
            raise ScinoephileError("Persisted model settings must be a JSON object.")
        normalized_settings = cast("dict[str, JsonValue]", loaded_settings)
        _validate_no_credentials(normalized_settings)

        return cls(
            model_id=get_model_id(
                provider_name,
                model_name,
                base_url,
                normalized_settings,
            ),
            provider_name=provider_name,
            model_name=model_name,
            base_url=base_url,
            settings=normalized_settings,
        )


def _is_credential_name(name: str) -> bool:
    """Return whether a configuration key appears to contain credentials.

    Arguments:
        name: configuration key name
    Returns:
        whether the name denotes credential material
    """
    compact_name = "".join(
        character for character in name.casefold() if character.isalnum()
    )
    if compact_name == "authorization":
        return True
    return compact_name.endswith(
        (
            "apikey",
            "credential",
            "credentials",
            "password",
            "secret",
            "token",
        )
    )


def _validate_base_url(base_url: str | None):
    """Validate that a base URL does not embed credentials.

    Arguments:
        base_url: effective provider API base URL
    Raises:
        ScinoephileError: if the URL contains credential material
    """
    if base_url is None:
        return
    parsed_url = urlsplit(base_url)
    if parsed_url.username is not None or parsed_url.password is not None:
        raise ScinoephileError("Persisted model base URL must not contain credentials.")
    if any(_is_credential_name(name) for name, _ in parse_qsl(parsed_url.query)):
        raise ScinoephileError(
            "Persisted model base URL must not contain credential query parameters."
        )


def _validate_no_credentials(value: JsonValue, path: str = "settings"):
    """Validate that JSON settings do not contain credential fields.

    Arguments:
        value: JSON value to inspect
        path: dotted path used in errors
    Raises:
        ScinoephileError: if a credential-bearing field is present
    """
    if isinstance(value, dict):
        for name, child in value.items():
            child_path = f"{path}.{name}"
            if _is_credential_name(name):
                raise ScinoephileError(
                    f"Persisted model settings must not contain credentials at "
                    f"{child_path}."
                )
            _validate_no_credentials(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_no_credentials(child, f"{path}[{index}]")
