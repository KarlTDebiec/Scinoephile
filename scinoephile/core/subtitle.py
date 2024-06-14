#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle."""
from __future__ import annotations

from dataclasses import fields
from typing import Any

from pysubs2 import SSAEvent
from pysubs2.time import ms_to_str


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

    comment: str = ""
    """Comment associated with subtitle."""

    def __eq__(self, other: SSAEvent) -> bool:
        """Whether this subtitle is equal to another.

        Arguments:
            other: Subtitle to which to compare
        Returns:
            Whether this subtitle is equal to another
        """
        return (
            self.start == other.start
            and self.end == other.end
            and self.text == other.text
        )

    def __ne__(self, other) -> bool:
        """Whether this subtitle is not equal to another.

        Arguments:
            other: Subtitle to which to compare
        Returns:
            Whether this subtitle is not equal to another
        """
        return (
            self.start != other.start
            or self.end != other.end
            or self.text != other.text
        )

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} "
            f"start={ms_to_str(self.start,True)} "
            f"end={ms_to_str(self.end,True)} "
            f"text={self.text!r}"
            f">"
        )
