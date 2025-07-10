#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Synchronization group between two series."""

from pydantic import BaseModel, Field


class SyncGroup(BaseModel):
    """Synchronization group between two series."""

    one_indexes: list[int] = Field(..., description="Series one subtitle indexes.")
    two_indexes: list[int] = Field(..., description="Series two subtitle indexes.")
