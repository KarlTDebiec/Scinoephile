#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Load and edit native proofreading decisions while preserving query history."""

from __future__ import annotations

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
        if not any(
            start <= index < start + len(self.cases[case_index].query.subtitles)
            for case_index, starts in self.locations.items()
            for start in starts
        ):
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
        covered = any(
            start <= index < start + len(self.cases[case_index].query.subtitles)
            for case_index, starts in self.locations.items()
            for start in starts
        )
        if not covered:
            first = 0
            for block in self.original.blocks:
                if first <= index < first + len(block):
                    query = tuple(s.text_with_newline for s in block)
                    affected.update(
                        start + index - first
                        for start in range(len(self.texts) - len(query) + 1)
                        if self.texts[start : start + len(query)] == query
                    )
                    break
                first += len(block)
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
            data = self.cases[case_index].model_dump(mode="json")
            data["verified"] = verified
            if verified and data["answer"] is None:
                data["answer"] = {"revisions": []}
            if not verified:
                data["few_shot"] = False
            self.cases[case_index] = self.case_cls.model_validate(data)

    def _add_case(self, index: int):
        """Create a native query for the source pause block containing a row.

        Arguments:
            index: zero-based source subtitle index
        """
        first = 0
        for block in self.original.blocks:
            if first <= index < first + len(block):
                self.cases.append(
                    self.case_cls.model_validate(
                        {
                            "query": {
                                "subtitles": [
                                    {
                                        "index": offset,
                                        "text": subtitle.text_with_newline,
                                    }
                                    for offset, subtitle in enumerate(block, 1)
                                ]
                            },
                            "answer": {"revisions": []},
                        }
                    )
                )
                self._index_cases()
                return
            first += len(block)

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
        """Match only the latest decision for each immutable query key."""
        self.locations = {}
        latest = {case.query.key: index for index, case in enumerate(self.cases)}
        for case_index in latest.values():
            query = tuple(s.text for s in self.cases[case_index].query.subtitles)
            starts = tuple(
                start
                for start in range(len(self.texts) - len(query) + 1)
                if self.texts[start : start + len(query)] == query
            )
            if starts:
                self.locations[case_index] = starts
