#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle."""
from __future__ import annotations

from dataclasses import fields
from typing import Any

from pysubs2 import SSAEvent


class Subtitle(SSAEvent):
    """Individual subtitle.

    Extension of pysubs2's SSAEvent with additional features.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes.

        Args:
            series (SubtitleSeries): Subtitle series of which this subtitle is a part
            **kwargs: Additional keyword arguments
        """
        super_field_names = {f.name for f in fields(SSAEvent)}
        super_kwargs = {k: v for k, v in kwargs.items() if k in super_field_names}
        super().__init__(**super_kwargs)
