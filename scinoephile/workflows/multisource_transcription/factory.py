#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factory for multi-source transcription workflows."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from scinoephile.analysis.alignment.timed_msa.aligner import Aligner
from scinoephile.audio.transcription.ctc import CtcAligner
from scinoephile.audio.transcription.transcriber import Transcriber
from scinoephile.core.language import Language
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.lang.transcription.standard import get_transcriber
from scinoephile.lang.yue.transcription.token_similarity import YueTokenSimilarity

from .transcriber import MultiSourceTranscriber

__all__ = ["get_multi_source_transcriber"]


def get_multi_source_transcriber(
    language: Language,
    transcribers: Mapping[str, Transcriber],
    *,
    provider: LLMProvider | None = None,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    additional_context: str | None = None,
    no_op: bool = False,
    current_test_cases_path: Path | None = None,
    prune_test_cases: bool = False,
    shared_test_cases: list[TestCase] | None = None,
) -> MultiSourceTranscriber:
    """Get a reference-free aligned multi-source transcriber.

    Arguments:
        language: transcription and output language
        transcribers: named equal-status ASR sources
        provider: provider to use for consensus queries
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching LLM cache entries
        additional_context: additional context to include in the prompt
        no_op: whether to use deterministic column consensus instead of an LLM
        current_test_cases_path: current transcription test-case JSON path
        prune_test_cases: whether to remove unencountered persisted test cases
        shared_test_cases: preloaded transcription test cases
    Returns:
        configured multi-source transcriber
    """
    processor = get_transcriber(
        language,
        shared_test_cases=shared_test_cases,
        provider=provider,
        cache_root_path=cache_root_path,
        overwrite_cache=overwrite_cache,
        additional_context=additional_context,
        no_op=no_op,
        current_test_cases_path=current_test_cases_path,
        prune_test_cases=prune_test_cases,
    )
    return MultiSourceTranscriber(
        language=language,
        transcribers=transcribers,
        aligner=Aligner(YueTokenSimilarity()),
        processor=processor,
        ctc_aligner=CtcAligner(
            language, cache_root_path=cache_root_path, overwrite_cache=overwrite_cache
        ),
    )
