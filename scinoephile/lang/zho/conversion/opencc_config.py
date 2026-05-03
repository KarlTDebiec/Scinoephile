#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OpenCC configuration names for standard Chinese character set conversion."""

from __future__ import annotations

from enum import Enum

__all__ = ["OpenCCConfig"]


class OpenCCConfig(Enum):
    """OpenCC configuration names for standard Chinese character set conversion."""

    _description: str

    s2t = ("s2t", "Simplified Chinese to Traditional Chinese.")
    """Simplified Chinese to Traditional Chinese."""
    t2s = ("t2s", "Traditional Chinese to Simplified Chinese.")
    """Traditional Chinese to Simplified Chinese."""
    s2tw = ("s2tw", "Simplified Chinese to Traditional Chinese (Taiwan).")
    """Simplified Chinese to Traditional Chinese for Taiwan."""
    tw2s = ("tw2s", "Traditional Chinese (Taiwan) to Simplified Chinese.")
    """Traditional Chinese for Taiwan to Simplified Chinese."""
    s2hk = ("s2hk", "Simplified Chinese to Traditional Chinese (Hong Kong).")
    """Simplified Chinese to Traditional Chinese for Hong Kong."""
    hk2s = ("hk2s", "Traditional Chinese (Hong Kong) to Simplified Chinese.")
    """Traditional Chinese for Hong Kong to Simplified Chinese."""
    s2twp = (
        "s2twp",
        "Simplified Chinese to Traditional Chinese (Taiwan) with Taiwanese idiom.",
    )
    """Simplified Chinese to Traditional Chinese for Taiwan with Taiwanese idiom."""
    tw2sp = (
        "tw2sp",
        "Traditional Chinese (Taiwan) to Simplified Chinese with Mainland idiom.",
    )
    """Traditional Chinese for Taiwan to Simplified Chinese with Mainland idiom."""
    t2tw = ("t2tw", "Traditional Chinese (OpenCC) to Taiwan Standard.")
    """Traditional Chinese in OpenCC standard to Taiwan standard."""
    hk2t = ("hk2t", "Traditional Chinese (Hong Kong) to Traditional Chinese.")
    """Traditional Chinese for Hong Kong to Traditional Chinese."""
    t2hk = ("t2hk", "Traditional Chinese (OpenCC) to Hong Kong variant.")
    """Traditional Chinese in OpenCC standard to Hong Kong variant."""
    t2jp = (
        "t2jp",
        "Traditional Chinese Characters (Kyujitai) to New Japanese Kanji (Shinjitai).",
    )
    """Traditional Chinese characters to new Japanese kanji."""
    jp2t = (
        "jp2t",
        "New Japanese Kanji (Shinjitai) to Traditional Chinese Characters (Kyujitai).",
    )
    """New Japanese kanji to traditional Chinese characters."""
    tw2t = ("tw2t", "Traditional Chinese (Taiwan) to Traditional Chinese.")
    """Traditional Chinese for Taiwan to Traditional Chinese."""

    def __new__(cls, code: str, description: str) -> OpenCCConfig:
        """Create enum member with attached description metadata.

        Arguments:
            code: OpenCC configuration code
            description: human-readable description
        """
        member = object.__new__(cls)
        member._value_ = code
        member._description = description
        return member

    @property
    def code(self) -> str:
        """OpenCC configuration code."""
        return self.value

    @property
    def description(self) -> str:
        """Human-readable description of this OpenCC configuration."""
        return self._description

    def __str__(self) -> str:
        """String representation used in CLI/help contexts."""
        return self.value
