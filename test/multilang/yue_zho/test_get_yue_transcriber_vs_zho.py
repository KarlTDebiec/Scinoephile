#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of get_yue_vs_zho_transcriber."""

from __future__ import annotations

from typing import cast
from unittest.mock import ANY, Mock, patch

from scinoephile.common.file import get_temp_directory_path
from scinoephile.core.llms import TestCase
from scinoephile.multilang.yue_zho.transcription import get_yue_vs_zho_transcriber
from scinoephile.multilang.yue_zho.transcription.deliniation import (
    YueZhoHansDeliniationPrompt,
)
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YueZhoHansPunctuationPrompt,
)


def test_get_yue_vs_zho_transcriber_uses_writable_runtime_test_case_root():
    """Test default transcriber setup uses a writable runtime test-case root."""
    deliniation_test_cases = [cast(TestCase, Mock())]
    punctuation_test_cases = [cast(TestCase, Mock())]

    with get_temp_directory_path() as temp_dir_path:
        runtime_test_case_dir_path = temp_dir_path / "test_cases"
        with patch(
            "scinoephile.multilang.yue_zho.transcription.get_runtime_cache_dir_path",
            return_value=runtime_test_case_dir_path,
        ):
            with patch(
                "scinoephile.multilang.yue_zho.transcription.YueTranscriber"
            ) as patched_transcriber:
                get_yue_vs_zho_transcriber(
                    deliniation_test_cases=deliniation_test_cases,
                    punctuation_test_cases=punctuation_test_cases,
                )
        patched_transcriber.assert_called_once_with(
            test_case_directory_path=runtime_test_case_dir_path,
            deliniation_test_cases=deliniation_test_cases,
            punctuation_test_cases=punctuation_test_cases,
            deliniation_prompt_cls=YueZhoHansDeliniationPrompt,
            punctuation_prompt_cls=YueZhoHansPunctuationPrompt,
            provider=ANY,
        )
        assert (
            runtime_test_case_dir_path
            / "multilang"
            / "yue_zho"
            / "transcription"
            / "deliniation"
        ).is_dir()
        assert (
            runtime_test_case_dir_path
            / "multilang"
            / "yue_zho"
            / "transcription"
            / "punctuation"
        ).is_dir()
