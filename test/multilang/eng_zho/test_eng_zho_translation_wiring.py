#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for English/Chinese translation wiring."""

from __future__ import annotations

from collections.abc import Callable
from typing import cast
from unittest.mock import Mock

from pytest import parametrize

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.dual_n_minus_m_to_n import (
    DualNMinusMToNProcessor,
    DualNMinusMToNPrompt,
)
from scinoephile.llms.dual_n_to_m import DualNToMProcessor, DualNToMPrompt
from scinoephile.multilang.eng_zho.gapped_translation import (
    EngGappedTranslationVsZhoPrompt,
    get_eng_gapped_translated_vs_zho,
    get_eng_vs_zho_gapped_translator,
)
from scinoephile.multilang.eng_zho.guided_translation import (
    EngGuidedTranslationVsZhoPrompt,
    get_eng_translated_from_zho_with_eng_guidance,
    get_eng_zho_guided_translator,
)
from scinoephile.multilang.eng_zho.translation import (
    EngTranslationVsZhoPrompt,
    get_eng_translated_from_zho,
    get_eng_zho_translator,
)

_PromptCls = type[DualNToMPrompt] | type[DualNMinusMToNPrompt]
_Processor = DualNToMProcessor | DualNMinusMToNProcessor
_ProcessorFactory = Callable[..., _Processor]


@parametrize(
    ("prompt_cls", "src_1", "src_2", "output"),
    [
        (EngTranslationVsZhoPrompt, "zho_1", "context_1", "eng_1"),
        (EngGuidedTranslationVsZhoPrompt, "zho_1", "eng_reference_1", "eng_1"),
        (EngGappedTranslationVsZhoPrompt, "eng_1", "zho_1", "eng_1"),
    ],
)
def test_eng_zho_prompt_field_names(
    prompt_cls: _PromptCls,
    src_1: str,
    src_2: str,
    output: str,
):
    """Test English/Chinese prompt field names.

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
    ("factory", "processor_cls", "prompt_cls"),
    [
        (get_eng_zho_translator, DualNToMProcessor, EngTranslationVsZhoPrompt),
        (
            get_eng_zho_guided_translator,
            DualNToMProcessor,
            EngGuidedTranslationVsZhoPrompt,
        ),
        (
            get_eng_vs_zho_gapped_translator,
            DualNMinusMToNProcessor,
            EngGappedTranslationVsZhoPrompt,
        ),
    ],
)
def test_eng_zho_translator_factory_wiring(
    factory: _ProcessorFactory,
    processor_cls: type[_Processor],
    prompt_cls: _PromptCls,
):
    """Test English/Chinese translator factory wiring.

    Arguments:
        factory: translator factory under test
        processor_cls: expected processor class
        prompt_cls: expected prompt class
    """
    provider = Mock(spec=LLMProvider)

    processor = factory(test_cases=[], provider=provider)

    assert isinstance(processor, processor_cls)
    assert processor.prompt_cls is prompt_cls
    assert processor.queryer.provider is provider


@parametrize(
    ("mode", "uses_empty_context"),
    [
        ("regular", True),
        ("guided", False),
        ("gapped", False),
    ],
)
def test_eng_zho_translation_wrappers_delegate_to_processor(
    mode: str,
    uses_empty_context: bool,
):
    """Test English/Chinese translation wrappers delegate to provided processors.

    Arguments:
        mode: wrapper variant under test
        uses_empty_context: whether the wrapper creates an empty second source
    """
    source_one = Series(
        [
            Subtitle(start=1000, end=2000, text="第一句"),
            Subtitle(start=2100, end=3000, text="第二句"),
        ]
    )
    source_two = Series([Subtitle(start=900, end=3100, text="Reference line")])
    expected = Series(
        [
            Subtitle(start=1000, end=2000, text="First translated"),
            Subtitle(start=2100, end=3000, text="Second translated"),
        ]
    )
    processor = _RecordingProcessor(expected)

    if mode == "regular":
        output = get_eng_translated_from_zho(
            source_one,
            translator=cast(DualNToMProcessor, processor),
        )
    elif mode == "guided":
        output = get_eng_translated_from_zho_with_eng_guidance(
            source_one,
            source_two,
            translator=cast(DualNToMProcessor, processor),
        )
    else:
        output = get_eng_gapped_translated_vs_zho(
            source_one,
            source_two,
            translator=cast(DualNMinusMToNProcessor, processor),
        )

    assert output == expected
    assert processor.source_one is source_one
    if uses_empty_context:
        assert isinstance(processor.source_two, Series)
        assert len(processor.source_two.events) == 0
    else:
        assert processor.source_two is source_two


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
