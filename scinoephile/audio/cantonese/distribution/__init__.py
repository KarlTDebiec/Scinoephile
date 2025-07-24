#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to distributing Cantonese audio transcription."""

from __future__ import annotations

from scinoephile.audio.cantonese.distribution.distribute_answer import DistributeAnswer
from scinoephile.audio.cantonese.distribution.distribute_query import DistributeQuery
from scinoephile.audio.cantonese.distribution.distribute_test_case import (
    DistributeTestCase,
)
from scinoephile.audio.cantonese.distribution.distributor import Distributor

__all__ = [
    "DistributeAnswer",
    "DistributeQuery",
    "DistributeTestCase",
    "Distributor",
]
