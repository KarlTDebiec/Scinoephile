#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Load and edit native proofreading decisions while preserving query history."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from scinoephile.core import Language
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.core.text import replace_control_characters
from scinoephile.lang.review.standard import DEFAULT_PROMPTS
from scinoephile.llms.review import ReviewManager, ReviewTestCase

from . import exceptions

__all__ = ["ProofreadingDecisions"]


class ProofreadingDecisions:
    """Saved proofreading answers matched to complete subtitle blocks."""

    def __init__(self, original: Series, language: Language, json_path: Path):
        """Load an optional existing decision log without creating it.

        Arguments:
            original: original subtitles
            language: proofreading language
            json_path: path to the proofreading JSON file
        """
        self.texts = tuple(s.text_with_newline for s in original)
        self.block_ranges = Series.get_block_indexes_by_pause(original)
        """Nonoverlapping subtitle blocks used for proofreading."""
        self._block_starts: defaultdict[tuple[str, ...], list[int]] = defaultdict(list)
        for first, last in self.block_ranges:
            self._block_starts[self.texts[first:last]].append(first)
        self.case_cls = ReviewManager.get_test_case_cls(DEFAULT_PROMPTS[language])
        self.cases: list[ReviewTestCase] = []
        if json_path.exists():
            self.cases = load_test_cases_from_json(
                json_path, ReviewManager, DEFAULT_PROMPTS[language]
            )
        self.locations: dict[int, tuple[int, ...]] = {}
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
        location = self._get_case_location(index) or self._add_case(index)
        if location is None:
            return
        case_index, subtitle_index = location
        data = self.cases[case_index].model_dump(mode="json")
        revisions = {}
        if data["answer"] is not None:
            revisions = {
                revision["index"]: revision for revision in data["answer"]["revisions"]
            }
        if text == self.texts[index]:
            revisions.pop(subtitle_index, None)
        else:
            revisions[subtitle_index] = {
                "index": subtitle_index,
                "text": text,
                "note": note.strip() or "Edited in the review browser.",
            }
        answer = {"revisions": [revisions[index] for index in sorted(revisions)]}
        if data["answer"] != answer:
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
        """Apply current sparse answers to the matching original blocks.

        Returns:
            full output text and revision explanations in subtitle order
        """
        texts = list(self.texts)
        notes = [""] * len(texts)
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
                    texts[target] = text
                    notes[target] = note
        return texts, notes

    def shared_indexes(self, index: int) -> tuple[int, ...]:
        """Find the same subtitle position in each identical block.

        Arguments:
            index: zero-based source subtitle index
        Returns:
            one-based linked subtitle indexes, including this subtitle
        """
        for first, last in self.block_ranges:
            if first <= index < last:
                return tuple(
                    start + index - first + 1
                    for start in self._block_starts[self.texts[first:last]]
                )
        return (index + 1,)

    def verified_indexes(self) -> set[int]:
        """Find which subtitles have verified proofreading cases.

        Returns:
            zero-based indexes covered by verified cases
        """
        verified = set()
        for case_index, starts in self.locations.items():
            case = self.cases[case_index]
            if case.verified:
                for start in starts:
                    verified.update(range(start, start + len(case.query.subtitles)))
        return verified

    def verify(self, index: int, *, verified: bool):
        """Set verification on the proofreading case covering a subtitle.

        Arguments:
            index: zero-based source subtitle index
            verified: whether a human approves the complete proofreading answer
        """
        location = self._get_case_location(index)
        if verified and location is None:
            location = self._add_case(index)
        if location is not None:
            self._set_case_verified(location[0], verified=verified)

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

    def _add_case(self, index: int) -> tuple[int, int] | None:
        """Create an unchanged answer for the editor block containing a subtitle.

        Arguments:
            index: zero-based source subtitle index
        Returns:
            case index and one-based subtitle index, if the subtitle exists
        """
        for first, last in self.block_ranges:
            if first <= index < last:
                self.cases.append(self._build_unchanged_case(first, last))
                self._index_cases()
                return len(self.cases) - 1, index - first + 1
        return None

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
            }
        )

    def _get_case_location(self, index: int) -> tuple[int, int] | None:
        """Find the active case and subtitle position for a source subtitle.

        Arguments:
            index: zero-based source subtitle index
        Returns:
            case index and one-based subtitle index, if an active case exists
        """
        for case_index, starts in self.locations.items():
            length = len(self.cases[case_index].query.subtitles)
            for start in starts:
                if start <= index < start + length:
                    return case_index, index - start + 1
        return None

    def _index_cases(self):
        """Match the latest answer for each query to its complete source blocks."""
        self.locations = {}
        latest = {case.query.key: index for index, case in enumerate(self.cases)}
        for case_index in latest.values():
            case = self.cases[case_index]
            query = tuple(subtitle.text for subtitle in case.query.subtitles)
            starts = self._block_starts.get(query)
            if starts:
                self.locations[case_index] = tuple(starts)

    def _set_case_verified(self, case_index: int, *, verified: bool):
        """Set verification and clear few-shot status when unverified.

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
