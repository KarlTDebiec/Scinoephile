#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Calibrate reference-free subtitle display timing on Cantonese test corpora."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Any

from scinoephile.analysis.transcription_alignment import (
    SubtitleTimingSettings,
    TranscriptionAlignmentArtifact,
)
from scinoephile.analysis.transcription_timing import (
    TranscriptionTimingMetrics,
    evaluate_transcription_timing,
    get_transcription_alignment_with_timing,
)
from scinoephile.core.subtitles import Series
from test.data.transcription import _save_evaluation
from test.helpers import test_data_root

__all__ = ["calibrate_transcription_timing"]


@dataclass(frozen=True, slots=True)
class _Dataset:
    """One aligned transcription artifact and independent reference."""

    name: str
    output_path: Path
    reference_path: Path


_DATASETS = (
    _Dataset(
        "acopopb",
        test_data_root / "acopopb" / "output" / "yue-Hant_transcribe",
        test_data_root
        / "acopopb"
        / "output"
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten.srt",
    ),
    _Dataset(
        "acoptc",
        test_data_root / "acoptc" / "output" / "yue-Hant_transcribe",
        test_data_root
        / "acoptc"
        / "output"
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten.srt",
    ),
    _Dataset(
        "kob",
        test_data_root / "kob" / "output" / "yue-Hant_transcribe",
        test_data_root
        / "kob"
        / "output"
        / "yue-Hant"
        / "clean_review_flatten_timewarp.srt",
    ),
    _Dataset(
        "tmm",
        test_data_root / "tmm" / "output" / "yue-Hant_transcribe",
        test_data_root
        / "tmm"
        / "output"
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten.srt",
    ),
)


def calibrate_transcription_timing(
    *, apply: bool = False, output_path: Path | None = None
) -> dict[str, Any]:
    """Evaluate a global timing grid and optionally apply the best policy.

    The references are used only to score fixed merged text, subtitle breaks, and
    CTC speech bounds. Applying a policy changes display padding only.

    Arguments:
        apply: whether to retime each artifact and regenerate its SRT and audit
        output_path: optional calibration result JSON path
    Returns:
        serializable calibration result ordered by aggregate temporal IoU
    """
    loaded = {
        dataset.name: (
            dataset,
            TranscriptionAlignmentArtifact.load(dataset.output_path / "alignment.json"),
            Series.load(dataset.reference_path),
        )
        for dataset in _DATASETS
    }
    results: list[dict[str, Any]] = []
    for lead_in, lead_out, minimum_duration in product(
        (index / 20 for index in range(16)),
        (index / 20 for index in range(16)),
        (0.5, 0.75, 1.0, 1.25, 1.5),
    ):
        settings = SubtitleTimingSettings(
            lead_in_seconds=lead_in,
            lead_out_seconds=lead_out,
            minimum_duration_seconds=minimum_duration,
        )
        metrics = {
            name: evaluate_transcription_timing(artifact, reference, settings)
            for name, (_, artifact, reference) in loaded.items()
        }
        results.append(_serialize_result(settings, metrics))
    results.sort(
        key=lambda result: (
            result["aggregate"]["micro_intersection_over_union"],
            result["aggregate"]["mean_reference_coverage"],
            -result["aggregate"]["mean_absolute_boundary_error_ms"],
        ),
        reverse=True,
    )
    calibration: dict[str, Any] = {
        "format": "scinoephile-transcription-timing-calibration",
        "version": 1,
        "objective": "aggregate_micro_intersection_over_union",
        "datasets": list(loaded),
        "best": results[0],
        "results": results,
    }
    if output_path is None:
        output_path = Path(__file__).parents[2] / "local" / "transcription_timing.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(calibration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if apply:
        best_settings = SubtitleTimingSettings.model_validate(results[0]["settings"])
        for dataset, artifact, reference in loaded.values():
            retimed = get_transcription_alignment_with_timing(artifact, best_settings)
            retimed.save(dataset.output_path / "alignment.json")
            retimed.get_series().save(dataset.output_path / "transcribe.srt")
            _save_evaluation(dataset.output_path, retimed, reference)
    return calibration


def _serialize_result(
    settings: SubtitleTimingSettings, metrics: dict[str, TranscriptionTimingMetrics]
) -> dict[str, Any]:
    """Serialize one global setting and its aggregate and per-dataset scores."""
    pairs = [pair for metric in metrics.values() for pair in metric.pairs]
    one_to_one_pairs = [
        pair
        for pair in pairs
        if len(pair.candidate_indexes) == len(pair.reference_indexes) == 1
    ]
    total_union_ms = sum(pair.union_ms for pair in pairs)
    total_intersection_ms = sum(pair.intersection_ms for pair in pairs)
    one_to_one_union_ms = sum(pair.union_ms for pair in one_to_one_pairs)
    return {
        "settings": settings.model_dump(mode="json"),
        "aggregate": {
            "text_aligned_groups": len(pairs),
            "micro_intersection_over_union": (
                total_intersection_ms / total_union_ms if total_union_ms else 0.0
            ),
            "one_to_one_groups": len(one_to_one_pairs),
            "one_to_one_micro_intersection_over_union": (
                sum(pair.intersection_ms for pair in one_to_one_pairs)
                / one_to_one_union_ms
                if one_to_one_union_ms
                else 0.0
            ),
            "mean_reference_coverage": (
                sum(pair.reference_coverage for pair in pairs) / len(pairs)
                if pairs
                else 0.0
            ),
            "mean_absolute_boundary_error_ms": (
                sum(abs(pair.start_error_ms) + abs(pair.end_error_ms) for pair in pairs)
                / (2 * len(pairs))
                if pairs
                else 0.0
            ),
        },
        "datasets": {
            name: {
                "text_aligned_groups": len(metric.pairs),
                "micro_intersection_over_union": (metric.micro_intersection_over_union),
                "one_to_one_groups": len(metric.one_to_one_pairs),
                "one_to_one_micro_intersection_over_union": (
                    metric.one_to_one_micro_intersection_over_union
                ),
                "mean_reference_coverage": metric.mean_reference_coverage,
                "mean_start_error_ms": metric.mean_start_error_ms,
                "mean_end_error_ms": metric.mean_end_error_ms,
                "mean_absolute_start_error_ms": (metric.mean_absolute_start_error_ms),
                "mean_absolute_end_error_ms": metric.mean_absolute_end_error_ms,
            }
            for name, metric in metrics.items()
        },
    }


def main():
    """Calibrate timing from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="apply the best policy to all four artifacts and regenerate evaluations",
    )
    arguments = parser.parse_args()
    calibration = calibrate_transcription_timing(apply=arguments.apply)
    print(json.dumps(calibration["best"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
