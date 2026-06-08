#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Cantonese-flexible series character error rate."""

from __future__ import annotations

from scinoephile.analysis.character_error_rate import SeriesCER
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.yue.analysis import YueLineCER, YueSeriesCER


def _get_series(*texts: str) -> Series:
    """Build a compact subtitle series for Cantonese CER tests.

    Arguments:
        *texts: subtitle event texts
    Returns:
        subtitle series with one event per text
    """
    return Series(
        events=[
            Subtitle(start=idx * 1000, end=idx * 1000 + 500, text=text)
            for idx, text in enumerate(texts)
        ]
    )


def test_series_cer_remains_exact_for_yue_characters():
    """Test generic CER still counts Cantonese character substitutions."""
    result = SeriesCER(_get_series("辛苦啦！少爷"), _get_series("辛苦喇！少爷"))

    assert result.cer == 0.2
    assert result.substitutions == 1
    assert result.insertions == 0
    assert result.deletions == 0
    assert result.correct == 4
    assert result.reference_length == 5


def test_yue_series_cer_suppresses_discretionary_diffs():
    """Test Cantonese CER suppresses known discretionary character diffs."""
    result = YueSeriesCER(
        _get_series(
            "睇下你咪知啦",
            "做乜㖞",
            "掉转咗呀！老爷",
            "　　好叻呀！原来少爷识写自己个名㖞　系呀！",
        ),
        _get_series(
            "睇吓你咪知啰",
            "做乜喎",
            "调转咗呀，老爷",
            "哗，好叻呀！原来少爷识写自己个名喎，系呀　",
        ),
    )

    assert result.cer == 0.0
    assert result.substitutions == 0
    assert result.insertions == 0
    assert result.deletions == 0
    assert result.correct == 28
    assert result.reference_length == 28


def test_yue_series_cer_keeps_content_changes():
    """Test Cantonese CER still reports substantive edits."""
    result = YueSeriesCER(
        _get_series("我哋苏察哈尔灿"),
        _get_series("我地苏察哈尔康"),
    )

    assert result.cer == 1 / 7
    assert result.substitutions == 1
    assert result.insertions == 0
    assert result.deletions == 0
    assert result.correct == 6
    assert result.reference_length == 7


def test_yue_line_cer_uses_yue_normalized_reference_length():
    """Test line CER divides by the Yue-normalized reference length."""
    result = YueLineCER("爹阿爹灿", "爹　爹康")

    assert result.cer == 1 / 3
    assert result.substitutions == 1
    assert result.insertions == 0
    assert result.deletions == 0
    assert result.correct == 2
    assert result.reference_length == 3


def test_yue_series_cer_uses_yue_normalized_reference_length():
    """Test series CER divides by the Yue-normalized reference length."""
    result = YueSeriesCER(
        _get_series("爹阿爹灿"),
        _get_series("爹　爹康"),
    )

    assert result.cer == 1 / 3
    assert result.substitutions == 1
    assert result.insertions == 0
    assert result.deletions == 0
    assert result.correct == 2
    assert result.reference_length == 3


def test_yue_series_cer_keeps_lexical_spacing_particles():
    """Test series CER counts lexical spacing particle deletions."""
    result = YueSeriesCER(_get_series("阿灿"), _get_series("灿"))

    assert result.cer == 1 / 2
    assert result.substitutions == 0
    assert result.insertions == 0
    assert result.deletions == 1
    assert result.correct == 1
    assert result.reference_length == 2
