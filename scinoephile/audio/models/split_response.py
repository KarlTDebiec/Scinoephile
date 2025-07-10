#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

from pydantic import BaseModel, Field


class SplitResponse(BaseModel):
    """Synchronization group between two series."""

    one: str = Field(..., description="Input text to append to first subtitle.")
    two: str = Field(..., description="Input text to prepend to second subtitle.")
