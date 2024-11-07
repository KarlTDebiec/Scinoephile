#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for OpenAI Service."""
from __future__ import annotations

import pytest

from scinoephile.core import SubtitleSeries
from scinoephile.synchronization import SynchronizationService
from ..data.mnt import mnt_input_english, mnt_input_hanzi


@pytest.fixture
def synchronization_service():
    return SynchronizationService()


def test_get_sync_notes(
    synchronization_service: SynchronizationService,
    mnt_input_hanzi: SubtitleSeries,
    mnt_input_english: SubtitleSeries,
) -> None:
    synced = synchronization_service.get_synced(mnt_input_hanzi, mnt_input_english)
