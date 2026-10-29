#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Load and edit native proofreading decisions while preserving query history."""

from __future__ import annotations

import json
from pathlib import Path

from scinoephile.core import Language
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.core.subtitles import Series
from scinoephile.lang.review.standard import DEFAULT_PROMPTS
from scinoephile.llms.review import ReviewManager, ReviewTestCase

__all__ = ["ReviewDecisions"]


class ReviewDecisions:
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
        base_cls = ReviewManager.get_test_case_cls(ReviewManager.base_prompt)
        data = [
            base_cls.model_validate(case.model_dump(mode="json")).model_dump(
                mode="json", by_alias=True, exclude_defaults=True
            )
            for case in self.cases
        ]
        return json.dumps(data, ensure_ascii=False, indent=2) + "\n"

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
