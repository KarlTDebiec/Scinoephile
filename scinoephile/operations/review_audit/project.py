#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Coordinate review jobs and saves for one subtitle project."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from threading import RLock

from scinoephile.common.validation import val_input_path, val_output_path
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms.utils import serialize_test_cases
from scinoephile.core.subtitles import Series
from scinoephile.lang.id import get_series_language
from scinoephile.lang.review.standard import DEFAULT_PROMPTS
from scinoephile.llms.review_audit import ReviewAuditManager, ReviewAuditTestCase

from .audit_cases import (
    apply_audit_case,
    build_audit_case,
    get_audit_query,
    load_audit_cases,
)
from .edits import build_review_edit, prepare_proofreading_edit
from .filters import AuditFilters
from .project_files import (
    backup_review_files,
    get_file_hashes,
    lock_review_files,
    parse_source_srt,
    render_review_files,
    validate_project_paths,
    write_files,
)
from .proofreading_decisions import ProofreadingDecisions
from .rows import AuditRow, AuditStatus, build_audit_rows
from .verification import get_verification_rows, get_verification_token

__all__ = ["ReviewAuditProject"]


class ReviewAuditProject:
    """Edit one subtitle language while preserving the original transcription."""

    def __init__(
        self,
        infile_path: Path,
        outfile_path: Path,
        *,
        json_path: Path | None = None,
        language: Language | None = None,
    ):
        """Open subtitles with native proofreading and audit test-case files.

        Arguments:
            infile_path: immutable original subtitles
            outfile_path: generated proofread subtitles
            json_path: proofreading JSON override, defaults to a sibling .review.json
            language: language override, otherwise detected from the input
        Raises:
            ScinoephileError: if files, paths, or review decisions are invalid
        """
        self._lock = RLock()
        self._auditing_running = False
        self._proofreading_running = False
        self._proofreading_source: Series | None = None
        self._proofreading_content: bytes | None = None
        self._proofreading_file_hashes: tuple[bytes | None, ...] | None = None
        try:
            self.infile_path = val_input_path(infile_path)
            self.outfile_path = val_output_path(
                outfile_path, exist_ok=True, create=False
            )
            if json_path is None:
                json_path = self.outfile_path.with_suffix(".review.json")
            self.json_path = val_output_path(json_path, exist_ok=True, create=False)
            self.audit_json_path = self.outfile_path.with_suffix(".audit.json")
            self._lock_path = self.audit_json_path.with_name(
                f".{self.audit_json_path.stem}.lock"
            )
            validate_project_paths(
                self.infile_path,
                self.outfile_path,
                self.audit_json_path,
                lock_path=self._lock_path,
                json_path=self.json_path,
            )
            with lock_review_files(self._lock_path):
                self._load_project(language)
        except (OSError, ValueError) as exc:
            raise ScinoephileError(f"Unable to open review editor: {exc}") from exc

    @property
    def auditing_running(self) -> bool:
        """Return whether an independent audit currently owns the review state."""
        with self._lock:
            return self._auditing_running

    @property
    def block_count(self) -> int:
        """Number of source context blocks, including previously audited blocks."""
        with self._lock:
            return len(self._block_ranges)

    @property
    def input_changed(self) -> bool:
        """Whether the configured OCR file differs from the last published baseline."""
        return self.infile_path.read_bytes() != self._source_content

    @property
    def job_running(self) -> bool:
        """Whether auditing or proofreading currently blocks row edits."""
        with self._lock:
            return self._auditing_running or self._proofreading_running

    @property
    def proofreading_running(self) -> bool:
        """Return whether an automated run currently owns output creation."""
        with self._lock:
            return self._proofreading_running

    def begin_auditing(
        self,
        *,
        rerun: bool = False,
        start_at_idx: int = 0,
        stop_at_idx: int | None = None,
    ) -> tuple[tuple[AuditRow, ...], ...]:
        """Reserve saved proofreading for an initial audit or whole-file re-audit.

        Arguments:
            rerun: audit blocks even if they already have saved findings
            start_at_idx: first source block to include, zero-based
            stop_at_idx: exclusive source block boundary, or None for the end
        Returns:
            complete context blocks containing at least one eligible subtitle
        Raises:
            ValueError: if output is absent, a worker is active, or no rows qualify
        """
        with self._lock, lock_review_files(self._lock_path):
            if self._auditing_running or self._proofreading_running:
                raise ValueError("Wait for the current operation to finish")
            if not self.outfile_path.exists():
                raise ValueError("Run proofreading before auditing")
            self._check_file_hashes()
            rows = self.rows()
            blocks = tuple(
                tuple(rows[first:last])
                for first, last in self._block_ranges[start_at_idx:stop_at_idx]
                if rerun
                or any(row.finding == AuditStatus.unaudited for row in rows[first:last])
            )
            if not blocks:
                raise ValueError("No unaudited subtitles remain")
            self._auditing_running = True
            return blocks

    def begin_proofreading(self, *, rerun: bool = False) -> Series:
        """Reload the configured OCR input and reserve an immutable run snapshot.

        Arguments:
            rerun: allow replacing existing output from current OCR
        Returns:
            freshly loaded source for the reserved worker
        Raises:
            ValueError: if another run, structural change, or external edit conflicts
        """
        with self._lock, lock_review_files(self._lock_path):
            if self._proofreading_running or self._auditing_running:
                raise ValueError("A proofreading or audit run is already running")
            if self.outfile_path.exists() and not rerun:
                raise ValueError("The proofreading output already exists")
            if rerun and not self.outfile_path.exists():
                raise ValueError("Run proofreading before re-proofreading")
            file_hashes = self._file_hashes()
            if file_hashes[1:] != self._saved_file_hashes[1:]:
                raise ValueError("Output or JSON changed outside this session")
            content = self.infile_path.read_bytes()
            source = parse_source_srt(content)
            if [(s.start, s.end) for s in source] != [
                (s.start, s.end) for s in self.original
            ]:
                raise ValueError("OCR reload must preserve subtitle counts and timings")
            if sha256(content).digest() != file_hashes[0]:
                raise ValueError("OCR input changed while it was being loaded")
            self._proofreading_source = source
            self._proofreading_content = content
            self._proofreading_file_hashes = file_hashes
            self._proofreading_running = True
            return source

    def end_auditing(self):
        """Release the audit reservation on completion or failure."""
        with self._lock:
            self._auditing_running = False

    def end_proofreading(self):
        """Release the reservation after worker completion or failure."""
        with self._lock:
            self._proofreading_running = False
            self._proofreading_source = None
            self._proofreading_content = None
            self._proofreading_file_hashes = None

    def publish_audit(
        self,
        block: tuple[AuditRow, ...],
        case: ReviewAuditTestCase,
        *,
        rerun: bool = False,
    ):
        """Save one complete audit test case and retain manual draft findings on resume.

        Arguments:
            block: reserved source rows supplying the queried context
            case: completed LLM test case for those rows
            rerun: replace previous findings for the block
        Raises:
            ValueError: if the case or reservation does not match the current block
            ScinoephileError: if the case cannot be persisted
        """
        with self._lock, lock_review_files(self._lock_path):
            if not self._auditing_running:
                raise ValueError("No audit run is active")
            self._check_file_hashes()
            first, last = self._block_ranges[block[0].block_number - 1]
            if (
                tuple(self._rows[first:last]) != block
                or case.query.key != get_audit_query(block).key
                or case.answer is None
                or case.draft
            ):
                raise ValueError("Audit case does not match the reserved block")

            previous = self._audit_cases.get(block[0].index)
            if previous is not None and previous.query.key != case.query.key:
                previous = None
            updated = apply_audit_case(list(block), case)
            if not rerun and previous is not None and previous.draft:
                updated = [
                    before if before.finding != AuditStatus.unaudited else after
                    for before, after in zip(block, updated, strict=True)
                ]
                case = build_audit_case(updated)
            elif (
                previous is not None
                and previous.verified
                and previous.answer == case.answer
            ):
                case = case.model_copy(
                    update={"verified": True, "few_shot": previous.few_shot}
                )
                updated = [replace(row, verified=True) for row in updated]

            rows = self._rows.copy()
            rows[first:last] = [
                replace(row, version=row.version + 1) for row in updated
            ]
            cases = self._audit_cases | {block[0].index: case}
            try:
                self._save_audit_cases(cases, rows)
            except OSError as exc:
                raise ScinoephileError(f"Unable to save audit findings: {exc}") from exc

    def publish_proofreading(self, decisions_path: Path, *, rerun: bool = False):
        """Publish validated proofreading and regenerate its subtitle output.

        Arguments:
            decisions_path: completed temporary native proofreading decisions
            rerun: back up and replace existing proofreading from current OCR
        Raises:
            ValueError: if the reservation is stale or revisions cannot be saved as SRT
            ScinoephileError: if publishing the output fails
        """
        with self._lock, lock_review_files(self._lock_path):
            if not self._proofreading_running:
                raise ValueError("No proofreading run is active")
            if (
                self.outfile_path.exists() and not rerun
            ) or self._file_hashes() != self._proofreading_file_hashes:
                raise ValueError(
                    "Project files changed during proofreading; restart the app. "
                    "Output was not replaced."
                )
            source = self._proofreading_source
            content = self._proofreading_content
            assert source is not None and content is not None
            decisions = ProofreadingDecisions(source, self.language, decisions_path)
            decisions.normalize_srt_revisions()
            rows, ranges = build_audit_rows(source, content, self.language, decisions)
            cases = {}
            for first, last in ranges:
                block = rows[first:last]
                case = self._audit_cases.get(block[0].index)
                if case is not None and case.query.key == get_audit_query(block).key:
                    cases[block[0].index] = case
                    rows[first:last] = apply_audit_case(block, case)
            rows = [
                replace(row, version=old.version + 1)
                for row, old in zip(rows, self._rows, strict=True)
            ]
            try:
                if rerun:
                    backup_review_files(
                        self.outfile_path, self.json_path, self.audit_json_path
                    )
                writes = render_review_files(
                    source,
                    rows,
                    self.outfile_path,
                    decisions=decisions,
                    json_path=self.json_path,
                )
                self._save_audit_cases(cases, rows, writes)
            except OSError as exc:
                raise ScinoephileError(
                    f"Unable to publish proofreading: {exc}"
                ) from exc
            self.original = source
            self._source_content = content
            self.decisions = decisions
            self._block_ranges = ranges

    def rows(self) -> list[AuditRow]:
        """Read the current project rows.

        Returns:
            snapshot of the subtitle rows and audit findings
        """
        with self._lock:
            return self._rows.copy()

    def save(
        self,
        key: str,
        *,
        reviewed: str,
        review_note: str,
        notes: str,
        finding: str,
        verified: bool,
        version: int,
        proofreading_verified: bool | None = None,
    ) -> set[str]:
        """Save proofreading and audit edits with independent case verification.

        Arguments:
            key: immutable source-row identity
            reviewed: complete corrected subtitle text
            review_note: native revision explanation
            notes: independent audit notes
            finding: independent audit verdict
            verified: whether the complete audit answer was checked
            version: rendered row version, rejecting stale forms
            proofreading_verified: optional approval of the proofreading answer
        Returns:
            source keys whose forms need updating
        Raises:
            KeyError: if the row is unknown
            ValueError: if an edit or verification is invalid or stale
            ScinoephileError: if saving files fails
        """
        with self._lock, lock_review_files(self._lock_path):
            current = next((row for row in self._rows if row.key == key), None)
            if current is None:
                raise KeyError(key)
            if self._proofreading_running or self._auditing_running:
                raise ValueError(
                    "Wait for proofreading or auditing to finish before editing"
                )
            if version != current.version:
                raise ValueError(
                    "This row changed in another tab. Reload before saving."
                )
            draft = build_review_edit(
                current,
                reviewed=reviewed,
                review_note=review_note,
                notes=notes,
                finding=finding,
                verified=verified,
            )
            self._check_file_hashes()
            rows, decisions, writes = self._prepare_save(
                current, draft, proofreading_verified
            )
            cases = self._update_edited_blocks(rows, current, draft)
            changed = set()
            for index, (old, row) in enumerate(zip(self._rows, rows, strict=True)):
                if old != row or row.key == key:
                    changed.add(row.key)
                    rows[index] = replace(row, version=old.version + 1)
            try:
                self._save_audit_cases(cases, rows, writes)
            except OSError as exc:
                raise ScinoephileError(f"Unable to save review edits: {exc}") from exc
            self.decisions = decisions
            return changed

    def verify_matching_rows(self, filters: AuditFilters, token: str) -> int:
        """Verify complete audit blocks whose rows all match the current filters.

        Arguments:
            filters: filters applied to the full project
            token: digest of the selected row identities and versions
        Returns:
            number of newly verified blocks
        Raises:
            ValueError: if output is absent, work is active, or the selection changed
            ScinoephileError: if verification cannot be persisted
        """
        with self._lock, lock_review_files(self._lock_path):
            if not self.outfile_path.exists():
                raise ValueError("Run proofreading before verifying subtitles")
            if self._proofreading_running or self._auditing_running:
                raise ValueError("Wait for proofreading or auditing to finish")
            self._check_file_hashes()
            matching = get_verification_rows(self._rows, filters)
            if token != get_verification_token(matching):
                raise ValueError(
                    "The matching blocks changed. Reload before verifying."
                )
            if not matching:
                return 0

            rows = self._rows.copy()
            cases = self._audit_cases.copy()
            blocks = {row.block_number for row in matching}
            for number in blocks:
                first, last = self._block_ranges[number - 1]
                rows[first:last] = [
                    replace(row, verified=True, version=row.version + 1)
                    for row in rows[first:last]
                ]
                cases[first + 1] = build_audit_case(rows[first:last])
            try:
                self._save_audit_cases(cases, rows)
            except OSError as exc:
                raise ScinoephileError(f"Unable to save verification: {exc}") from exc
            return len(blocks)

    def _check_file_hashes(self):
        """Reject changes made outside the active editor's write transaction.

        Raises:
            ValueError: if project files changed externally
        """
        if self.input_changed:
            raise ValueError(
                "OCR input changed. Re-proofread before editing or auditing."
            )
        if self._file_hashes() != self._saved_file_hashes:
            raise ValueError(
                "A subtitle or JSON file changed outside this session. "
                "Restart before saving."
            )

    def _file_hashes(self) -> tuple[bytes | None, ...]:
        """Hash the project's source and writable files.

        Returns:
            hashes for the input, output, proofreading JSON, and audit JSON
        """
        return get_file_hashes(
            self.infile_path, self.outfile_path, self.json_path, self.audit_json_path
        )

    def _load_project(self, language: Language | None):
        """Open both native case files and project them onto the original SRT.

        Arguments:
            language: explicit language, or None to detect it from the original SRT
        Raises:
            ValueError: if the language or saved case files are invalid
        """
        self._source_content = self.infile_path.read_bytes()
        self.original = parse_source_srt(self._source_content)
        cases, saved_language = load_audit_cases(self.audit_json_path)
        if (
            language is not None
            and saved_language is not None
            and language != saved_language
        ):
            raise ValueError(f"Audit cases use language {saved_language.code}")
        resolved = language or saved_language or get_series_language(self.original)
        if resolved is None or resolved not in DEFAULT_PROMPTS:
            raise ValueError("Specify a supported proofreading language")
        self.language = resolved

        self.decisions = ProofreadingDecisions(
            self.original, self.language, self.json_path
        )
        self.decisions.normalize_srt_revisions()
        rows, self._block_ranges = build_audit_rows(
            self.original, self._source_content, self.language, self.decisions
        )
        for first, last in self._block_ranges:
            rows[first:last] = apply_audit_case(rows[first:last], cases.get(first + 1))

        writes = {}
        if not self.audit_json_path.exists():
            writes[self.audit_json_path] = "[]\n"
        if not self.json_path.exists():
            writes[self.json_path] = "[]\n"
        has_decisions = any(case.answer is not None for case in self.decisions.cases)
        if self.outfile_path.exists():
            output = Series.load(self.outfile_path)
            if [(s.start, s.end) for s in output] != [
                (row.start, row.end) for row in rows
            ]:
                raise ValueError("Original and output subtitle timings must match")
            if [s.text_with_newline for s in output] != [row.reviewed for row in rows]:
                raise ValueError("Output subtitles disagree with the proofreading JSON")
        elif has_decisions:
            generated = render_review_files(
                self.original,
                rows,
                self.outfile_path,
                decisions=self.decisions,
                json_path=self.json_path,
            )
            writes[self.outfile_path] = generated[self.outfile_path]
        write_files(writes)
        self._rows = rows
        self._audit_cases = cases
        self._saved_file_hashes = self._file_hashes()

    def _prepare_save(
        self, current: AuditRow, draft: AuditRow, proofreading_verified: bool | None
    ) -> tuple[list[AuditRow], ProofreadingDecisions, dict[Path, str]]:
        """Prepare proofreading changes and the files they affect.

        Arguments:
            current: saved subtitle row
            draft: validated edit from the editor
            proofreading_verified: optional approval of the proofreading answer
        Returns:
            candidate rows, decisions, and file writes
        """
        text_changed = (draft.reviewed, draft.review_note) != (
            current.reviewed,
            current.review_note,
        )
        verification_changed = (
            proofreading_verified is not None
            and proofreading_verified != current.proofreading_verified
        )
        rows = self._rows.copy()
        decisions = self.decisions
        writes = {}
        if text_changed:
            rows, decisions = prepare_proofreading_edit(rows, draft, decisions)
        if verification_changed:
            assert proofreading_verified is not None
            if not text_changed:
                decisions = deepcopy(decisions)
            decisions.verify(current.index - 1, verified=proofreading_verified)
        if text_changed or verification_changed:
            verified_indexes = decisions.verified_indexes()
            rows = [
                replace(row, proofreading_verified=index in verified_indexes)
                for index, row in enumerate(rows)
            ]
            if text_changed:
                writes = render_review_files(
                    self.original,
                    rows,
                    self.outfile_path,
                    decisions=decisions,
                    json_path=self.json_path,
                )
            else:
                writes[self.json_path] = decisions.serialize()
        return rows, decisions, writes

    def _save_audit_cases(
        self,
        cases: dict[int, ReviewAuditTestCase],
        rows: list[AuditRow],
        writes: dict[Path, str] | None = None,
    ):
        """Commit candidate cases and any generated proofreading files.

        Arguments:
            cases: current audit cases keyed by first subtitle index
            rows: candidate editor snapshot
            writes: other candidate project files to commit together
        """
        if writes is None:
            writes = {}
        if cases != self._audit_cases:
            writes[self.audit_json_path] = (
                serialize_test_cases(
                    (cases[index] for index in sorted(cases)), ReviewAuditManager
                )
                + "\n"
            )
        write_files(writes)
        self._rows = rows
        self._audit_cases = cases
        self._saved_file_hashes = self._file_hashes()

    def _update_edited_blocks(
        self, rows: list[AuditRow], current: AuditRow, draft: AuditRow
    ) -> dict[int, ReviewAuditTestCase]:
        """Apply an audit edit and discard findings whose query changed.

        Arguments:
            rows: candidate rows, updated in place with their audit findings
            current: saved row before the edit
            draft: validated edit from the editor
        Returns:
            candidate audit cases
        Raises:
            ValueError: if verification was requested for an incomplete answer
        """
        cases = self._audit_cases.copy()
        changed_blocks = {
            row.block_number
            for old, row in zip(self._rows, rows, strict=True)
            if (old.reviewed, old.review_note) != (row.reviewed, row.review_note)
        }
        for number in changed_blocks:
            first, last = self._block_ranges[number - 1]
            rows[first:last] = apply_audit_case(rows[first:last], None)
            cases.pop(first + 1, None)

        first, last = self._block_ranges[current.block_number - 1]
        block_changed = current.block_number in changed_blocks
        audit_changed = (draft.finding, draft.notes) != (current.finding, current.notes)
        if block_changed and not audit_changed:
            return cases
        if (
            not block_changed
            and not audit_changed
            and draft.verified == current.verified
        ):
            return cases

        index = current.index - 1
        rows[index] = replace(
            rows[index], finding=draft.finding, notes=draft.notes.strip()
        )
        verify = draft.verified and (not block_changed or not current.verified)
        if verify and any(
            row.finding == AuditStatus.unaudited for row in rows[first:last]
        ):
            if not current.verified:
                raise ValueError("Complete the audit block before verifying it")
            verify = False
        rows[first:last] = [replace(row, verified=verify) for row in rows[first:last]]
        case = build_audit_case(rows[first:last])
        if case.answer is None:
            cases.pop(first + 1, None)
        else:
            cases[first + 1] = case
        return cases
