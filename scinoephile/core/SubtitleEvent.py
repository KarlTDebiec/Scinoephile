#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from typing import Any

from pysubs2 import SSAEvent
from pysubs2.time import ms_to_str

from scinoephile.core.Base import Base


class SubtitleEvent(Base, SSAEvent):  # type: ignore
    """
    An individual subtitle.

    Extension of pysubs2's SSAEvent with additional features.
    """

    fields = {
        "start",
        "end",
        "text",
        "marked",
        "layer",
        "style",
        "name",
        "marginl",
        "marginr",
        "marginv",
        "effect",
        "type",
    }

    # region Builtins

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes.

        Args:
            series (SubtitleSeries): Subtitle series of which this subtitle is
              a part
            **kwargs: Additional keyword arguments
        """
        super().__init__(**{k: v for k, v in kwargs.items() if k not in self.fields})

        # SSAEvent.__init__ accepts arguments
        SSAEvent.__init__(self, **{k: v for k, v in kwargs.items() if k in self.fields})

    def __str__(self) -> str:
        return (
            f"<{self.__class__.__name__}— "
            f"type={self.type} "
            f"start={ms_to_str(self.start)} "
            f"end={ms_to_str(self.end)} "
            f"text='{self.text}'>"
        )

    # endregion
