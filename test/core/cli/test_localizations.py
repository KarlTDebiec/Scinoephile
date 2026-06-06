#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of CLI localization helpers."""

from __future__ import annotations

from scinoephile.cli.helpers.cache import CACHE_DIR_HELP, CACHE_LOCALIZATIONS
from scinoephile.core.cli.localization import merge_localizations


def test_merge_localizations_merges_locale_text_in_order():
    """Test localization maps merge with later maps taking precedence."""
    shared = {
        "zh-hans": {
            "shared": "共享",
            "override": "共享覆盖",
        },
        "zh-hant": {
            "shared": "共享",
        },
    }
    cli_specific = {
        "zh-hans": {
            "override": "本地覆盖",
            "specific": "本地",
        },
        "zh-hant": {
            "specific": "本地",
        },
    }

    merged = merge_localizations(shared, cli_specific)

    assert merged == {
        "zh-hans": {
            "shared": "共享",
            "override": "本地覆盖",
            "specific": "本地",
        },
        "zh-hant": {
            "shared": "共享",
            "specific": "本地",
        },
    }


def test_merge_localizations_does_not_mutate_inputs():
    """Test localization maps are copied before merging."""
    shared = {"zh-hans": {"shared": "共享"}}
    cli_specific = {"zh-hans": {"specific": "本地"}}

    merged = merge_localizations(shared, cli_specific)
    merged["zh-hans"]["shared"] = "changed"

    assert shared == {"zh-hans": {"shared": "共享"}}
    assert cli_specific == {"zh-hans": {"specific": "本地"}}


def test_merge_localizations_allows_cli_cache_text_override():
    """Test CLI localization maps override shared cache helper text."""
    cli_specific = {
        "zh-hans": {
            CACHE_DIR_HELP: "命令专用缓存目录（默认：%(default)s）",
        },
        "zh-hant": {
            CACHE_DIR_HELP: "命令專用快取目錄（預設：%(default)s）",
        },
    }

    merged = merge_localizations(CACHE_LOCALIZATIONS, cli_specific)

    assert merged["zh-hans"][CACHE_DIR_HELP] == (
        "命令专用缓存目录（默认：%(default)s）"
    )
    assert merged["zh-hant"][CACHE_DIR_HELP] == (
        "命令專用快取目錄（預設：%(default)s）"
    )
