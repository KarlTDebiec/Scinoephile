#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for guided transcription configuration and construction."""

from __future__ import annotations

from typing import cast
from unittest.mock import Mock

from pytest import raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.lang.transcription.guided import (
    DEFAULT_LANGUAGE_SPECS,
    DEFAULT_SPECS,
    get_guided_transcriber,
)
from scinoephile.lang.yue_zho.transcription import (
    YueZhoDelineationPromptYueHant,
    YueZhoPunctuationPromptYueHant,
)


def test_default_specs_are_read_only_and_cover_yue_zho_scripts():
    """Test default specs cover both scripts for target and reference Chinese."""
    assert set(DEFAULT_LANGUAGE_SPECS) == {Language.yue_hans, Language.yue_hant}
    assert (
        DEFAULT_LANGUAGE_SPECS[Language.yue_hans]
        is DEFAULT_LANGUAGE_SPECS[Language.yue_hant]
    )
    assert set(DEFAULT_SPECS) == {
        (Language.yue_hans, Language.zho_hans),
        (Language.yue_hans, Language.zho_hant),
        (Language.yue_hant, Language.zho_hans),
        (Language.yue_hant, Language.zho_hant),
    }
    assert {language for language, _ in DEFAULT_SPECS} <= DEFAULT_LANGUAGE_SPECS.keys()
    assert (
        DEFAULT_SPECS[(Language.yue_hans, Language.zho_hans)]
        is DEFAULT_SPECS[(Language.yue_hans, Language.zho_hant)]
    )
    assert (
        DEFAULT_SPECS[(Language.yue_hant, Language.zho_hans)]
        is DEFAULT_SPECS[(Language.yue_hant, Language.zho_hant)]
    )
    mutable_specs = cast(dict, DEFAULT_SPECS)
    with raises(TypeError):
        mutable_specs[(Language.eng, Language.zho_hans)] = DEFAULT_SPECS[
            (Language.yue_hans, Language.zho_hans)
        ]
    mutable_language_specs = cast(dict, DEFAULT_LANGUAGE_SPECS)
    with raises(TypeError):
        mutable_language_specs[Language.eng] = DEFAULT_LANGUAGE_SPECS[Language.yue_hans]


def test_get_guided_transcriber_uses_registered_language_configuration(tmp_path):
    """Test factory configures language-specific prompts and Whisper language."""
    transcriber = get_guided_transcriber(
        Language.yue_hant,
        Language.zho_hans,
        provider=Mock(spec=LLMProvider),
        test_case_dir_path=tmp_path,
        delineation_test_cases=[],
        punctuation_test_cases=[],
    )

    assert transcriber.language is Language.yue_hant
    assert transcriber.reference_language is Language.zho_hans
    assert transcriber.whisper_language == "yue"
    assert transcriber.segment_splitter is not None
    assert transcriber.aligner.delineation_queryer.prompt is (
        YueZhoDelineationPromptYueHant
    )
    assert transcriber.aligner.punctuation_queryer.prompt is (
        YueZhoPunctuationPromptYueHant
    )
    assert transcriber.vad_transcriber is not None
    assert transcriber.vad_transcriber.language == "yue"
    assert transcriber.no_vad_transcriber is not None
    assert transcriber.no_vad_transcriber.language == "yue"
    assert (tmp_path / "delineation").is_dir()
    assert (tmp_path / "punctuation").is_dir()


def test_get_guided_transcriber_rejects_unsupported_language_pair():
    """Test factory rejects language pairs absent from the registry."""
    with raises(ScinoephileError, match="eng <- zho-Hans"):
        get_guided_transcriber(Language.eng, Language.zho_hans)
