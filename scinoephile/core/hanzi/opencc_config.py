#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OpenCC configuration names for hanzi character set conversion."""

from __future__ import annotations

from enum import StrEnum


class OpenCCConfig(StrEnum):
    """OpenCC configuration names for hanzi character set conversion."""

    s2t = "s2t"
    """Simplified Chinese to Traditional Chinese."""
    t2s = "t2s"
    """Traditional Chinese to Simplified Chinese."""
    s2tw = "s2tw"
    """Simplified Chinese to Traditional Chinese (Taiwan)."""
    tw2s = "tw2s"
    """Traditional Chinese (Taiwan) to Simplified Chinese."""
    s2hk = "s2hk"
    """Simplified Chinese to Traditional Chinese (Hong Kong)."""
    hk2s = "hk2s"
    """Traditional Chinese (Hong Kong) to Simplified Chinese."""
    s2twp = "s2twp"
    """Simplified Chinese to Traditional Chinese (Taiwan) with Taiwanese idiom."""
    tw2sp = "tw2sp"
    """Traditional Chinese (Taiwan) to Simplified Chinese with Mainland idiom."""
    t2tw = "t2tw"
    """Traditional Chinese (OpenCC) to Taiwan Standard."""
    hk2t = "hk2t"
    """Traditional Chinese (Hong Kong) to Traditional Chinese."""
    t2hk = "t2hk"
    """Traditional Chinese (OpenCC) to Hong Kong variant."""
    t2jp = "t2jp"
    """Traditional Chinese Characters (Kyūjitai) to New Japanese Kanji (Shinjitai)."""
    jp2t = "jp2t"
    """New Japanese Kanji (Shinjitai) to Traditional Chinese Characters (Kyūjitai)."""
    tw2t = "tw2t"
    """Traditional Chinese (Taiwan) to Traditional Chinese."""
