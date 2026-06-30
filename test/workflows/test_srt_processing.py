#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of source text SRT processing workflows."""

from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch

from scinoephile.core import Language
from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.block_review import (
    BlockReviewPromptZhoHans,
    BlockReviewPromptZhoHant,
)
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.workflows.srt_processing import (
    SrtProcessingResult,
    SrtProcessingWorkflow,
)
from test.helpers.series_files import get_text_series


def _raise_if_called(*args: object, **kwargs: object) -> object:
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


class _PatchedEngSrtPipeline:
    """Recording fake for English SRT workflow dependencies."""

    def __init__(self, monkeypatch: MonkeyPatch):
        """Initialize and patch English SRT workflow dependencies.

        Arguments:
            monkeypatch: pytest monkeypatch fixture
        """
        self.calls: list[str] = []
        self.reviewer = object()
        self.review_test_case_path_calls: list[Path] = []
        self.review_auto_verify_calls: list[object] = []
        self.reviewed_text_calls: list[list[str]] = []
        self.timewarp_text_calls: list[list[str]] = []
        self.timewarp_kw_calls: list[dict[str, object]] = []
        self.cleaned_text_calls: list[list[str]] = []
        self.flattened_text_calls: list[list[str]] = []

        monkeypatch.setattr(
            "scinoephile.workflows.srt_processing.get_eng_block_reviewer",
            self.get_eng_block_reviewer,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.srt_processing.get_eng_block_reviewed",
            self.get_eng_block_reviewed,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.srt_processing.get_series_timewarped",
            self.get_series_timewarped,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.srt_processing.get_eng_cleaned",
            self.get_eng_cleaned,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.srt_processing.get_eng_flattened",
            self.get_eng_flattened,
        )

    def get_eng_block_reviewed(self, series: Series, processor: object) -> Series:
        """Fake English block review.

        Arguments:
            series: subtitle series to review
            processor: fake reviewer
        Returns:
            reviewed subtitle series
        """
        assert processor is self.reviewer
        self.calls.append("review")
        self.reviewed_text_calls.append(_series_texts(series))
        return get_text_series("eng reviewed")

    def get_eng_block_reviewer(
        self,
        *,
        test_case_path: Path,
        provider: object,
        **kwargs: object,
    ) -> object:
        """Return a fixed fake English reviewer.

        Arguments:
            test_case_path: path where test cases should be written
            provider: provider passed through by workflow
            **kwargs: reviewer keyword arguments
        Returns:
            fake reviewer
        """
        self.calls.append("get_reviewer")
        self.review_test_case_path_calls.append(test_case_path)
        self.review_auto_verify_calls.append(kwargs["auto_verify"])
        return self.reviewer

    def get_eng_cleaned(self, series: Series) -> Series:
        """Fake English cleaning.

        Arguments:
            series: subtitle series to clean
        Returns:
            cleaned subtitle series
        """
        self.calls.append("clean")
        self.cleaned_text_calls.append(_series_texts(series))
        return get_text_series("eng cleaned")

    def get_eng_flattened(self, series: Series) -> Series:
        """Fake English flattening.

        Arguments:
            series: subtitle series to flatten
        Returns:
            flattened subtitle series
        """
        self.calls.append("flatten")
        self.flattened_text_calls.append(_series_texts(series))
        return get_text_series("eng flattened")

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
        self.calls.append("timewarp")
        self.timewarp_text_calls.append(_series_texts(source_two))
        self.timewarp_kw_calls.append(kwargs)
        return get_text_series("eng timewarped")


class _PatchedYueSrtPipeline:
    """Recording fake for Yue SRT workflow dependencies."""

    def __init__(self, monkeypatch: MonkeyPatch):
        """Initialize and patch Yue SRT workflow dependencies.

        Arguments:
            monkeypatch: pytest monkeypatch fixture
        """
        self.calls: list[str] = []
        self.reviewer = object()
        self.review_prompt_calls: list[type[BlockReviewPromptZhoHans]] = []
        self.review_test_case_path_calls: list[Path] = []
        self.review_auto_verify_calls: list[object] = []
        self.reviewed_text_calls: list[list[str]] = []
        self.timewarp_text_calls: list[list[str]] = []
        self.timewarp_kw_calls: list[dict[str, object]] = []
        self.cleaned_text_calls: list[list[str]] = []
        self.flattened_text_calls: list[list[str]] = []
        self.converted_text_calls: list[list[str]] = []
        self.convert_config_calls: list[OpenCCConfig] = []
        self.romanized_text_calls: list[list[str]] = []
        self.romanize_append_calls: list[bool] = []

        monkeypatch.setattr(
            "scinoephile.workflows.srt_processing.get_zho_reviewer",
            self.get_zho_reviewer,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.srt_processing.get_zho_block_reviewed",
            self.get_zho_block_reviewed,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.srt_processing.get_series_timewarped",
            self.get_series_timewarped,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.srt_processing.get_zho_cleaned",
            self.get_zho_cleaned,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.srt_processing.get_zho_flattened",
            self.get_zho_flattened,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.srt_processing.get_zho_converted",
            self.get_zho_converted,
        )
        monkeypatch.setattr(
            "scinoephile.workflows.srt_processing.get_yue_romanized",
            self.get_yue_romanized,
        )

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
        self.calls.append("timewarp")
        self.timewarp_text_calls.append(_series_texts(source_two))
        self.timewarp_kw_calls.append(kwargs)
        return get_text_series("yue timewarped")

    def get_yue_romanized(self, series: Series, append: bool = True) -> Series:
        """Fake Yue romanization.

        Arguments:
            series: subtitle series to romanize
            append: whether romanization should be appended
        Returns:
            romanized subtitle series
        """
        self.calls.append("romanize")
        self.romanized_text_calls.append(_series_texts(series))
        self.romanize_append_calls.append(append)
        return get_text_series("yue romanized")

    def get_zho_block_reviewed(
        self,
        series: Series,
        processor: object,
    ) -> Series:
        """Fake Chinese block review.

        Arguments:
            series: subtitle series to review
            processor: fake reviewer
        Returns:
            reviewed subtitle series
        """
        assert processor is self.reviewer
        self.calls.append("review")
        self.reviewed_text_calls.append(_series_texts(series))
        return get_text_series(f"yue reviewed {len(self.reviewed_text_calls)}")

    def get_zho_cleaned(self, series: Series) -> Series:
        """Fake Chinese cleaning.

        Arguments:
            series: subtitle series to clean
        Returns:
            cleaned subtitle series
        """
        self.calls.append("clean")
        self.cleaned_text_calls.append(_series_texts(series))
        return get_text_series("yue cleaned")

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

    def get_zho_flattened(self, series: Series) -> Series:
        """Fake Chinese flattening.

        Arguments:
            series: subtitle series to flatten
        Returns:
            flattened subtitle series
        """
        self.calls.append("flatten")
        self.flattened_text_calls.append(_series_texts(series))
        return get_text_series("yue flattened")

    def get_zho_reviewer(
        self,
        *,
        prompt_cls: type[BlockReviewPromptZhoHans],
        test_case_path: Path,
        provider: object,
        **kwargs: object,
    ) -> object:
        """Return a fixed fake Chinese reviewer.

        Arguments:
            prompt_cls: prompt class selected by the workflow
            test_case_path: path where test cases should be written
            provider: provider passed through by workflow
            **kwargs: reviewer keyword arguments
        Returns:
            fake reviewer
        """
        self.calls.append("get_reviewer")
        self.review_prompt_calls.append(prompt_cls)
        self.review_test_case_path_calls.append(test_case_path)
        self.review_auto_verify_calls.append(kwargs["auto_verify"])
        return self.reviewer


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
    output_names = [
        "clean",
        "clean_review",
        "clean_review_flatten",
        "clean_review_flatten_timewarp",
        "clean_review_flatten_timewarp_romanize",
    ]
    for output_name in output_names:
        _write_series(output_dir_path / f"{output_name}.srt", f"existing {output_name}")

    for name in [
        "get_zho_reviewer",
        "get_zho_block_reviewed",
        "get_series_timewarped",
        "get_zho_cleaned",
        "get_zho_flattened",
        "get_yue_romanized",
    ]:
        monkeypatch.setattr(
            f"scinoephile.workflows.srt_processing.{name}", _raise_if_called
        )

    result = SrtProcessingWorkflow(
        source_path,
        reference_path,
        output_dir_path,
        language=Language.yue_hans,
    )()

    assert isinstance(result, SrtProcessingResult)
    assert result.output_paths == {
        output_name: output_dir_path / f"{output_name}.srt"
        for output_name in output_names
    }
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
    pipeline = _PatchedYueSrtPipeline(monkeypatch)

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
        "get_reviewer",
        "review",
        "flatten",
        "timewarp",
        "romanize",
    ]
    assert pipeline.review_prompt_calls == [BlockReviewPromptZhoHans]
    assert pipeline.review_test_case_path_calls == [
        output_dir_path / "lang" / "yue" / "block_review.json"
    ]
    assert pipeline.review_auto_verify_calls == [True]
    assert pipeline.cleaned_text_calls == [["source"]]
    assert pipeline.reviewed_text_calls == [["yue cleaned"]]
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
    assert pipeline.romanize_append_calls == [True]
    assert result.output_paths == {
        "clean": output_dir_path / "clean.srt",
        "clean_review": output_dir_path / "clean_review.srt",
        "clean_review_flatten": output_dir_path / "clean_review_flatten.srt",
        "clean_review_flatten_timewarp": (
            output_dir_path / "clean_review_flatten_timewarp.srt"
        ),
        "clean_review_flatten_timewarp_romanize": (
            output_dir_path / "clean_review_flatten_timewarp_romanize.srt"
        ),
    }


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
    pipeline = _PatchedYueSrtPipeline(monkeypatch)

    result = SrtProcessingWorkflow(
        source_path,
        reference_path,
        output_dir_path,
        language=Language.yue_hant,
    )()

    assert pipeline.calls == [
        "clean",
        "get_reviewer",
        "review",
        "flatten",
        "timewarp",
        "simplify",
        "get_reviewer",
        "review",
        "romanize",
    ]
    assert pipeline.review_prompt_calls == [
        BlockReviewPromptZhoHant,
        BlockReviewPromptZhoHans,
    ]
    assert pipeline.review_test_case_path_calls == [
        output_dir_path / "lang" / "yue" / "block_review.json",
        output_dir_path / "lang" / "yue" / "simplify_block_review.json",
    ]
    assert pipeline.convert_config_calls == [OpenCCConfig.t2s]
    assert pipeline.cleaned_text_calls == [["source"]]
    assert pipeline.reviewed_text_calls == [["yue cleaned"], ["yue simplified"]]
    assert pipeline.flattened_text_calls == [["yue reviewed 1"]]
    assert pipeline.timewarp_text_calls == [["yue flattened"]]
    assert pipeline.converted_text_calls == [["yue timewarped"]]
    assert pipeline.romanized_text_calls == [["yue reviewed 2"]]
    assert result.output_paths == {
        "clean": output_dir_path / "clean.srt",
        "clean_review": output_dir_path / "clean_review.srt",
        "clean_review_flatten": output_dir_path / "clean_review_flatten.srt",
        "clean_review_flatten_timewarp": (
            output_dir_path / "clean_review_flatten_timewarp.srt"
        ),
        "clean_review_flatten_timewarp_simplify": (
            output_dir_path / "clean_review_flatten_timewarp_simplify.srt"
        ),
        "clean_review_flatten_timewarp_simplify_review": (
            output_dir_path / "clean_review_flatten_timewarp_simplify_review.srt"
        ),
        "clean_review_flatten_timewarp_simplify_review_romanize": (
            output_dir_path
            / "clean_review_flatten_timewarp_simplify_review_romanize.srt"
        ),
    }
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
    pipeline = _PatchedEngSrtPipeline(monkeypatch)

    result = SrtProcessingWorkflow(
        source_path,
        reference_path,
        output_dir_path,
        language=Language.eng,
        one_end_idx=11,
    )()

    assert pipeline.calls == [
        "clean",
        "get_reviewer",
        "review",
        "flatten",
        "timewarp",
    ]
    assert pipeline.review_test_case_path_calls == [
        output_dir_path / "lang" / "eng" / "block_review.json"
    ]
    assert pipeline.review_auto_verify_calls == [True]
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
    assert pipeline.flattened_text_calls == [["eng reviewed"]]
    assert result.output_paths == {
        "clean": output_dir_path / "clean.srt",
        "clean_review": output_dir_path / "clean_review.srt",
        "clean_review_flatten": output_dir_path / "clean_review_flatten.srt",
        "clean_review_flatten_timewarp": (
            output_dir_path / "clean_review_flatten_timewarp.srt"
        ),
    }
    assert _series_texts(
        Series.load(output_dir_path / "clean_review_flatten_timewarp.srt")
    ) == ["eng timewarped"]
