#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of source text SRT processing workflows."""

from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch

from scinoephile.core import Language
from scinoephile.core.subtitles import Series
from scinoephile.lang.yue.review import ReviewPromptYueHans, ReviewPromptYueHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.review import ReviewPrompt
from scinoephile.workflows.srt_processing import (
    SrtProcessingResult,
    SrtProcessingWorkflow,
)
from test.helpers.series_files import get_text_series

SRT_PROCESSING_MODULE = "scinoephile.workflows.srt_processing"
"""Module path patched by these workflow tests."""

BASE_OUTPUT_NAMES = [
    "clean",
    "clean_review",
    "clean_review_flatten",
    "clean_review_flatten_timewarp",
]
"""Output stems common to every SRT processing workflow."""

YUE_HANS_OUTPUT_NAMES = [
    *BASE_OUTPUT_NAMES,
    "clean_review_flatten_timewarp_romanize",
]
"""Output stems for simplified written Cantonese SRT processing."""

YUE_HANT_OUTPUT_NAMES = [
    *BASE_OUTPUT_NAMES,
    "clean_review_flatten_timewarp_simplify",
    "clean_review_flatten_timewarp_simplify_review",
    "clean_review_flatten_timewarp_simplify_review_romanize",
]
"""Output stems for traditional written Cantonese SRT processing."""


def _output_paths(output_dir_path: Path, output_names: list[str]) -> dict[str, Path]:
    """Build expected workflow output paths.

    Arguments:
        output_dir_path: workflow output directory path
        output_names: output filename stems
    Returns:
        output paths keyed by output filename stem
    """
    return {name: output_dir_path / f"{name}.srt" for name in output_names}


def _raise_unexpected_call(*args: object, **kwargs: object) -> object:
    """Raise if a patched function is unexpectedly called.

    Arguments:
        *args: positional arguments
        **kwargs: keyword arguments
    """
    raise AssertionError("Existing workflow output should have been reused")


def _series_texts(series: Series) -> list[str]:
    """Get subtitle texts from a series.

    Arguments:
        series: subtitle series
    Returns:
        subtitle texts
    """
    return [subtitle.text for subtitle in series]


def _write_series(output_path: Path, *texts: str) -> Series:
    """Write a compact SRT series.

    Arguments:
        output_path: path to write
        *texts: subtitle texts
    Returns:
        written subtitle series
    """
    series = get_text_series(*texts, start_ms=1000, duration_ms=500, step_ms=1000)
    series.save(output_path, format_="srt")
    return series


class _PatchedSrtPipeline:
    """Recording fake for SRT workflow dependencies."""

    def __init__(self, monkeypatch: MonkeyPatch):
        """Initialize and patch SRT workflow dependencies.

        Arguments:
            monkeypatch: pytest monkeypatch fixture
        """
        self.calls: list[str] = []
        self.review_language_calls: list[Language] = []
        self.review_prompt_calls: list[ReviewPrompt | None] = []
        self.review_test_case_path_calls: list[Path] = []
        self.review_auto_verify_calls: list[object] = []
        self.reviewed_text_calls: list[list[str]] = []
        self.timewarp_text_calls: list[list[str]] = []
        self.timewarp_kw_calls: list[dict[str, object]] = []
        self.clean_language_calls: list[Language] = []
        self.cleaned_text_calls: list[list[str]] = []
        self.flatten_language_calls: list[Language] = []
        self.flattened_text_calls: list[list[str]] = []
        self.converted_text_calls: list[list[str]] = []
        self.convert_config_calls: list[OpenCCConfig] = []
        self.romanized_text_calls: list[list[str]] = []
        self.romanize_language_calls: list[Language] = []
        self.romanize_append_calls: list[bool] = []

        for name in [
            "clean_series",
            "flatten",
            "get_series_timewarped",
            "get_zho_converted",
            "romanize",
            "review",
        ]:
            monkeypatch.setattr(f"{SRT_PROCESSING_MODULE}.{name}", getattr(self, name))

    def clean_series(self, series: Series, *, language: Language) -> Series:
        """Fake language-aware cleaning.

        Arguments:
            series: subtitle series to clean
            language: language selected by the workflow
        Returns:
            cleaned subtitle series
        """
        self.calls.append("clean")
        self.clean_language_calls.append(language)
        self.cleaned_text_calls.append(_series_texts(series))
        if language is Language.eng:
            return get_text_series("eng cleaned")
        return get_text_series("yue cleaned")

    def review_series(
        self,
        series: Series,
        *,
        language: Language,
        prompt: ReviewPrompt | None,
        test_case_path: Path,
        provider: object,
        **kwargs: object,
    ) -> Series:
        """Fake review.

        Arguments:
            series: subtitle series to review
            language: language selected by the workflow
            prompt: prompt selected by the workflow
            test_case_path: path where test cases should be written
            provider: provider passed through by workflow
            **kwargs: reviewer keyword arguments
        Returns:
            reviewed subtitle series
        """
        self.calls.append("review")
        self.review_language_calls.append(language)
        self.review_prompt_calls.append(prompt)
        self.review_test_case_path_calls.append(test_case_path)
        self.review_auto_verify_calls.append(kwargs["auto_verify"])
        self.reviewed_text_calls.append(_series_texts(series))
        if language is Language.eng:
            return get_text_series("eng reviewed")
        return get_text_series(f"yue reviewed {len(self.reviewed_text_calls)}")

    def flatten_series(self, series: Series, *, language: Language) -> Series:
        """Fake language-aware flattening.

        Arguments:
            series: subtitle series to flatten
            language: subtitle language
        Returns:
            flattened subtitle series
        """
        self.calls.append("flatten")
        self.flatten_language_calls.append(language)
        self.flattened_text_calls.append(_series_texts(series))
        if language is Language.eng:
            return get_text_series("eng flattened")
        return get_text_series("yue flattened")

    def get_series_timewarped(
        self,
        source_one: Series,
        source_two: Series,
        **kwargs: object,
    ) -> Series:
        """Fake timewarping.

        Arguments:
            source_one: anchor subtitle series
            source_two: source subtitle series
            **kwargs: timewarp keyword arguments
        Returns:
            timewarped subtitle series
        """
        texts = _series_texts(source_two)
        self.calls.append("timewarp")
        self.timewarp_text_calls.append(texts)
        self.timewarp_kw_calls.append(kwargs)
        if texts == ["eng flattened"]:
            return get_text_series("eng timewarped")
        return get_text_series("yue timewarped")

    def romanize_series(
        self,
        series: Series,
        *,
        language: Language,
        append: bool = True,
    ) -> Series:
        """Fake romanization.

        Arguments:
            series: subtitle series to romanize
            language: language selected by the workflow
            append: whether romanization should be appended
        Returns:
            romanized subtitle series
        """
        self.calls.append("romanize")
        self.romanized_text_calls.append(_series_texts(series))
        self.romanize_language_calls.append(language)
        self.romanize_append_calls.append(append)
        return get_text_series("yue romanized")

    def get_zho_converted(self, series: Series, config: OpenCCConfig) -> Series:
        """Fake Chinese script conversion.

        Arguments:
            series: subtitle series to convert
            config: OpenCC conversion configuration
        Returns:
            converted subtitle series
        """
        self.calls.append("simplify")
        self.converted_text_calls.append(_series_texts(series))
        self.convert_config_calls.append(config)
        return get_text_series("yue simplified")


def test_yue_srt_workflow_reuses_existing_outputs_without_overwrite(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test existing Yue SRT workflow outputs are reused by default.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    source_path = tmp_path / "source.srt"
    reference_path = tmp_path / "reference.srt"
    output_dir_path = tmp_path / "output"
    _write_series(source_path, "source")
    _write_series(reference_path, "reference")
    for output_name in YUE_HANS_OUTPUT_NAMES:
        _write_series(output_dir_path / f"{output_name}.srt", f"existing {output_name}")

    for name in [
        "clean_series",
        "review",
        "get_series_timewarped",
        "flatten",
        "romanize",
    ]:
        monkeypatch.setattr(f"{SRT_PROCESSING_MODULE}.{name}", _raise_unexpected_call)

    result = SrtProcessingWorkflow(
        source_path,
        reference_path,
        output_dir_path,
        language=Language.yue_hans,
    )()

    assert isinstance(result, SrtProcessingResult)
    assert result.output_paths == _output_paths(output_dir_path, YUE_HANS_OUTPUT_NAMES)
    assert _series_texts(
        Series.load(output_dir_path / "clean_review_flatten_timewarp_romanize.srt")
    ) == ["existing clean_review_flatten_timewarp_romanize"]


def test_yue_srt_workflow_reviews_before_timewarp_and_populates_outputs(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test simplified Yue SRT workflow reviews before timewarping.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    source_path = tmp_path / "source.srt"
    reference_path = tmp_path / "reference.srt"
    output_dir_path = tmp_path / "output"
    _write_series(source_path, "source")
    _write_series(reference_path, "reference")
    pipeline = _PatchedSrtPipeline(monkeypatch)

    result = SrtProcessingWorkflow(
        source_path,
        reference_path,
        output_dir_path,
        language=Language.yue_hans,
        one_end_idx=7,
        two_end_idx=9,
    )()

    assert pipeline.calls == [
        "clean",
        "review",
        "flatten",
        "timewarp",
        "romanize",
    ]
    assert pipeline.review_language_calls == [Language.yue_hans]
    assert pipeline.review_prompt_calls == [ReviewPromptYueHans]
    assert pipeline.review_test_case_path_calls == [
        output_dir_path / "lang" / "yue" / "review.json"
    ]
    assert pipeline.review_auto_verify_calls == [True]
    assert pipeline.clean_language_calls == [Language.yue_hans]
    assert pipeline.cleaned_text_calls == [["source"]]
    assert pipeline.reviewed_text_calls == [["yue cleaned"]]
    assert pipeline.flatten_language_calls == [Language.yue_hans]
    assert pipeline.flattened_text_calls == [["yue reviewed 1"]]
    assert pipeline.timewarp_text_calls == [["yue flattened"]]
    assert pipeline.timewarp_kw_calls == [
        {
            "one_start_idx": None,
            "one_end_idx": 7,
            "two_start_idx": None,
            "two_end_idx": 9,
        }
    ]
    assert pipeline.romanized_text_calls == [["yue timewarped"]]
    assert pipeline.romanize_language_calls == [Language.yue_hans]
    assert pipeline.romanize_append_calls == [True]
    assert result.output_paths == _output_paths(output_dir_path, YUE_HANS_OUTPUT_NAMES)


def test_traditional_yue_srt_workflow_simplifies_reviews_and_romanizes(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test traditional Yue workflow includes simplify, review, and romanize outputs.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    source_path = tmp_path / "source.srt"
    reference_path = tmp_path / "reference.srt"
    output_dir_path = tmp_path / "output"
    _write_series(source_path, "source")
    _write_series(reference_path, "reference")
    pipeline = _PatchedSrtPipeline(monkeypatch)

    result = SrtProcessingWorkflow(
        source_path,
        reference_path,
        output_dir_path,
        language=Language.yue_hant,
    )()

    assert pipeline.calls == [
        "clean",
        "review",
        "flatten",
        "timewarp",
        "simplify",
        "review",
        "romanize",
    ]
    assert pipeline.review_language_calls == [
        Language.yue_hant,
        Language.yue_hans,
    ]
    assert pipeline.review_prompt_calls == [
        ReviewPromptYueHant,
        ReviewPromptYueHans,
    ]
    assert pipeline.review_test_case_path_calls == [
        output_dir_path / "lang" / "yue" / "review.json",
        output_dir_path / "lang" / "yue" / "simplify_review.json",
    ]
    assert pipeline.clean_language_calls == [Language.yue_hant]
    assert pipeline.convert_config_calls == [OpenCCConfig.t2s]
    assert pipeline.cleaned_text_calls == [["source"]]
    assert pipeline.reviewed_text_calls == [["yue cleaned"], ["yue simplified"]]
    assert pipeline.flatten_language_calls == [Language.yue_hant]
    assert pipeline.flattened_text_calls == [["yue reviewed 1"]]
    assert pipeline.timewarp_text_calls == [["yue flattened"]]
    assert pipeline.converted_text_calls == [["yue timewarped"]]
    assert pipeline.romanized_text_calls == [["yue reviewed 2"]]
    assert pipeline.romanize_language_calls == [Language.yue_hant]
    assert result.output_paths == _output_paths(output_dir_path, YUE_HANT_OUTPUT_NAMES)
    assert "clean_review_flatten_timewarp_romanize" not in result.output_paths


def test_eng_srt_workflow_reviews_before_timewarp_and_populates_outputs(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test English SRT workflow reviews before timewarping and writes outputs.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    source_path = tmp_path / "source.srt"
    reference_path = tmp_path / "reference.srt"
    output_dir_path = tmp_path / "output"
    _write_series(source_path, "source")
    _write_series(reference_path, "reference")
    pipeline = _PatchedSrtPipeline(monkeypatch)

    result = SrtProcessingWorkflow(
        source_path,
        reference_path,
        output_dir_path,
        language=Language.eng,
        one_end_idx=11,
    )()

    assert pipeline.calls == [
        "clean",
        "review",
        "flatten",
        "timewarp",
    ]
    assert pipeline.review_language_calls == [Language.eng]
    assert pipeline.review_prompt_calls == [None]
    assert pipeline.review_test_case_path_calls == [
        output_dir_path / "lang" / "eng" / "review.json"
    ]
    assert pipeline.review_auto_verify_calls == [True]
    assert pipeline.clean_language_calls == [Language.eng]
    assert pipeline.timewarp_text_calls == [["eng flattened"]]
    assert pipeline.timewarp_kw_calls == [
        {
            "one_start_idx": None,
            "one_end_idx": 11,
            "two_start_idx": None,
            "two_end_idx": None,
        }
    ]
    assert pipeline.cleaned_text_calls == [["source"]]
    assert pipeline.reviewed_text_calls == [["eng cleaned"]]
    assert pipeline.flatten_language_calls == [Language.eng]
    assert pipeline.flattened_text_calls == [["eng reviewed"]]
    assert result.output_paths == _output_paths(output_dir_path, BASE_OUTPUT_NAMES)
    assert _series_texts(
        Series.load(output_dir_path / "clean_review_flatten_timewarp.srt")
    ) == ["eng timewarped"]
