#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of get_yue_vs_zho_transcriber."""

from __future__ import annotations

from pathlib import Path
from typing import cast
from unittest.mock import ANY, Mock, patch

from scinoephile.common.file import get_temp_directory_path
from scinoephile.core.llms import TestCase
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.llms.default_test_cases import (
    YUE_ZHO_TRANSCRIPTION_DELINIATION_JSON_PATHS,
    YUE_ZHO_TRANSCRIPTION_PUNCTUATION_JSON_PATHS,
)
from scinoephile.multilang.yue_zho.transcription import (
    DemucsMode,
    VADMode,
    get_yue_vs_zho_transcriber,
)
from scinoephile.multilang.yue_zho.transcription.deliniation import (
    YueVsZhoYueHansDeliniationPrompt,
)
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YueVsZhoYueHansPunctuationPrompt,
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
            model_name="khleeloo/whisper-large-v3-cantonese",
            demucs_mode=DemucsMode.OFF,
            vad_mode=VADMode.AUTO,
            convert=None,
            deliniation_prompt_cls=YueVsZhoYueHansDeliniationPrompt,
            punctuation_prompt_cls=YueVsZhoYueHansPunctuationPrompt,
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


def test_get_yue_vs_zho_transcriber_passes_model_name():
    """Test transcriber factory forwards an explicit Whisper model name."""
    deliniation_test_cases = [cast(TestCase, Mock())]
    punctuation_test_cases = [cast(TestCase, Mock())]

    with get_temp_directory_path() as temp_dir_path:
        with patch(
            "scinoephile.multilang.yue_zho.transcription.YueTranscriber"
        ) as patched_transcriber:
            get_yue_vs_zho_transcriber(
                deliniation_test_cases=deliniation_test_cases,
                punctuation_test_cases=punctuation_test_cases,
                test_case_directory_path=temp_dir_path,
                model_name="custom/model",
            )

    assert patched_transcriber.call_args.kwargs["model_name"] == "custom/model"


def test_get_yue_vs_zho_transcriber_passes_demucs_mode():
    """Test transcriber factory forwards an explicit Demucs mode."""
    deliniation_test_cases = [cast(TestCase, Mock())]
    punctuation_test_cases = [cast(TestCase, Mock())]

    with get_temp_directory_path() as temp_dir_path:
        with patch(
            "scinoephile.multilang.yue_zho.transcription.YueTranscriber"
        ) as patched_transcriber:
            get_yue_vs_zho_transcriber(
                deliniation_test_cases=deliniation_test_cases,
                punctuation_test_cases=punctuation_test_cases,
                test_case_directory_path=temp_dir_path,
                demucs_mode=DemucsMode.ON,
            )

    assert patched_transcriber.call_args.kwargs["demucs_mode"] == DemucsMode.ON


def test_get_yue_vs_zho_transcriber_passes_convert():
    """Test transcriber factory forwards an explicit OpenCC conversion."""
    deliniation_test_cases = [cast(TestCase, Mock())]
    punctuation_test_cases = [cast(TestCase, Mock())]

    with get_temp_directory_path() as temp_dir_path:
        with patch(
            "scinoephile.multilang.yue_zho.transcription.YueTranscriber"
        ) as patched_transcriber:
            get_yue_vs_zho_transcriber(
                deliniation_test_cases=deliniation_test_cases,
                punctuation_test_cases=punctuation_test_cases,
                test_case_directory_path=temp_dir_path,
                convert=OpenCCConfig.hk2s,
            )

    assert patched_transcriber.call_args.kwargs["convert"] == OpenCCConfig.hk2s


def test_get_yue_vs_zho_transcriber_defaults_exclude_kob_test_cases():
    """Test default transcription test-case paths exclude KOB corpora."""
    assert YUE_ZHO_TRANSCRIPTION_DELINIATION_JSON_PATHS == (
        Path(
            "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/transcription/deliniation/cuda.json"
        ),
        Path(
            "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/transcription/deliniation/mps.json"
        ),
    )
    assert YUE_ZHO_TRANSCRIPTION_PUNCTUATION_JSON_PATHS == (
        Path(
            "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/transcription/punctuation/cuda.json"
        ),
        Path(
            "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/transcription/punctuation/mps.json"
        ),
    )
