#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for guided-transcription test-data generation."""

from __future__ import annotations

from logging import INFO, WARNING, getLogger
from pathlib import Path
from unittest.mock import Mock

from pytest import LogCaptureFixture, MonkeyPatch, mark, param

import test.data.transcription as transcription_data
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import VADMode
from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle


def test_get_reference_for_guide_blocks_limits_reference_prefix():
    """Limit an evaluation reference using the selected guide blocks."""
    guide = Series(
        events=[
            Subtitle(start=0, end=1_000, text="一"),
            Subtitle(start=5_000, end=6_000, text="二"),
        ]
    )
    reference = Series(
        events=[
            Subtitle(start=100, end=500, text="甲"),
            Subtitle(start=999, end=1_500, text="乙"),
            Subtitle(start=1_000, end=2_000, text="丙"),
            Subtitle(start=5_500, end=6_000, text="丁"),
        ]
    )

    limited = transcription_data.get_reference_for_guide_blocks(reference, guide, 1)

    assert [subtitle.text for subtitle in limited] == ["甲", "乙"]


def test_process_transcription_multi_review_uses_root_json_cache(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Load named sources and store the aggregate cache beside model directories.

    Arguments:
        tmp_path: temporary pipeline directory
        monkeypatch: pytest monkeypatch fixture
    """
    source_paths = {
        "whisper": tmp_path / "whisper.srt",
        "mimo": tmp_path / "mimo.srt",
        "qwen": tmp_path / "qwen.srt",
    }
    guide_path = tmp_path / "guide.srt"
    reference_path = tmp_path / "reference.srt"
    output_path = tmp_path / "yue-Hant_transcribe" / "merge.srt"
    for source_idx, source_path in enumerate(source_paths.values(), 1):
        Series(events=[Subtitle(start=0, end=1_000, text=f"來源{source_idx}")]).save(
            source_path
        )
    guide = Series(events=[Subtitle(start=0, end=1_000, text="指引")])
    guide.save(guide_path)
    guide.save(reference_path)
    reviewed = Series(events=[Subtitle(start=0, end=1_000, text="綜合")])
    review = Mock(return_value=reviewed)
    monkeypatch.setattr(transcription_data, "review_series_multi", review)

    output = transcription_data.process_transcription_multi_review(
        source_paths,
        guide_path,
        output_path,
        reference_path=reference_path,
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        stop_at_idx=5,
        additional_context="Film context",
        overwrite=True,
    )

    assert output is reviewed
    assert Series.load(output_path) == reviewed
    assert set(review.call_args.args[0]) == {"whisper", "mimo", "qwen"}
    assert review.call_args.args[1] == guide
    assert review.call_args.kwargs == {
        "language": Language.yue_hant,
        "guide_language": Language.zho_hant,
        "stop_at_idx": 5,
        "test_case_path": output_path.parent / "json" / "multi_review.json",
        "additional_context": "Film context",
    }


def test_process_transcription_pipeline_runs_all_stages(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Transcribe with all models before merging, translating, and simplifying.

    Arguments:
        tmp_path: temporary pipeline directory
        monkeypatch: pytest monkeypatch fixture
    """
    reference = Series(
        events=[
            Subtitle(start=0, end=1_000, text="佢喺度"),
            Subtitle(start=2_000, end=3_000, text="返嚟啦"),
        ]
    )
    guide = Series(
        events=[
            Subtitle(start=0, end=1_000, text="他在這裡"),
            Subtitle(start=2_000, end=3_000, text="回來吧"),
        ]
    )
    reference_path = tmp_path / "reference.srt"
    guide_path = tmp_path / "guide.srt"
    reference.save(reference_path)
    guide.save(guide_path)
    output_dir_path = tmp_path / "yue-Hant_transcribe"
    audio_dir_path = output_dir_path / "audio"

    merged = Series(
        events=[
            Subtitle(start=0, end=1_000, text="佢喺度"),
            Subtitle(start=2_000, end=3_000, text=""),
        ]
    )
    translated = Series(
        events=[
            Subtitle(start=0, end=1_000, text="佢喺度"),
            Subtitle(start=2_000, end=3_000, text="返嚟啦"),
        ]
    )
    simplified = Series(events=list(translated.events))
    stage_order: list[str] = []
    transcribe = Mock(
        side_effect=lambda *args, **kwargs: (
            stage_order.append(f"transcribe-{kwargs['output_dir_path'].name}")
            or reference
        )
    )
    merge = Mock(
        side_effect=lambda *args, **kwargs: stage_order.append("merge") or merged
    )
    translate = Mock(
        side_effect=lambda *args, **kwargs: (
            stage_order.append("translate") or translated
        )
    )
    simplify = Mock(
        side_effect=lambda *args, **kwargs: stage_order.append("simplify") or simplified
    )
    monkeypatch.setattr(transcription_data, "process_transcription", transcribe)
    monkeypatch.setattr(transcription_data, "process_transcription_multi_review", merge)
    monkeypatch.setattr(transcription_data, "_load_or_translate_series_gaps", translate)
    monkeypatch.setattr(transcription_data, "load_or_simplify_series", simplify)

    output = transcription_data.process_transcription_pipeline(
        tmp_path,
        guide_path,
        reference_path=reference_path,
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        output_dir_path=output_dir_path,
        audio_dir_path=audio_dir_path,
        stop_at_idx=5,
        additional_context="Film context",
        reviewer_kw={"prune_test_cases": True},
        translator_kw={"prune_test_cases": True},
        vad_mode=VADMode.OFF,
        overwrite=True,
    )

    assert output is simplified
    assert stage_order == [
        "transcribe-whisper",
        "transcribe-mimo",
        "transcribe-qwen",
        "merge",
        "translate",
        "simplify",
    ]
    assert [call.kwargs["audio_dir_path"] for call in transcribe.call_args_list] == [
        audio_dir_path,
        audio_dir_path,
        audio_dir_path,
    ]
    transcription_kw_by_name = {
        call.kwargs["output_dir_path"].name: call.kwargs["transcription_kw"]
        for call in transcribe.call_args_list
    }
    assert transcription_kw_by_name["whisper"] == {
        "alignment_mode": transcription_data.TranscriptionAlignmentMode.PAIRWISE,
        "fallback_to_no_op": False,
        "no_op": False,
        "prune_test_cases": True,
        "vad_mode": VADMode.OFF,
    }
    assert transcription_kw_by_name["mimo"] == {
        "alignment_mode": transcription_data.TranscriptionAlignmentMode.PAIRWISE,
        "backend": transcription_data.TranscriptionBackend.MLX_AUDIO,
        "fallback_to_no_op": False,
        "model_name": transcription_data.MIMO_MODEL_NAME,
        "no_op": False,
        "prune_test_cases": True,
        "vad_mode": VADMode.OFF,
    }
    assert transcription_kw_by_name["qwen"] == {
        "alignment_mode": transcription_data.TranscriptionAlignmentMode.PAIRWISE,
        "backend": transcription_data.TranscriptionBackend.MLX_AUDIO,
        "fallback_to_no_op": False,
        "model_name": transcription_data.QWEN3_ASR_MODEL_NAME,
        "no_op": False,
        "prune_test_cases": True,
        "vad_mode": VADMode.OFF,
    }
    assert all(
        call.kwargs["run_traditionalize"] is True
        and call.kwargs["run_review_and_translation"] is False
        for call in transcribe.call_args_list
    )
    assert merge.call_args.args[0] == {
        name: output_dir_path / name / "transcribe_clean_traditionalize.srt"
        for name in ("whisper", "mimo", "qwen")
    }
    assert merge.call_args.args[2] == output_dir_path / "merge.srt"
    assert merge.call_args.kwargs["reviewer_kw"] == {"prune_test_cases": True}
    assert translate.call_args.args[:3] == (
        guide,
        Series(events=[merged.events[0]]),
        output_dir_path / "merge_translate.srt",
    )
    assert translate.call_args.kwargs["translator_kw"] == {
        "prune_test_cases": True,
        "additional_context": "Film context",
    }
    assert simplify.call_args.args == (
        translated,
        output_dir_path / "merge_translate_simplify.srt",
        True,
    )


def test_process_transcription_pipeline_can_stop_before_merge(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Stop after all three transcription sources have been prepared.

    Arguments:
        tmp_path: temporary pipeline directory
        monkeypatch: pytest monkeypatch fixture
    """
    reference = Series(events=[Subtitle(start=0, end=1_000, text="佢喺度")])
    guide = Series(events=[Subtitle(start=0, end=1_000, text="他在這裡")])
    reference_path = tmp_path / "reference.srt"
    guide_path = tmp_path / "guide.srt"
    reference.save(reference_path)
    guide.save(guide_path)
    transcribe = Mock(return_value=reference)
    merge = Mock()
    monkeypatch.setattr(transcription_data, "process_transcription", transcribe)
    monkeypatch.setattr(transcription_data, "process_transcription_multi_review", merge)

    output = transcription_data.process_transcription_pipeline(
        tmp_path,
        guide_path,
        reference_path=reference_path,
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        run_merge_and_translation=False,
    )

    assert output is None
    assert [
        call.kwargs["output_dir_path"].name for call in transcribe.call_args_list
    ] == ["whisper", "mimo", "qwen"]
    merge.assert_not_called()


@mark.parametrize(
    ("language", "guide_language", "detected_language", "expected_log_level"),
    [
        param(
            Language.yue_hans,
            Language.zho_hans,
            Language.zho_hans,
            INFO,
            id="yue-hans-from-zho-hans",
        ),
        param(
            Language.yue_hant,
            Language.zho_hant,
            Language.zho_hant,
            INFO,
            id="yue-hant-from-zho-hant",
        ),
        param(
            Language.yue_hant,
            Language.zho_hant,
            Language.zho_hans,
            WARNING,
            id="different-script",
        ),
        param(
            Language.eng,
            Language.zho_hant,
            Language.zho_hant,
            WARNING,
            id="non-cantonese",
        ),
    ],
)
def test_process_transcription_orders_stages_and_relogs_expected_mismatch(
    tmp_path: Path,
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
    language: Language,
    guide_language: Language,
    detected_language: Language,
    expected_log_level: int,
):
    """Run stages in order and relog only same-script Yue-to-Zho detection.

    Arguments:
        tmp_path: temporary pipeline directory
        caplog: captured log records
        monkeypatch: pytest monkeypatch fixture
        language: transcription language
        guide_language: guide subtitle language
        detected_language: language reported for the fresh transcription
        expected_log_level: expected mismatch log level
    """
    reference = Series(events=[Subtitle(start=0, end=1_000, text="佢喺度")])
    guide = Series(events=[Subtitle(start=0, end=1_000, text="他在這裡")])
    reference_path = tmp_path / "reference.srt"
    guide_path = tmp_path / "guide.srt"
    reference.save(reference_path)
    guide.save(guide_path)
    stage_order: list[str] = []
    stage_audio = Mock(
        side_effect=lambda *args, **kwargs: stage_order.append("audio") or reference
    )
    transcribe = Mock(
        side_effect=lambda *args, **kwargs: (
            stage_order.append("transcribe") or reference
        )
    )
    mismatch_message = (
        f"Explicit language {language.code} does not "
        f"match detected language {detected_language.code}; "
        f"using {language.code}"
    )
    language_logger = getLogger("scinoephile.workflows.helpers")
    clean = Mock(
        side_effect=lambda *args, **kwargs: (
            stage_order.append("clean")
            or language_logger.warning(mismatch_message)
            or reference
        )
    )
    review = Mock(
        side_effect=lambda *args, **kwargs: stage_order.append("review") or reference
    )
    translate = Mock(
        side_effect=lambda *args, **kwargs: stage_order.append("translate") or reference
    )
    monkeypatch.setattr(
        transcription_data,
        "resolve_language",
        Mock(side_effect=lambda series, explicit_language: explicit_language),
    )
    monkeypatch.setattr(transcription_data, "_stage_audio_series", stage_audio)
    monkeypatch.setattr(
        transcription_data, "_load_or_transcribe_series_guided", transcribe
    )
    monkeypatch.setattr(transcription_data, "load_or_clean_series", clean)
    monkeypatch.setattr(transcription_data, "_load_or_review_series_guided", review)
    monkeypatch.setattr(transcription_data, "_load_or_translate_series_gaps", translate)

    with caplog.at_level(INFO):
        audio_dir_path = tmp_path / "shared-audio"
        output = transcription_data.process_transcription(
            tmp_path,
            guide_path,
            reference_path=reference_path,
            language=language,
            guide_language=guide_language,
            audio_dir_path=audio_dir_path,
            additional_context="Movie-specific context",
        )

    assert output is reference
    assert stage_order == ["audio", "transcribe", "clean", "review", "translate"]
    assert stage_audio.call_args.args[1] == audio_dir_path
    assert transcribe.call_args.kwargs["transcription_kw"] == {
        "additional_context": "Movie-specific context"
    }
    assert review.call_args.kwargs["reviewer_kw"] == {
        "additional_context": "Movie-specific context"
    }
    assert translate.call_args.kwargs["translator_kw"] == {
        "additional_context": "Movie-specific context"
    }
    mismatch_records = [
        record for record in caplog.records if record.getMessage() == mismatch_message
    ]
    assert len(mismatch_records) == 1
    assert mismatch_records[0].levelno == expected_log_level


def test_transcription_stages_use_flat_json_directory(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Store all transcription-stage JSON in one model-local directory.

    Arguments:
        tmp_path: temporary pipeline directory
        monkeypatch: pytest monkeypatch fixture
    """
    series = Series(events=[Subtitle(start=0, end=1_000, text="佢喺度")])
    audio = Mock(spec=AudioSeries)
    model_dir_path = tmp_path / "mimo"
    transcribe = Mock(return_value=series)
    review = Mock(return_value=series)
    translate = Mock(return_value=series)
    monkeypatch.setattr(
        transcription_data, "get_torch_device", Mock(return_value="mps")
    )
    monkeypatch.setattr(transcription_data, "transcribe_series_guided", transcribe)
    monkeypatch.setattr(transcription_data, "review_series_guided", review)
    monkeypatch.setattr(transcription_data, "translate_series_gaps", translate)

    transcription_data._load_or_transcribe_series_guided(
        audio,
        series,
        model_dir_path / "transcribe.srt",
        Language.yue_hant,
        Language.zho_hant,
        overwrite=True,
    )
    transcription_data._load_or_review_series_guided(
        series,
        series,
        model_dir_path / "transcribe_clean_review.srt",
        Language.yue_hant,
        Language.zho_hant,
        overwrite=True,
    )
    transcription_data._load_or_translate_series_gaps(
        series,
        series,
        model_dir_path / "transcribe_clean_review_translate.srt",
        Language.zho_hant,
        Language.yue_hant,
        overwrite=True,
    )

    json_dir_path = model_dir_path / "json"
    assert transcribe.call_args.kwargs["delineation_json_path"] == (
        json_dir_path / "delineation-mps.json"
    )
    assert transcribe.call_args.kwargs["punctuation_json_path"] == (
        json_dir_path / "punctuation-mps.json"
    )

    transcribe.reset_mock()
    transcription_data._load_or_transcribe_series_guided(
        audio,
        series,
        model_dir_path / "transcribe-block.srt",
        Language.yue_hant,
        Language.zho_hant,
        transcription_kw={
            "alignment_mode": transcription_data.TranscriptionAlignmentMode.BLOCK
        },
        overwrite=True,
    )
    assert transcribe.call_args.kwargs["block_delineation_json_path"] == (
        json_dir_path / "block_delineation-mps.json"
    )
    assert transcribe.call_args.kwargs["block_punctuation_json_path"] == (
        json_dir_path / "block_punctuation-mps.json"
    )
    assert "delineation_json_path" not in transcribe.call_args.kwargs
    assert "punctuation_json_path" not in transcribe.call_args.kwargs
    assert review.call_args.kwargs["test_case_path"] == (
        json_dir_path / "guided_review-mps.json"
    )
    assert translate.call_args.kwargs["test_case_path"] == (
        json_dir_path / "gap_translation-mps.json"
    )


def test_process_transcription_uses_traditionalized_output_downstream(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Use the Traditional derivation for downstream stages."""
    reference = Series(events=[Subtitle(start=0, end=1_000, text="佢喺度")])
    traditionalized = Series(events=[Subtitle(start=0, end=1_000, text="佢喺度")])
    reference_path = tmp_path / "reference.srt"
    guide_path = tmp_path / "guide.srt"
    reference.save(reference_path)
    reference.save(guide_path)
    stage_order: list[str] = []
    traditionalize = Mock(
        side_effect=lambda *args, **kwargs: (
            stage_order.append("traditionalize") or traditionalized
        )
    )
    review = Mock(
        side_effect=lambda *args, **kwargs: stage_order.append("review") or reference
    )
    translate = Mock(
        side_effect=lambda *args, **kwargs: stage_order.append("translate") or reference
    )
    monkeypatch.setattr(
        transcription_data,
        "resolve_language",
        Mock(side_effect=lambda series, explicit_language: explicit_language),
    )
    monkeypatch.setattr(
        transcription_data,
        "_stage_audio_series",
        Mock(
            side_effect=lambda *args, **kwargs: stage_order.append("audio") or reference
        ),
    )
    monkeypatch.setattr(
        transcription_data,
        "_load_or_transcribe_series_guided",
        Mock(
            side_effect=lambda *args, **kwargs: (
                stage_order.append("transcribe") or reference
            )
        ),
    )
    monkeypatch.setattr(
        transcription_data,
        "load_or_clean_series",
        Mock(
            side_effect=lambda *args, **kwargs: stage_order.append("clean") or reference
        ),
    )
    monkeypatch.setattr(
        transcription_data, "load_or_traditionalize_series", traditionalize
    )
    monkeypatch.setattr(transcription_data, "_load_or_review_series_guided", review)
    monkeypatch.setattr(transcription_data, "_load_or_translate_series_gaps", translate)

    output = transcription_data.process_transcription(
        tmp_path,
        guide_path,
        reference_path=reference_path,
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        run_traditionalize=True,
    )

    assert output is reference
    assert stage_order == [
        "audio",
        "transcribe",
        "clean",
        "traditionalize",
        "review",
        "translate",
    ]
    assert traditionalize.call_args.args[0] is reference
    assert traditionalize.call_args.args[1] == (
        tmp_path
        / "output"
        / "yue-Hant_transcribe"
        / "transcribe_clean_traditionalize.srt"
    )
    assert review.call_args.args[0] is traditionalized
    assert review.call_args.args[2] == (
        tmp_path
        / "output"
        / "yue-Hant_transcribe"
        / "transcribe_clean_traditionalize_review.srt"
    )
    assert translate.call_args.args[2] == (
        tmp_path
        / "output"
        / "yue-Hant_transcribe"
        / "transcribe_clean_traditionalize_review_translate.srt"
    )


def test_process_transcription_can_stop_after_cleaning(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Skip guided review and gap translation when they are disabled.

    Arguments:
        tmp_path: temporary pipeline directory
        monkeypatch: pytest monkeypatch fixture
    """
    reference = Series(events=[Subtitle(start=0, end=1_000, text="佢喺度")])
    reference_path = tmp_path / "reference.srt"
    guide_path = tmp_path / "guide.srt"
    reference.save(reference_path)
    reference.save(guide_path)
    review = Mock()
    translate = Mock()
    monkeypatch.setattr(
        transcription_data,
        "resolve_language",
        Mock(side_effect=lambda series, explicit_language: explicit_language),
    )
    monkeypatch.setattr(
        transcription_data, "_stage_audio_series", Mock(return_value=reference)
    )
    monkeypatch.setattr(
        transcription_data,
        "_load_or_transcribe_series_guided",
        Mock(return_value=reference),
    )
    monkeypatch.setattr(
        transcription_data, "load_or_clean_series", Mock(return_value=reference)
    )
    monkeypatch.setattr(transcription_data, "_load_or_review_series_guided", review)
    monkeypatch.setattr(transcription_data, "_load_or_translate_series_gaps", translate)

    output = transcription_data.process_transcription(
        tmp_path,
        guide_path,
        reference_path=reference_path,
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        run_review_and_translation=False,
    )

    assert output is reference
    review.assert_not_called()
    translate.assert_not_called()


def test_process_transcription_can_stop_before_cleaning(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Return the transcription without running later stages.

    Arguments:
        tmp_path: temporary pipeline directory
        monkeypatch: pytest monkeypatch fixture
    """
    reference = Series(events=[Subtitle(start=0, end=1_000, text="佢喺度")])
    reference_path = tmp_path / "reference.srt"
    guide_path = tmp_path / "guide.srt"
    reference.save(reference_path)
    reference.save(guide_path)
    clean = Mock()
    review = Mock()
    translate = Mock()
    monkeypatch.setattr(
        transcription_data,
        "resolve_language",
        Mock(side_effect=lambda series, explicit_language: explicit_language),
    )
    monkeypatch.setattr(
        transcription_data, "_stage_audio_series", Mock(return_value=reference)
    )
    monkeypatch.setattr(
        transcription_data,
        "_load_or_transcribe_series_guided",
        Mock(return_value=reference),
    )
    monkeypatch.setattr(transcription_data, "load_or_clean_series", clean)
    monkeypatch.setattr(transcription_data, "_load_or_review_series_guided", review)
    monkeypatch.setattr(transcription_data, "_load_or_translate_series_gaps", translate)

    output = transcription_data.process_transcription(
        tmp_path,
        guide_path,
        reference_path=reference_path,
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        run_cleaning=False,
    )

    assert output is reference
    clean.assert_not_called()
    review.assert_not_called()
    translate.assert_not_called()
