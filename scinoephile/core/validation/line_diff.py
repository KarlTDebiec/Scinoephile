#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Line-level diff records."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.validation.line_diff_kind import LineDiffKind

__all__ = ["LineDiff"]


@dataclass(frozen=True)
class LineDiff:
    """Represents a line-level difference."""

    kind: LineDiffKind
    one_lbl: str | None = None
    two_lbl: str | None = None
    one_idxs: list[int] | None = None
    two_idxs: list[int] | None = None
    one_texts: list[str] | None = None
    two_texts: list[str] | None = None

    @staticmethod
    def _format_idxs(idxs: list[int]) -> str:
        if len(idxs) == 1:
            return str(idxs[0] + 1)
        return f"{idxs[0] + 1}-{idxs[-1] + 1}"

    def __str__(self) -> str:
        """Format the diff as a display string."""
        if self.one_idxs and self.one_texts and self.two_idxs is None:
            missing_idx = self.one_idxs[0]
            missing_text = self.one_texts[0]
            return (
                f"{self.kind.value}: "
                f"{self.one_lbl}[{missing_idx + 1}] "
                f"{missing_text!r} not present in {self.two_lbl}"
            )
        one_idxs = self.one_idxs or []
        two_idxs = self.two_idxs or []
        one_texts = self.one_texts or []
        two_texts = self.two_texts or []
        use_list_repr = len(one_idxs) != 1 or len(two_idxs) != 1
        one_text_repr = repr(one_texts) if use_list_repr else repr(one_texts[0])
        two_text_repr = repr(two_texts) if use_list_repr else repr(two_texts[0])
        return (
            f"{self.kind.value}: "
            f"{self.one_lbl}[{self._format_idxs(one_idxs)}] -> "
            f"{self.two_lbl}[{self._format_idxs(two_idxs)}]: "
            f"{one_text_repr} -> {two_text_repr}"
        )
