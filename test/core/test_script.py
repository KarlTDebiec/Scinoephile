#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of shared script primitives and conversion configuration."""

from __future__ import annotations

from opencc import CONFIGS

from scinoephile.cli.helpers.conversion import OPENCC_CONFIG_LOCALIZATIONS
from scinoephile.core.script import (
    SIMPLIFIED_CONFIGS,
    TRADITIONAL_CONFIGS,
    OpenCCConfig,
)


def test_opencc_config_covers_available_configs():
    """Test the public enum covers every configuration bundled with OpenCC."""
    available_codes = {config.removesuffix(".json") for config in CONFIGS}

    assert {config.code for config in OpenCCConfig} == available_codes


def test_opencc_config_localizations_cover_available_configs():
    """Test each supported locale describes every OpenCC configuration."""
    config_codes = {config.code for config in OpenCCConfig}

    assert set(OPENCC_CONFIG_LOCALIZATIONS) == {"zh-hans", "zh-hant"}
    for localizations in OPENCC_CONFIG_LOCALIZATIONS.values():
        assert set(localizations) == config_codes


def test_opencc_configs_are_classified_by_output_script():
    """Test each OpenCC configuration has one output-script classification."""
    assert SIMPLIFIED_CONFIGS.isdisjoint(TRADITIONAL_CONFIGS)
    assert SIMPLIFIED_CONFIGS | TRADITIONAL_CONFIGS == set(OpenCCConfig)
