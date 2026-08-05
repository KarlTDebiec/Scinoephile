#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for reviewing multiple subtitle sources using a guide."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["MultiReviewPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class MultiReviewPrompt(Prompt):
    """Text for reviewing equal-status subtitle sources using a guide."""

    boundary_aware: bool = False
    """Whether outputs must reconcile provisional boundaries across the block."""

    minimum_duplicate_fragment_characters: int = 4
    """Minimum normalized fragment length checked for conflicting duplication."""

    # Query fields
    sources: str = "sources"
    """Name of sources field in query."""

    sources_desc: str = "Named equal-status subtitle sources for the same passage."
    """Description of sources field in query."""

    guides: str = "guides"
    """Name of guides field in query."""

    guides_desc: str = "Complete guide subtitles for the same passage."
    """Description of guides field in query."""

    # Answer fields
    outputs: str = "outputs"
    """Name of outputs field in answer."""

    outputs_desc: str = "Reviewed outputs corresponding to every guide subtitle."
    """Description of outputs field in answer."""

    # Source fields
    source_name: str = "name"
    """Name of name field in source items."""

    source_name_desc: str = "Stable name identifying the subtitle source."
    """Description of name field in source items."""

    subtitles: str = "subtitles"
    """Name of subtitles field in source items."""

    subtitles_desc: str = "Sparse subtitles from this source, indexed by guide."
    """Description of subtitles field in source items."""

    # Subtitle fields
    index: str = "index"
    """Name of index field in subtitle items."""

    index_desc: str = "One-based guide subtitle index."
    """Description of index field in subtitle items."""

    text: str = "text"
    """Name of text field in subtitle items."""

    source_text_desc: str = "Subtitle transcription from this source."
    """Description of text field in source subtitle items."""

    guide_text_desc: str = "Guide subtitle text."
    """Description of text field in guide subtitle items."""

    output_text_desc: str = (
        "Full reviewed subtitle text, or an empty string when every source is absent."
    )
    """Description of text field in output subtitle items."""

    # Validation errors
    guide_indices_err: str = (
        "Query guide indexes must be consecutive, ordered, and begin at 1."
    )
    """Error when query guide indexes are invalid."""

    source_count_err: str = "Query must contain at least two subtitle sources."
    """Error when a query contains fewer than two sources."""

    source_name_err: str = "Query source names must be nonblank and unique."
    """Error when source names are blank or duplicated."""

    source_indices_err: str = (
        "Each query source's subtitle indexes must be unique and in ascending order."
    )
    """Error when source subtitle indexes are invalid."""

    source_index_missing_err: str = (
        "Every query source subtitle index must correspond to a guide index."
    )
    """Error when a source subtitle index is absent from the guide."""

    output_indices_err: str = (
        "Answer output indexes must be consecutive, ordered, and begin at 1."
    )
    """Error when answer output indexes are invalid."""

    output_correspondence_err: str = (
        "Answer output indexes must correspond exactly to query guide indexes."
    )
    """Error when answer outputs do not correspond to guides."""

    unsupported_output_err_tpl: str = (
        "Answer output {idx} must be blank because every subtitle source is absent."
    )
    """Error template when an unsupported output contains text."""

    conflicting_boundary_duplication_err_tpl: str = (
        "Answer outputs {one_idx} and {two_idx} reuse fragment {fragment!r} from "
        "conflicting whole-versus-split source boundaries. Reconcile the boundary "
        "once across the complete block; do not emit the same spoken fragment twice."
    )
    """Error template when outputs duplicate a conflicting boundary fragment."""

    def conflicting_boundary_duplication_err(
        self, one_idx: int, two_idx: int, fragment: str
    ) -> str:
        """Get error when adjacent outputs reuse a conflicting source fragment.

        Arguments:
            one_idx: first one-based output index
            two_idx: second one-based output index
            fragment: duplicated normalized output fragment
        Returns:
            error message
        """
        return self.conflicting_boundary_duplication_err_tpl.format(
            one_idx=one_idx, two_idx=two_idx, fragment=fragment
        )

    def unsupported_output_err(self, idx: int) -> str:
        """Get error when an unsupported output contains text.

        Arguments:
            idx: one-based guide subtitle index
        Returns:
            error message
        """
        return self.unsupported_output_err_tpl.format(idx=idx)
