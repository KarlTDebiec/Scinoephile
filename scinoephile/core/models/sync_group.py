#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Synchronization group between two blocks."""

from pydantic import BaseModel, Field


class SyncGroup(BaseModel):
    """Synchronization group between two blocks."""

    one_indexes: list[int] = Field(..., description="Block one subtitle indexes.")
    two_indexes: list[int] = Field(..., description="Block two subtitle indexes.")
