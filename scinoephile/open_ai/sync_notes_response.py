#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

from __future__ import annotations

from pydantic import BaseModel


class SyncNotesResponse(BaseModel):
    chinese: list[str]
    english: list[str]
