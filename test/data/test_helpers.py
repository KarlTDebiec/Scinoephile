#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for shared test-data helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from pytest import MonkeyPatch

import test.data.helpers as data_helpers
from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle


def test_load_or_clean_series_forwards_informational_detected_language(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Forward the informational detected language to subtitle cleaning.

    Arguments:
        tmp_path: temporary output directory
        monkeypatch: pytest monkeypatch fixture
    """
    source = Series(events=[Subtitle(text="佢喺度")])
    cleaned = Series(events=[Subtitle(text="佢喺度")])
    clean_series = Mock(return_value=cleaned)
    monkeypatch.setattr(data_helpers, "clean_series", clean_series)
    output_path = tmp_path / "cleaned.srt"

    output = data_helpers.load_or_clean_series(
        source,
        output_path,
        Language.yue_hant,
        informational_detected_language=Language.zho_hant,
    )

    assert output is cleaned
    assert output_path.exists()
    clean_series.assert_called_once_with(
        source,
        language=Language.yue_hant,
        informational_detected_language=Language.zho_hant,
    )
