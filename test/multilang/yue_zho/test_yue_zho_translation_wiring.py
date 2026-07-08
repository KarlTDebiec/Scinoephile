#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for written Cantonese/Chinese translation wiring."""

from __future__ import annotations

from collections.abc import Callable
from typing import cast
from unittest.mock import Mock

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.dual_n_to_m import DualNToMProcessor, DualNToMPrompt
from scinoephile.multilang.translation import (
    get_guided_translated,
    get_guided_translator,
    get_translated,
    get_translator,
)
from scinoephile.multilang.yue_zho.translation import (
    YueZhoGuidedTranslationPromptYueHans,
    YueZhoTranslationPromptYueHans,
)
from test.helpers import parametrize

_ProcessorFactory = Callable[..., DualNToMProcessor]


@parametrize(
    ("prompt_cls", "src_1", "src_2", "output"),
    [
        (YueZhoTranslationPromptYueHans, "zhongwen_1", "context_1", "yuewen_1"),
        (
            YueZhoGuidedTranslationPromptYueHans,
            "zhongwen_1",
            "yuewen_reference_1",
            "yuewen_1",
        ),
    ],
)
def test_yue_zho_prompt_field_names(
    prompt_cls: type[DualNToMPrompt],
    src_1: str,
    src_2: str,
    output: str,
):
    """Test written Cantonese/Chinese prompt field names.

    Arguments:
        prompt_cls: prompt class under test
        src_1: expected first source field name
        src_2: expected second source field name
        output: expected output field name
    """
    assert prompt_cls.src_1(1) == src_1
    assert prompt_cls.src_2(1) == src_2
    assert prompt_cls.output(1) == output


@parametrize(
    ("factory", "prompt_cls"),
    [
        (get_translator, YueZhoTranslationPromptYueHans),
        (get_guided_translator, YueZhoGuidedTranslationPromptYueHans),
    ],
)
def test_yue_zho_translator_factory_wiring(
    factory: _ProcessorFactory,
    prompt_cls: type[DualNToMPrompt],
):
    """Test written Cantonese/Chinese translator factory wiring.

    Arguments:
        factory: translator factory under test
        prompt_cls: expected prompt class
    """
    provider = Mock(spec=LLMProvider)

    processor = factory(
        Language.zho_hans,
        Language.yue_hans,
        test_cases=[],
        use_dictionary_tool=False,
        provider=provider,
    )

    assert isinstance(processor, DualNToMProcessor)
    assert processor.prompt_cls is prompt_cls
    assert processor.queryer.provider is provider


@parametrize(
    ("mode", "uses_empty_context"),
    [
        ("regular", True),
        ("guided", False),
    ],
)
def test_yue_zho_translation_wrappers_delegate_to_processor(
    mode: str,
    uses_empty_context: bool,
):
    """Test written Cantonese/Chinese wrappers delegate to provided processors.

    Arguments:
        mode: wrapper variant under test
        uses_empty_context: whether the wrapper creates an empty second source
    """
    zhongwen = Series(
        [
            Subtitle(start=1000, end=2000, text="第一句"),
            Subtitle(start=2100, end=3000, text="第二句"),
        ]
    )
    yuewen = Series([Subtitle(start=900, end=3100, text="参考粤文")])
    expected = Series(
        [
            Subtitle(start=1000, end=2000, text="第一句粤文"),
            Subtitle(start=2100, end=3000, text="第二句粤文"),
        ]
    )
    processor = _RecordingProcessor(expected)

    if mode == "regular":
        output = get_translated(
            zhongwen,
            Language.zho_hans,
            Language.yue_hans,
            translator=cast(DualNToMProcessor, processor),
        )
    else:
        output = get_guided_translated(
            zhongwen,
            yuewen,
            Language.zho_hans,
            Language.yue_hans,
            translator=cast(DualNToMProcessor, processor),
        )

    assert output == expected
    assert processor.source_one is zhongwen
    if uses_empty_context:
        assert isinstance(processor.source_two, Series)
        assert len(processor.source_two.events) == 0
    else:
        assert processor.source_two is yuewen


class _RecordingProcessor:
    """Processor test double that records process inputs."""

    def __init__(self, output: Series):
        """Initialize.

        Arguments:
            output: series to return
        """
        self.output = output
        self.source_one: Series | None = None
        self.source_two: Series | None = None

    def process(self, source_one: Series, source_two: Series) -> Series:
        """Record inputs and return configured output.

        Arguments:
            source_one: first source series
            source_two: second source series
        Returns:
            configured output series
        """
        self.source_one = source_one
        self.source_two = source_two
        return self.output
