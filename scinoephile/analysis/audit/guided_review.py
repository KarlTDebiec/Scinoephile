#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit guided subtitle review decisions and format them as Markdown."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import get_sync_groups
from scinoephile.core.text import remove_punc_and_whitespace

from .review import ReviewAuditFilter
from .utils import (
    AuditResult,
    escape_table_cell,
    format_audit_report,
    is_block_in_range,
    validate_audit_range,
)

__all__ = ["audit_guided_review"]


@dataclass(frozen=True, kw_only=True)
class _GuidedReviewBlock:
    """One target and guide block available for guided review."""

    block_number: int
    """One-based position in the complete block alignment."""
    target_indexes: tuple[int, ...]
    """One-based target subtitle indexes in the block."""
    target_texts: tuple[str, ...]
    """Current target subtitle texts in the block."""
    guide_texts: tuple[str, ...]
    """Guide subtitle texts in the block."""
    aligned_guide_texts: tuple[tuple[str, ...], ...]
    """Timing-aligned guide texts for each target subtitle."""


@dataclass(frozen=True, kw_only=True)
class _GuidedReviewRow:
    """One final per-subtitle guided-review audit row."""

    subtitle_index: int
    """One-based target subtitle index."""
    test_case_index: int
    """One-based position of the source test case in the JSON."""
    markdown: str
    """Formatted Markdown table row."""
    result: AuditResult
    """Result of the logged answer for this subtitle."""
    verified: bool
    """Whether the source test case is verified."""


class _GuidedReviewSubtitle(Protocol):
    """Subtitle fields required for guided-review audit reporting."""

    @property
    def text(self) -> str:
        """Subtitle text.

        Returns:
            subtitle text
        """
        ...


class _GuidedReviewRevision(_GuidedReviewSubtitle, Protocol):
    """Revision fields required for guided-review audit reporting."""

    @property
    def index(self) -> int:
        """One-based query-local target index.

        Returns:
            one-based query-local target index
        """
        ...


class _GuidedReviewAnswer(Protocol):
    """Answer fields required for guided-review audit reporting."""

    @property
    def revisions(self) -> Sequence[_GuidedReviewRevision]:
        """Sparse target revisions.

        Returns:
            sparse target revisions
        """
        ...


class _GuidedReviewQuery(Protocol):
    """Query fields required for guided-review audit reporting."""

    @property
    def guides(self) -> Sequence[_GuidedReviewSubtitle]:
        """Guide subtitles.

        Returns:
            guide subtitles
        """
        ...

    @property
    def targets(self) -> Sequence[_GuidedReviewSubtitle]:
        """Target subtitles.

        Returns:
            target subtitles
        """
        ...


class _GuidedReviewTestCase(Protocol):
    """Test-case fields required for guided-review audit reporting."""

    @property
    def answer(self) -> _GuidedReviewAnswer | None:
        """Optional guided-review answer.

        Returns:
            guided-review answer, if present
        """
        ...

    @property
    def query(self) -> _GuidedReviewQuery:
        """Guided-review query.

        Returns:
            guided-review query
        """
        ...

    @property
    def verified(self) -> bool:
        """Whether the test case has been verified.

        Returns:
            whether the test case has been verified
        """
        ...


def audit_guided_review(
    target: Series,
    guide: Series,
    test_cases: Sequence[_GuidedReviewTestCase],
    *,
    row_filter: ReviewAuditFilter = ReviewAuditFilter.all,
    first_index: int | None = None,
    last_index: int | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
) -> str:
    """Audit logged guided-review decisions by target subtitle.

    Arguments:
        target: target subtitle series provided for guided review
        guide: guide subtitle series provided for guided review
        test_cases: logged guided-review test cases
        row_filter: row status filter
        first_index: first 1-indexed target subtitle number to include
        last_index: last 1-indexed target subtitle number to include
        first_block: first 1-indexed paired block number to include
        last_block: last 1-indexed paired block number to include
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if a logged case cannot be matched uniquely to source data
    """
    block_pairs = get_block_pairs_by_pause(target, guide)
    validate_audit_range(
        first_index,
        last_index,
        first_block,
        last_block,
        block_count=len(block_pairs),
    )
    blocks_by_key = _get_blocks_by_key(block_pairs)
    rows_by_subtitle_index: dict[int, _GuidedReviewRow] = {}

    for test_case_index, test_case, block in _get_active_test_case_blocks(
        target,
        guide,
        test_cases,
        blocks_by_key,
        block_pairs,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    ):
        answer = test_case.answer
        revisions_by_index = (
            {revision.index: revision for revision in answer.revisions}
            if answer is not None
            else {}
        )

        for local_index, (subtitle_index, query_target, guide_texts) in enumerate(
            zip(
                block.target_indexes,
                test_case.query.targets,
                block.aligned_guide_texts,
                strict=False,
            ),
            1,
        ):
            if (first_index is not None and subtitle_index < first_index) or (
                last_index is not None and subtitle_index > last_index
            ):
                continue

            revision = revisions_by_index.get(local_index)

            target_revision = query_target.text
            if answer is None:
                target_revision = f"{query_target.text}\n(unanswered)"
                result = AuditResult.unanswered
            elif revision is not None:
                target_revision = f"{query_target.text}\n{revision.text}"
                result = AuditResult.changed
            else:
                result = AuditResult.unchanged

            guide_text = "\n".join(guide_texts)
            if not guide_texts:
                guide_text = "—"
            cells = (
                str(subtitle_index),
                str(block.block_number),
                guide_text,
                target_revision,
                "",
                "✓" if test_case.verified else "",
            )
            rows_by_subtitle_index[subtitle_index] = _GuidedReviewRow(
                subtitle_index=subtitle_index,
                test_case_index=test_case_index,
                markdown=(
                    f"| {' | '.join(escape_table_cell(cell) for cell in cells)} |"
                ),
                result=result,
                verified=test_case.verified,
            )

    all_rows = sorted(
        rows_by_subtitle_index.values(),
        key=lambda row: (row.subtitle_index, row.test_case_index),
    )
    revised_subtitles = sum(row.result is AuditResult.changed for row in all_rows)
    unanswered_subtitles = sum(row.result is AuditResult.unanswered for row in all_rows)
    verified_subtitles = sum(row.verified for row in all_rows)
    rows = [
        row
        for row in all_rows
        if not (
            row_filter is ReviewAuditFilter.changes
            and row.result is not AuditResult.changed
        )
        and not (row_filter is ReviewAuditFilter.unverified and row.verified)
    ]
    subtitles = len(all_rows)
    unchanged_subtitles = subtitles - revised_subtitles - unanswered_subtitles
    unverified_subtitles = subtitles - verified_subtitles
    return format_audit_report(
        title="Guided Subtitle Review Audit",
        summary_lines=(
            f"- subtitles: {subtitles}",
            f"- revised subtitles: {revised_subtitles}",
            f"- unchanged subtitles: {unchanged_subtitles}",
            f"- unanswered subtitles: {unanswered_subtitles}",
            f"- verified subtitles: {verified_subtitles}",
            f"- unverified subtitles: {unverified_subtitles}",
            f"- row filter: {row_filter.value}",
        ),
        column_labels=(
            "Index",
            "Block",
            "Guide",
            "Target / revision",
            "Notes",
            "Verified",
        ),
        column_separators=("---:", "---:", "---", "---", "---", ":---:"),
        rows=[row.markdown for row in rows],
        first_index=first_index,
        last_index=last_index,
        index_track_name="target",
        first_block=first_block,
        last_block=last_block,
    )


def _get_blocks_by_key(
    block_pairs: Sequence[tuple[Series, Series]],
) -> dict[tuple[tuple[str, ...], tuple[str, ...]], list[_GuidedReviewBlock]]:
    """Index eligible target and guide blocks by their logged text.

    Arguments:
        block_pairs: paired target and guide workflow blocks
    Returns:
        guided-review blocks keyed by target and guide text
    """
    blocks_by_key: dict[
        tuple[tuple[str, ...], tuple[str, ...]],
        list[_GuidedReviewBlock],
    ] = defaultdict(list)
    target_offset = 0
    for block_number, (target_block, guide_block) in enumerate(block_pairs, 1):
        target_indexes = tuple(
            range(target_offset + 1, target_offset + len(target_block) + 1)
        )
        target_offset += len(target_block)
        if not target_block:
            continue

        target_texts = tuple(
            subtitle.text_with_newline.strip() for subtitle in target_block
        )
        guide_texts = tuple(
            subtitle.text_with_newline.strip() for subtitle in guide_block
        )
        aligned_guide_texts: list[tuple[str, ...]] = [()] * len(target_block)
        for target_group, guide_group in get_sync_groups(target_block, guide_block):
            group_guide_texts = tuple(guide_texts[index] for index in guide_group)
            for target_index in target_group:
                aligned_guide_texts[target_index] = group_guide_texts
        key = (_normalize_texts(target_texts), guide_texts)
        blocks_by_key[key].append(
            _GuidedReviewBlock(
                block_number=block_number,
                target_indexes=target_indexes,
                target_texts=target_texts,
                guide_texts=guide_texts,
                aligned_guide_texts=tuple(aligned_guide_texts),
            )
        )
    return blocks_by_key


def _get_active_test_case_blocks(  # noqa: PLR0912
    target: Series,
    guide: Series,
    test_cases: Sequence[_GuidedReviewTestCase],
    blocks_by_key: dict[
        tuple[tuple[str, ...], tuple[str, ...]], list[_GuidedReviewBlock]
    ],
    block_pairs: Sequence[tuple[Series, Series]],
    *,
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
) -> list[tuple[int, _GuidedReviewTestCase, _GuidedReviewBlock]]:
    """Get current cases while ignoring superseded historical cases.

    Persisted guided-review cases are retained after their target block's
    segmentation or guide text changes. A current case with the same guide or
    target block supersedes one of those historical cases. If no current case
    exists, preserve the audit's strict failure rather than assigning stale
    local revision indexes.

    Arguments:
        target: current target subtitle series
        guide: current guide subtitle series
        test_cases: logged guided-review test cases
        blocks_by_key: current guided-review blocks keyed by text
        block_pairs: paired target and guide workflow blocks
        first_index: first included target subtitle number
        last_index: last included target subtitle number
        first_block: first included paired block number
        last_block: last included paired block number
    Returns:
        active test cases paired with their current subtitle blocks
    Raises:
        ScinoephileError: if a selected stale case has no current replacement
            or cannot be matched uniquely
    """
    blocks_by_guides: dict[tuple[str, ...], list[_GuidedReviewBlock]] = defaultdict(
        list
    )
    blocks_by_targets: dict[tuple[str, ...], list[_GuidedReviewBlock]] = defaultdict(
        list
    )
    for blocks in blocks_by_key.values():
        for block in blocks:
            blocks_by_guides[block.guide_texts].append(block)
            blocks_by_targets[_normalize_texts(block.target_texts)].append(block)

    active_cases: list[tuple[int, _GuidedReviewTestCase, _GuidedReviewBlock]] = []
    unmatched_cases: list[tuple[int, _GuidedReviewTestCase]] = []
    for test_case_index, test_case in enumerate(test_cases, 1):
        key = (
            _normalize_texts(tuple(target.text for target in test_case.query.targets)),
            tuple(guide.text for guide in test_case.query.guides),
        )
        matches = blocks_by_key.get(key, [])
        selected_matches = [
            block
            for block in matches
            if _block_intersects_range(
                block,
                first_index,
                last_index,
                first_block,
                last_block,
            )
        ]
        if len(selected_matches) == 1:
            active_cases.append((test_case_index, test_case, selected_matches[0]))
            continue
        if len(selected_matches) > 1:
            block_numbers = ", ".join(
                str(match.block_number) for match in selected_matches
            )
            raise ScinoephileError(
                "Unable to audit guided review: "
                f"test case {test_case_index} is ambiguous; it matches blocks "
                f"{block_numbers}"
            )
        if matches:
            continue
        unmatched_cases.append((test_case_index, test_case))

    active_block_numbers = {block.block_number for _, _, block in active_cases}
    guide_block_numbers = tuple(
        block_number
        for block_number, (_, guide_block) in enumerate(block_pairs, 1)
        for _ in guide_block
    )
    stale_cases: list[tuple[int, _GuidedReviewTestCase, list[_GuidedReviewBlock]]] = []
    for test_case_index, test_case in unmatched_cases:
        key = (
            _normalize_texts(tuple(target.text for target in test_case.query.targets)),
            tuple(guide.text for guide in test_case.query.guides),
        )
        guide_matches = blocks_by_guides.get(key[1], [])
        if guide_matches:
            stale_cases.append((test_case_index, test_case, guide_matches))
        elif any(
            block.block_number in active_block_numbers
            for block in blocks_by_targets.get(key[0], [])
        ):
            continue
        elif not _is_test_case_outside_range(
            test_case,
            target,
            guide,
            guide_block_numbers,
            first_index=first_index,
            last_index=last_index,
            first_block=first_block,
            last_block=last_block,
        ):
            raise ScinoephileError(
                "Unable to audit guided review: "
                f"test case {test_case_index} was not found in the target and guide "
                "subtitle blocks"
            )

    for test_case_index, test_case, matches in stale_cases:
        selected_matches = [
            block
            for block in matches
            if _block_intersects_range(
                block,
                first_index,
                last_index,
                first_block,
                last_block,
            )
        ]
        if not selected_matches or all(
            block.block_number in active_block_numbers for block in selected_matches
        ):
            continue
        if len(selected_matches) > 1:
            block_numbers = ", ".join(
                str(match.block_number) for match in selected_matches
            )
            raise ScinoephileError(
                "Unable to audit guided review: "
                f"test case {test_case_index} is ambiguous; it matches blocks "
                f"{block_numbers}"
            )
        _validate_selected_targets(
            test_case,
            selected_matches[0],
            first_index=first_index,
            last_index=last_index,
            test_case_index=test_case_index,
        )
        active_cases.append((test_case_index, test_case, selected_matches[0]))

    return active_cases


def _block_intersects_range(
    block: _GuidedReviewBlock,
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
) -> bool:
    """Check whether a guided-review block intersects an audit range.

    Arguments:
        block: guided-review block to check
        first_index: first included target subtitle number
        last_index: last included target subtitle number
        first_block: first included paired block number
        last_block: last included paired block number
    Returns:
        whether any target subtitle in the block is selected
    """
    return (
        is_block_in_range(block.block_number, first_block, last_block)
        and (first_index is None or block.target_indexes[-1] >= first_index)
        and (last_index is None or block.target_indexes[0] <= last_index)
    )


def _validate_selected_targets(
    test_case: _GuidedReviewTestCase,
    block: _GuidedReviewBlock,
    *,
    first_index: int | None,
    last_index: int | None,
    test_case_index: int,
):
    """Validate selected logged targets against the current target block.

    This permits an audit of an unaffected prefix after later upstream
    delineation changes while rejecting selected rows whose indexing changed.

    Arguments:
        test_case: guided-review test case to validate
        block: current target and guide block matched to the case
        first_index: first included target subtitle number
        last_index: last included target subtitle number
        test_case_index: one-based test case position used in errors
    Raises:
        ScinoephileError: if selected logged targets no longer match current indexes
    """
    query_targets = tuple(target.text for target in test_case.query.targets)
    selected_positions = [
        position
        for position, subtitle_index in enumerate(block.target_indexes)
        if (first_index is None or subtitle_index >= first_index)
        and (last_index is None or subtitle_index <= last_index)
    ]
    if not selected_positions:
        return

    for position in selected_positions:
        if position >= len(query_targets) or _normalize_texts(
            (query_targets[position],)
        ) != _normalize_texts((block.target_texts[position],)):
            subtitle_index = block.target_indexes[position]
            raise ScinoephileError(
                "Unable to audit guided review: "
                f"test case {test_case_index} target segmentation no longer "
                f"matches subtitle index {subtitle_index}"
            )

    includes_block_end = last_index is None or last_index >= block.target_indexes[-1]
    if len(query_targets) != len(block.target_texts) and includes_block_end:
        raise ScinoephileError(
            "Unable to audit guided review: "
            f"test case {test_case_index} target block length changed from "
            f"{len(query_targets)} to {len(block.target_texts)} subtitles"
        )


def _normalize_texts(texts: tuple[str, ...]) -> tuple[str, ...]:
    """Normalize target texts for matching across punctuation-only changes.

    Arguments:
        texts: target subtitle texts
    Returns:
        texts without punctuation or whitespace
    """
    return tuple(remove_punc_and_whitespace(text) for text in texts)


def _is_test_case_outside_range(
    test_case: _GuidedReviewTestCase,
    target: Series,
    guide: Series,
    guide_block_numbers: Sequence[int],
    *,
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
) -> bool:
    """Check whether an unmatched case is provably outside a bounded range.

    Later upstream changes can alter block grouping outside the requested audit
    range. Match the logged guide sequence directly by text and timing so those
    irrelevant cases do not prevent a partial audit.

    Arguments:
        test_case: unmatched guided-review test case
        target: current target subtitle series
        guide: current guide subtitle series
        guide_block_numbers: paired block number for every guide subtitle
        first_index: first included target subtitle number
        last_index: last included target subtitle number
        first_block: first included paired block number
        last_block: last included paired block number
    Returns:
        whether every matching guide sequence lies outside the target time range
    """
    if all(
        boundary is None
        for boundary in (first_index, last_index, first_block, last_block)
    ):
        return False

    first_target_index = 0
    if first_index is not None:
        first_target_index = first_index - 1
    last_target_index = len(target) - 1
    if last_index is not None:
        last_target_index = min(last_index, len(target)) - 1
    if (
        not target
        or first_target_index >= len(target)
        or last_target_index < first_target_index
    ):
        return True

    selected_start = target[first_target_index].start
    selected_end = target[last_target_index].end
    query_guides = tuple(item.text for item in test_case.query.guides)
    if not query_guides:
        return False
    guide_texts = tuple(subtitle.text_with_newline.strip() for subtitle in guide)
    starts = [
        index
        for index in range(len(guide_texts) - len(query_guides) + 1)
        if guide_texts[index : index + len(query_guides)] == query_guides
    ]
    if not starts:
        return False
    outside_selected_ranges = []
    for start in starts:
        stop = start + len(query_guides)
        outside_index_range = (
            guide[stop - 1].end < selected_start or guide[start].start > selected_end
        )
        outside_block_range = all(
            not is_block_in_range(block_number, first_block, last_block)
            for block_number in guide_block_numbers[start:stop]
        )
        outside_selected_ranges.append(outside_index_range or outside_block_range)
    return all(outside_selected_ranges)
