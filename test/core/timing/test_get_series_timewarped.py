#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.timing.get_series_timewarped."""

from __future__ import annotations

from scinoephile.core.subtitles import Series
from scinoephile.core.timing import get_series_timewarped


def _test_get_series_timewarped(anchor: Series, source: Series, expected: Series):
    """Test get_series_timewarped.

    Arguments:
        anchor: anchor subtitle fixture
        source: source subtitle fixture
        expected: expected timewarp subtitle fixture
    """
    output = get_series_timewarped(
        anchor,
        source,
        one_start_idx=1,
        one_end_idx=1421,
        two_start_idx=1,
        two_end_idx=1461,
    )

    assert output == expected


def test_get_series_timewarped_kob(
    kob_zho_hant_fuse_clean_validate_proofread: Series,
    kob_yue_hant: Series,
    kob_yue_hant_timewarp: Series,
):
    """Test get_series_timewarped with KOB subtitles.

    Arguments:
        kob_zho_hant_fuse_clean_validate_proofread: 繁体中文 subtitle fixture
        kob_yue_hant: 繁體粵文 subtitle fixture
        kob_yue_hant_timewarp: expected timewarp subtitle fixture
    """
    _test_get_series_timewarped(
        kob_zho_hant_fuse_clean_validate_proofread,
        kob_yue_hant,
        kob_yue_hant_timewarp,
    )
