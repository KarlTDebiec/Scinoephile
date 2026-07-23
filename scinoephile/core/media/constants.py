#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core media constants."""

from __future__ import annotations

__all__ = ["SUBTITLE_CODEC_OUTPUTS"]

SUBTITLE_CODEC_OUTPUTS = {
    "ass": ("ass", "ass"),
    "dvd_subtitle": ("sub", "copy"),
    "eia_608": ("srt", "subrip"),
    "hdmv_pgs_subtitle": ("sup", "copy"),
    "mov_text": ("srt", "subrip"),
    "ssa": ("ssa", "ass"),
    "subrip": ("srt", "subrip"),
    "webvtt": ("vtt", "webvtt"),
    "xsub": ("divx", "copy"),
}
"""Mapping from ffmpeg subtitle codec names to output extensions and codecs."""
