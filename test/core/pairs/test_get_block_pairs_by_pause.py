#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of paired subtitle block construction."""

from __future__ import annotations

from scinoephile.core.pairs import (
    get_block_pair_indexes_by_pause,
    get_block_pairs_by_pause,
)
from scinoephile.core.subtitles import Series


def test_get_block_pairs_by_pause_kob(kob_yue_hans: Series, kob_eng: Series):
    """Test get_block_pairs_by_pause with KOB simplified written Cantonese.

    Arguments:
        kob_yue_hans: KOB simplified written Cantonese series fixture
        kob_eng: KOB English series fixture
    """
    block_pairs = get_block_pairs_by_pause(kob_yue_hans, kob_eng)
    block_pair_indexes = get_block_pair_indexes_by_pause(kob_yue_hans, kob_eng)

    assert len(block_pairs) == 193
    assert len(block_pair_indexes) == len(block_pairs)
    assert block_pair_indexes[0] == ((0, 1), (0, 1))
    assert block_pair_indexes[-1] == ((1459, 1461), (1448, 1450))
    first_one_block, first_two_block = block_pairs[0]
    assert len(first_one_block) == 1
    assert len(first_two_block) == 1
    assert first_one_block[0].start == 136970
    assert first_two_block[0].start == 136970
    assert first_one_block[0].text == "少爷！准备好喇"
    assert first_two_block[0].text == "Young master, we are ready"

    last_one_block, last_two_block = block_pairs[-1]
    assert len(last_one_block) == 2
    assert len(last_two_block) == 2
    assert last_one_block[0].start == 5931306
    assert last_two_block[0].start == 5931348
