#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from pydantic import BaseModel, create_model


def get_sync_notes_response_model(language: str, count: int) -> BaseModel:
    model_name = f"SyncNotes{language.capitalize()}{count}ResponseModel"
    keys = [f"{language}_{i}" for i in range(1, count + 1)]
    fields = {key: (str, ...) for key in keys}
    model = create_model(model_name, **fields)

    return model
