#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Provider composition layer for LLM integrations outside `scinoephile.core`.

Package hierarchy (modules may import from any above):
* deepseek_provider / openai_provider / registry
"""

from __future__ import annotations

from typing import TYPE_CHECKING

__all__ = [
    "DeepSeekProvider",
    "OpenAIProvider",
]

if TYPE_CHECKING:
    from .deepseek_provider import DeepSeekProvider
    from .openai_provider import OpenAIProvider


def __getattr__(name: str) -> object:
    """Import provider classes on demand.

    Arguments:
        name: requested module attribute name
    Returns:
        requested provider class
    Raises:
        AttributeError: if the requested attribute is not exported here
    """
    if name == "DeepSeekProvider":
        from .deepseek_provider import DeepSeekProvider  # noqa: PLC0415

        return DeepSeekProvider
    if name == "OpenAIProvider":
        from .openai_provider import OpenAIProvider  # noqa: PLC0415

        return OpenAIProvider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
