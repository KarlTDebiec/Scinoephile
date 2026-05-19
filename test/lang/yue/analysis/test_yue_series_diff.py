#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Cantonese-flexible series diffing."""

from __future__ import annotations

import pytest

from scinoephile.analysis.diff import LineDiffKind, SeriesDiff
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.yue.analysis import YueSeriesDiff

ANSI_RESET = "\x1b[0m"
ANSI_YELLOW = "\x1b[33m"
ANSI_PURPLE = "\x1b[35m"


def _get_series(*texts: str) -> Series:
    """Build a compact subtitle series for Cantonese analysis tests.

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


def test_series_diff_remains_exact_for_yue_characters():
    """Test generic diffing still reports Cantonese character substitutions."""
    diff = SeriesDiff(_get_series("辛苦啦！少爷"), _get_series("辛苦喇！少爷"))

    messages = list(diff)

    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.EDIT


@pytest.mark.parametrize(
    ("one", "two"),
    [
        ("辛苦啦！少爷", "辛苦喇！少爷"),
        ("好字呀！龙飞凤舞，苏察哈尔灿", "好字　！龙飞凤舞，苏察哈尔灿"),
        ("爹　爹，我哋苏察哈尔家", "爹阿爹，我地苏察哈尔家"),
        ("而家唔系啦，我个仔，你个孙阿灿呢", "而家唔系喇，我个仔　你个孙阿灿呢"),
        ("睇下你咪知啦", "睇吓你咪知啰"),
        ("因为我哋几个加埋都未必系佢对手", "因为我地几个加埋都未必系佢对手"),
    ],
)
def test_yue_series_diff_suppresses_discretionary_diffs(one: str, two: str):
    """Test Cantonese diffing suppresses known discretionary diffs.

    Arguments:
        one: first subtitle text
        two: second subtitle text
    """
    diff = YueSeriesDiff(_get_series(one), _get_series(two))

    assert list(diff) == []


def test_yue_series_diff_keeps_content_changes():
    """Test Cantonese diffing still reports substantive edits."""
    diff = YueSeriesDiff(
        _get_series("我哋苏察哈尔灿"),
        _get_series("我地苏察哈尔康"),
    )

    messages = list(diff)

    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.EDIT


def test_yue_series_diff_keeps_lexical_spacing_particles():
    """Test Cantonese diffing reports lexical spacing particle deletions."""
    diff = YueSeriesDiff(_get_series("阿灿"), _get_series("灿"))

    messages = list(diff)

    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.EDIT


def test_yue_series_diff_skips_empty_normalized_lines():
    """Test Cantonese diffing ignores lines empty after Yue normalization."""
    diff = YueSeriesDiff(_get_series("！"), _get_series(""))

    assert list(diff) == []


def test_yue_series_diff_colored_equal_highlights_ignored_diffs():
    """Test colored equal output highlights ignored Cantonese variants."""
    diff = YueSeriesDiff(_get_series("辛苦啦！少爷"), _get_series("辛苦喇！少爷"))

    rendered = diff.get_stacked_str(color=True, include_equal=True)

    assert f"{ANSI_YELLOW}啦{ANSI_RESET}" in rendered
    assert f"{ANSI_YELLOW}喇{ANSI_RESET}" in rendered
    assert ANSI_PURPLE not in rendered


def test_yue_series_diff_colored_edit_distinguishes_ignored_and_real_diffs():
    """Test colored edit output distinguishes ignored and substantive edits."""
    diff = YueSeriesDiff(
        _get_series("我哋苏察哈尔灿"),
        _get_series("我地苏察哈尔康"),
    )

    rendered = diff.get_stacked_str(color=True)

    assert f"{ANSI_YELLOW}哋{ANSI_RESET}" in rendered
    assert f"{ANSI_YELLOW}地{ANSI_RESET}" in rendered
    assert f"{ANSI_PURPLE}灿{ANSI_RESET}" in rendered
    assert f"{ANSI_PURPLE}康{ANSI_RESET}" in rendered
