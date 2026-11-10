#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Load and edit native proofreading decisions while preserving query history."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from scinoephile.core import Language
from scinoephile.core.llms.utils import load_test_cases_from_json, serialize_test_cases
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.core.text import replace_control_characters
from scinoephile.lang.review.standard import DEFAULT_PROMPTS
from scinoephile.llms.review import ReviewManager, ReviewTestCase

from . import exceptions

__all__ = ["ProofreadingDecisions"]


class ProofreadingDecisions:
    """Native sparse review answers matched to immutable subtitle query blocks."""

    def __init__(self, original: Series, language: Language, json_path: Path):
        """Load an optional existing decision log without creating it.

        Arguments:
            original: immutable source subtitles
            language: proofreading language
            json_path: existing or future native decision JSON
        """
        self.original = original
        self.texts = tuple(s.text_with_newline for s in original)
        self.case_cls = ReviewManager.get_test_case_cls(DEFAULT_PROMPTS[language])
        self.cases: list[ReviewTestCase] = []
        if json_path.exists():
            self.cases = load_test_cases_from_json(
                json_path, ReviewManager, DEFAULT_PROMPTS[language]
            )
        self.locations: dict[int, tuple[int, ...]] = {}
        self.block_ranges: list[tuple[int, int]] = []
        """Nonoverlapping query blocks, with uncovered subtitles grouped by pauses."""
        self._index_cases()

    def edit(self, index: int, text: str, note: str):
        """Edit the answer covering a subtitle and all shared query occurrences.

        Arguments:
            index: zero-based source subtitle index
            text: complete corrected subtitle text
            note: human revision explanation
        Raises:
            ValueError: if native review validation fails
        """
        if not self._get_case_indexes(index):
            self._add_case(index)
        texts, notes = self.render()
        affected = {value - 1 for value in self.shared_indexes(index)}
        for target in affected:
            texts[target] = text
            notes[target] = note.strip() or "Edited in the review browser."
        for case_index, starts in self.locations.items():
            case = self.cases[case_index]
            if not any(
                start + offset in affected
                for start in starts
                for offset in range(len(case.query.subtitles))
            ):
                continue
            revisions = []
            for offset, subtitle in enumerate(case.query.subtitles):
                target = starts[0] + offset
                if texts[target] != subtitle.text:
                    revisions.append(
                        {
                            "index": offset + 1,
                            "text": texts[target],
                            "note": notes[target] or "Edited in the review browser.",
                        }
                    )
            data = case.model_dump(mode="json")
            answer = {"revisions": revisions}
            if data.get("answer") != answer:
                data.update(answer=answer, verified=False, few_shot=False)
            self.cases[case_index] = self.case_cls.model_validate(data)

    def normalize_srt_revisions(self):
        """Normalize active native revisions and check that each fits in SRT.

        Raises:
            InvalidReviewSubtitleError: if a revision cannot round-trip through SRT
        """
        for case_index, starts in self.locations.items():
            case = self.cases[case_index]
            if case.answer is None:
                continue
            revisions = []
            for revision in case.answer.revisions:
                text = replace_control_characters(revision.text)
                text = text.replace("\r\n", "\n").replace("\r", "\n")
                text = text.replace(r"\N", "\n").replace(r"\n", "\n")
                text = text.replace(r"\h", " ").strip()
                cue = Series(events=[Subtitle(start=0, end=1000, text=text)])
                parsed = Series.from_string(cue.to_string("srt"), format_="srt")
                if (
                    not text
                    or len(parsed) != 1
                    or parsed.events[0].text_with_newline != text
                ):
                    raise exceptions.InvalidReviewSubtitleError(
                        f"Subtitle {starts[0] + revision.index} text cannot be saved "
                        "unchanged in SRT."
                    )
                if text != case.query.subtitles[revision.index - 1].text:
                    revisions.append(
                        {"index": revision.index, "text": text, "note": revision.note}
                    )
            data = case.model_dump(mode="json")
            if data["answer"]["revisions"] != revisions:
                data["answer"]["revisions"] = revisions
                self.cases[case_index] = self.case_cls.model_validate(data)

    def render(self) -> tuple[list[str], list[str]]:
        """Apply current sparse answers to their exact original query matches.

        Returns:
            full output text and revision explanations in subtitle order
        Raises:
            ValueError: if overlapping current decisions conflict
        """
        texts = list(self.texts)
        notes = [""] * len(texts)
        assigned: dict[int, str] = {}
        for case_index, starts in self.locations.items():
            case = self.cases[case_index]
            if case.answer is None:
                continue
            revisions = {r.index - 1: r for r in case.answer.revisions}
            for start in starts:
                for offset, subtitle in enumerate(case.query.subtitles):
                    text = subtitle.text
                    note = ""
                    if offset in revisions:
                        text = revisions[offset].text
                        note = revisions[offset].note
                    target = start + offset
                    if target in assigned and assigned[target] != text:
                        raise ValueError(
                            f"Conflicting review decisions for subtitle {target + 1}"
                        )
                    assigned[target] = text
                    texts[target] = text
                    notes[target] = note
        return texts, notes

    def serialize(self) -> str:
        """Serialize with the native base-prompt field names.

        Returns:
            validated native review JSON text
        """
        return serialize_test_cases(self.cases, ReviewManager) + "\n"

    def shared_indexes(self, index: int) -> tuple[int, ...]:
        """Find all row positions linked through reused native query decisions.

        Arguments:
            index: zero-based source subtitle index
        Returns:
            one-based linked subtitle indexes, including this subtitle
        """
        affected = {index}
        if not self._get_case_indexes(index):
            for first, last in self.block_ranges:
                if first <= index < last:
                    query = self.texts[first:last]
                    return tuple(
                        start + index - first + 1
                        for start, stop in self.block_ranges
                        if self.texts[start:stop] == query
                        and not self._get_case_indexes(start)
                    )
        previous = set()
        while affected != previous:
            previous = set(affected)
            for case_index, starts in self.locations.items():
                for offset in range(len(self.cases[case_index].query.subtitles)):
                    linked = {start + offset for start in starts}
                    if affected.intersection(linked):
                        affected.update(linked)
        return tuple(sorted(value + 1 for value in affected))

    def verified_indexes(self) -> set[int]:
        """Find which subtitles have verified proofreading cases.

        Returns:
            zero-based indexes covered by verified cases only
        """
        verified = set()
        pending = set()
        for case_index, starts in self.locations.items():
            case = self.cases[case_index]
            indexes = verified if case.verified else pending
            for start in starts:
                indexes.update(range(start, start + len(case.query.subtitles)))
        return verified - pending

    def verify(self, index: int, *, verified: bool):
        """Set verification on the proofreading cases covering a subtitle.

        Arguments:
            index: zero-based source subtitle index
            verified: whether a human approves the complete proofreading answer
        """
        if verified and not self._get_case_indexes(index):
            self._add_case(index)
        for case_index in self._get_case_indexes(index):
            self._set_case_verified(case_index, verified=verified)

    def verify_blocks(self, ranges: list[tuple[int, int]]):
        """Approve existing cases and record unchanged answers for uncovered subtitles.

        Arguments:
            ranges: complete visible block bounds, zero-based and end-exclusive
        """
        selected = {index for first, last in ranges for index in range(first, last)}
        uncovered = selected.copy()
        for case_index, starts in self.locations.items():
            case = self.cases[case_index]
            covered = {
                index
                for start in starts
                for index in range(start, start + len(case.query.subtitles))
            }
            if covered & selected:
                uncovered.difference_update(covered)
                if not case.verified:
                    self._set_case_verified(case_index, verified=True)

        new_cases = {}
        for first, last in ranges:
            if first in uncovered:
                case = self._build_unchanged_case(first, last, verified=True)
                new_cases[case.query.key] = case
        if new_cases:
            self.cases.extend(new_cases.values())
            self._index_cases()

    def _add_case(self, index: int):
        """Create an unchanged answer for the editor block containing a subtitle.

        Arguments:
            index: zero-based source subtitle index
        """
        for first, last in self.block_ranges:
            if first <= index < last:
                self.cases.append(self._build_unchanged_case(first, last))
                self._index_cases()
                return

    def _build_unchanged_case(
        self, first: int, last: int, *, verified: bool = False
    ) -> ReviewTestCase:
        """Build a native case for subtitles with no proofreading revisions.

        Arguments:
            first: zero-based first subtitle index
            last: exclusive subtitle index
            verified: whether a human has approved the answer
        Returns:
            native case for the selected subtitle range
        """
        return self.case_cls.model_validate(
            {
                "query": {
                    "subtitles": [
                        {"index": offset, "text": text}
                        for offset, text in enumerate(self.texts[first:last], 1)
                    ]
                },
                "answer": {"revisions": []},
                "verified": verified,
                "match_complete_blocks": True,
            }
        )

    def _get_block_ranges(self) -> list[tuple[int, int]]:
        """Derive the block boundaries from native cases and source pauses.

        Returns:
            nonoverlapping zero-based subtitle ranges
        """
        if not self.texts:
            return []
        joined = [False] * (len(self.texts) - 1)
        covered = set()
        for case_index, starts in self.locations.items():
            size = len(self.cases[case_index].query.subtitles)
            for first in starts:
                covered.update(range(first, first + size))
                for index in range(first, first + size - 1):
                    joined[index] = True
        for first, last in Series.get_block_indexes_by_pause(self.original):
            for index in range(first, last - 1):
                if index not in covered and index + 1 not in covered:
                    joined[index] = True
        boundaries = [0]
        boundaries.extend(index + 1 for index, value in enumerate(joined) if not value)
        boundaries.append(len(self.texts))
        return list(zip(boundaries[:-1], boundaries[1:], strict=True))

    def _get_case_indexes(self, index: int) -> list[int]:
        """Find active cases covering a source subtitle.

        Arguments:
            index: zero-based source subtitle index
        Returns:
            indexes into the case list
        """
        return [
            case_index
            for case_index, starts in self.locations.items()
            if any(
                start <= index < start + len(self.cases[case_index].query.subtitles)
                for start in starts
            )
        ]

    def _index_cases(self):
        """Locate the latest native cases, then match approvals to uncovered blocks."""
        self.locations = {}
        block_cases = {}
        latest = {case.query.key: index for index, case in enumerate(self.cases)}
        for case_index in latest.values():
            case = self.cases[case_index]
            query = tuple(s.text for s in case.query.subtitles)
            if case.match_complete_blocks:
                block_cases[query] = case_index
                continue
            starts = tuple(
                start
                for start in range(len(self.texts) - len(query) + 1)
                if self.texts[start : start + len(query)] == query
            )
            if starts:
                self.locations[case_index] = starts

        # Match editor cases after native cases have established the block boundaries
        self.block_ranges = self._get_block_ranges()
        if block_cases:
            block_starts: defaultdict[int, list[int]] = defaultdict(list)
            for first, last in self.block_ranges:
                case_index = block_cases.get(self.texts[first:last])
                if case_index is not None and not self._get_case_indexes(first):
                    block_starts[case_index].append(first)
            self.locations.update(
                (case_index, tuple(starts))
                for case_index, starts in block_starts.items()
            )

    def _set_case_verified(self, case_index: int, *, verified: bool):
        """Update one case using the standard test-case verification rules.

        Arguments:
            case_index: index into the active case list
            verified: whether a human has approved the answer
        """
        data = self.cases[case_index].model_dump(mode="json")
        data["verified"] = verified
        if verified and data["answer"] is None:
            data["answer"] = {"revisions": []}
        if not verified:
            data["few_shot"] = False
        self.cases[case_index] = self.case_cls.model_validate(data)
