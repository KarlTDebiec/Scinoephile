#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Editable proofreading sessions with native decision JSON and subtitle output."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from threading import RLock

from scinoephile.common.validation import val_input_path, val_output_path
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.lang.id import get_series_language
from scinoephile.lang.review.standard import DEFAULT_PROMPTS

from .decisions import ReviewDecisions
from .files import (
    backup_review_files,
    get_file_hashes,
    parse_source_srt,
    render_review_files,
    validate_project_paths,
    write_files,
)
from .models import AuditFilters, AuditPage, AuditRow, AuditStatus
from .pagination import get_audit_page, get_verification_token
from .rows import build_audit_rows
from .store import AuditProgress

__all__ = ["AuditSession"]


class AuditSession:
    """Edit one subtitle language while preserving the original transcription."""

    page_size = 5
    """Number of complete matching blocks per incremental batch."""

    def __init__(
        self,
        infile_path: Path,
        outfile_path: Path,
        *,
        json_path: Path | None = None,
        title: str | None = None,
        language: Language | None = None,
        report_path: Path | None = None,
    ):
        """Open subtitles and optionally resume native proofreading decisions.

        Arguments:
            infile_path: immutable original subtitles
            outfile_path: edited subtitles, loaded if already present
            json_path: optional native review JSON to read and update or create
            title: display title, defaulting to the input filename stem
            language: language override, otherwise detected from the input
            report_path: optional old Markdown report used only to seed audit notes
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
            self.json_path = None
            if json_path is not None:
                self.json_path = val_output_path(json_path, exist_ok=True, create=False)
            if report_path is not None:
                report_path = val_input_path(report_path)
            self.state_path = self.outfile_path.with_suffix(".audit.json")
            self.title = title or self.infile_path.stem
            validate_project_paths(
                self.infile_path,
                self.outfile_path,
                self.state_path,
                json_path=self.json_path,
                report_path=report_path,
            )
            content = self.infile_path.read_bytes()
            write_progress = not self.state_path.exists()
            if not write_progress:
                self._progress = AuditProgress.model_validate_json(
                    self.state_path.read_bytes()
                )
            else:
                if self.outfile_path.with_suffix(".review.sqlite3").exists():
                    raise ValueError(
                        "Migrate the existing audit database to JSON first"
                    )
                self._progress = AuditProgress(
                    source=content.decode("utf-8").splitlines(keepends=True)
                )
            self._source_content = "".join(self._progress.source).encode("utf-8")
            if not self.outfile_path.exists() and self._source_content != content:
                self._source_content = content
                self._progress = AuditProgress(
                    source=content.decode("utf-8").splitlines(keepends=True)
                )
                write_progress = True
            self.original = parse_source_srt(self._source_content)
            detected = language or get_series_language(self.original)
            if detected is None or detected not in DEFAULT_PROMPTS:
                raise ValueError("Specify a supported proofreading language")
            self.language = detected
            self.decisions = None
            if self.json_path is not None:
                self.decisions = ReviewDecisions(
                    self.original, self.language, self.json_path
                )
            self._rows, self._block_ranges = build_audit_rows(
                self.original,
                self._source_content,
                self.language,
                self.decisions,
                outfile_path=self.outfile_path,
                report_path=report_path,
            )
            self._rows_by_key = {row.key: row for row in self._rows}
            if write_progress:
                self._write_progress(self._progress)
            else:
                self._saved_file_hashes = self._file_hashes()
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
    def proofreading_running(self) -> bool:
        """Return whether an automated run currently owns output creation."""
        with self._lock:
            return self._proofreading_running

    @property
    def proofreading_settings(self) -> dict[str, str]:
        """Last successful proofreading settings and authored-decision provenance."""
        with self._lock:
            return self._progress.proofreading.copy()

    def begin_auditing(
        self,
        *,
        rerun: bool = False,
        start_at_idx: int = 0,
        stop_at_idx: int | None = None,
    ) -> tuple[tuple[AuditRow, ...], ...]:
        """Reserve saved proofreading for an initial audit or whole-file re-audit.

        Arguments:
            rerun: replace existing findings for all subtitles, retaining verification
            start_at_idx: first source block to include, zero-based
            stop_at_idx: exclusive source block boundary, or None for the end
        Returns:
            complete context blocks containing at least one eligible subtitle
        Raises:
            ValueError: if output is absent, a worker is active, or no rows qualify
        """
        with self._lock:
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
                or any(
                    not row.verified and row.finding == AuditStatus.unaudited
                    for row in rows[first:last]
                )
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
        with self._lock:
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

    def page(
        self, filters: AuditFilters, *, after: int = 0, through: int | None = None
    ) -> AuditPage:
        """Select a block batch or the complete prefix already loaded by the browser.

        Arguments:
            filters: requested filters
            after: stable source block cursor before a new batch
            through: inclusive loaded cursor when acknowledging edits
        Returns:
            loaded blocks and complete filtered progress counts
        """
        filters.validate()
        with self._lock:
            rows = self.rows()
            block_ranges = self._block_ranges
        return get_audit_page(
            rows,
            block_ranges,
            filters,
            page_size=self.page_size,
            after=after,
            through=through,
        )

    def publish_audit(
        self,
        block: tuple[AuditRow, ...],
        findings: dict[int, tuple[str, str]],
        *,
        rerun: bool = False,
    ):
        """Persist one complete audit block without changing proofreading files.

        Arguments:
            block: reserved source rows supplying the queried context
            findings: one status and note for each one-based subtitle index
            rerun: replace all findings while retaining human verification marks
        Raises:
            ValueError: if reservation, files or source row versions changed
            ScinoephileError: if audit progress cannot be persisted
        """
        with self._lock:
            if not self._auditing_running:
                raise ValueError("No audit run is active")
            self._check_file_hashes()
            if set(findings) != {row.index for row in block}:
                raise ValueError("Audit findings must cover the complete block")
            current = {row.key: row for row in self.rows()}
            updated = []
            for row in block:
                if not rerun and (row.verified or row.finding != AuditStatus.unaudited):
                    continue
                if current[row.key] != row:
                    raise ValueError("Subtitle changed during auditing")
                status, note = findings[row.index]
                if status not in {AuditStatus.ok, AuditStatus.review}:
                    raise ValueError("Invalid automated audit verdict")
                if (status == AuditStatus.review) != bool(note.strip()):
                    raise ValueError("Only Review verdicts require audit notes")
                updated.append(
                    replace(
                        row,
                        notes=note.strip(),
                        finding=AuditStatus(status),
                        version=row.version + 1,
                    )
                )
            try:
                self._write_progress(self._progress.with_rows(updated))
            except OSError as exc:
                raise ScinoephileError(f"Unable to save audit findings: {exc}") from exc

    def publish_proofreading(
        self,
        decisions_path: Path,
        *,
        rerun: bool = False,
        settings: dict[str, str] | None = None,
    ):
        """Publish validated decisions and subtitles as one recoverable operation.

        Arguments:
            decisions_path: completed temporary native proofreading decisions
            rerun: back up and replace existing proofreading from current OCR
            settings: effective run settings and decision-reuse provenance
        Raises:
            ValueError: if the run lost its reservation, files changed, or the
                new output cannot be saved as SRT
            ScinoephileError: if publishing files or progress fails
        """
        with self._lock:
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
            decisions = ReviewDecisions(source, self.language, decisions_path)
            decisions.normalize_srt_revisions()
            updated, ranges = build_audit_rows(
                source, content, self.language, decisions
            )
            previous = self.rows()
            for index, (row, replacement) in enumerate(
                zip(previous, updated, strict=True)
            ):
                current = replace(replacement, version=row.version + 1)
                if (
                    current.original == row.original
                    and current.reviewed == row.reviewed
                    and current.review_note == row.review_note
                ):
                    current = replace(
                        current,
                        finding=row.finding,
                        notes=row.notes,
                        verified=row.verified,
                    )
                updated[index] = current
            progress = AuditProgress(
                source=content.decode("utf-8").splitlines(keepends=True),
                proofreading=self._progress.proofreading
                if settings is None
                else settings,
            ).with_rows(updated)
            try:
                if rerun:
                    backup_review_files(
                        self.outfile_path, self.json_path, self.state_path
                    )
                writes = render_review_files(
                    source,
                    updated,
                    self.outfile_path,
                    decisions=decisions,
                    json_path=self.json_path,
                )
                self._write_progress(progress, writes)
            except OSError as exc:
                raise ScinoephileError(
                    f"Unable to publish proofreading: {exc}"
                ) from exc
            self.original = source
            self._source_content = content
            self.decisions = decisions
            self._block_ranges = ranges
            self._rows = updated
            self._rows_by_key = {row.key: row for row in updated}

    def rows(self) -> list[AuditRow]:
        """Read current text and independent progress without stale form caching.

        Returns:
            current editable rows and their audit progress
        """
        with self._lock:
            return self._progress.apply(
                self._rows,
                match_review_note=self.decisions is not None
                and bool(self.decisions.cases),
            )

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
    ) -> set[str]:
        """Save proofreading and audit progress with stale-write checks.

        Arguments:
            key: immutable source-row identity
            reviewed: complete corrected subtitle text
            review_note: native revision explanation
            notes: independent audit notes
            finding: independent audit verdict
            verified: whether this audit finding was checked
            version: rendered row version, rejecting stale forms
        Returns:
            source keys whose forms need updating
        Raises:
            KeyError: if the row is unknown
            ValueError: if text, verdict, or a stale save is invalid
            ScinoephileError: if saving files fails
        """
        original = self._rows_by_key[key].original
        reviewed = reviewed.replace("\r\n", "\n").replace("\r", "\n")
        if not reviewed.strip() or len(reviewed) > 1000 or "\n\n" in reviewed:
            raise ValueError(
                "Subtitle text must contain 1–1000 characters and no blank lines"
            )
        if reviewed != original and not review_note.strip():
            raise ValueError("A note is required for changed proofreading text")
        if len(review_note) > 1000:
            raise ValueError("Revision notes must not exceed 1000 characters")
        try:
            finding = AuditStatus(finding)
        except ValueError as exc:
            raise ValueError("Unknown audit verdict") from exc
        _validate_audit_notes(finding, notes)
        with self._lock:
            if self._proofreading_running or self._auditing_running:
                raise ValueError(
                    "Wait for proofreading or auditing to finish before editing"
                )
            try:
                rows = self.rows()
                current = next(row for row in rows if row.key == key)
                if version != current.version:
                    raise ValueError(
                        "This row changed in another tab. Reload before saving."
                    )
                self._check_file_hashes()
                proofreading_changed = (
                    not self.outfile_path.exists()
                    or reviewed != current.reviewed
                    or review_note != current.review_note
                )
                if proofreading_changed:
                    updated, decisions = self._prepare_edit(
                        rows, current, reviewed, review_note
                    )
                else:
                    updated, decisions = rows, self.decisions
                affected = {
                    row.key: replace(
                        row, verified=False, finding=AuditStatus.unaudited, notes=""
                    )
                    for row in updated
                    if row != rows[row.index - 1]
                }
                # Keep the reset unless the form also changed its audit decision
                if key not in affected or (notes, finding, verified) != (
                    current.notes,
                    current.finding,
                    current.verified,
                ):
                    affected[key] = replace(
                        updated[current.index - 1],
                        notes=notes,
                        finding=finding,
                        verified=verified
                        and (key not in affected or not current.verified),
                    )
                progress = self._progress.with_rows(
                    replace(row, version=row.version + 1) for row in affected.values()
                )
                writes = {}
                if proofreading_changed:
                    writes = render_review_files(
                        self.original,
                        updated,
                        self.outfile_path,
                        decisions=decisions,
                        json_path=self.json_path,
                    )
                self._write_progress(progress, writes)
            except OSError as exc:
                raise ScinoephileError(f"Unable to save review edits: {exc}") from exc
            self.decisions = decisions
            self._rows = updated
            self._rows_by_key = {row.key: row for row in updated}
            return set(affected)

    def verify_visible(self, filters: AuditFilters, token: str) -> int:
        """Verify every matching subtitle atomically without changing its text.

        Arguments:
            filters: current browser filters, independent of the loaded cursor
            token: selection digest rendered with the operations form
        Returns:
            number of newly verified subtitles
        Raises:
            ValueError: if output is absent, work is active, or the selection changed
            ScinoephileError: if verification cannot be persisted
        """
        with self._lock:
            if not self.outfile_path.exists():
                raise ValueError("Run proofreading before verifying subtitles")
            if self._proofreading_running or self._auditing_running:
                raise ValueError("Wait for proofreading or auditing to finish")
            self._check_file_hashes()
            try:
                filters.validate()
                matching = [row for row in self.rows() if filters.matches(row)]
                if token != get_verification_token(matching):
                    raise ValueError(
                        "The matching subtitles changed. Reload before verifying."
                    )
                rows = [row for row in matching if not row.verified]
                for row in rows:
                    _validate_audit_notes(row.finding, row.notes)
                if rows:
                    progress = self._progress.with_rows(
                        replace(row, verified=True, version=row.version + 1)
                        for row in rows
                    )
                    self._write_progress(progress)
            except OSError as exc:
                raise ScinoephileError(f"Unable to verify subtitles: {exc}") from exc
            return len(rows)

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
            self.infile_path, self.outfile_path, self.json_path, self.state_path
        )

    def _prepare_edit(
        self, rows: list[AuditRow], current: AuditRow, text: str, note: str
    ) -> tuple[list[AuditRow], ReviewDecisions | None]:
        """Build validated candidate text and native decisions before writing.

        Arguments:
            rows: current text and audit progress
            current: row being saved
            text: new complete subtitle text
            note: new revision explanation
        Returns:
            candidate rows and optional native decision log
        Raises:
            ValueError: if starting a decision log would change existing subtitles
        """
        decisions = self.decisions
        if decisions is None:
            updated = list(rows)
            updated[current.index - 1] = replace(
                current, reviewed=text, review_note=note
            )
            return updated, None
        decisions = deepcopy(decisions)
        # Seed any existing output edits when starting a new JSON log
        if not decisions.cases:
            for row in rows:
                if row.changed:
                    decisions.edit(row.index - 1, row.reviewed, row.review_note)
            seeded_texts, _ = decisions.render()
            if seeded_texts != [row.reviewed for row in rows]:
                raise ValueError(
                    "Existing corrections differ across linked subtitles. "
                    "Open the editor without --json to keep those corrections."
                )
        decisions.edit(current.index - 1, text, note)
        texts, revision_notes = decisions.render()
        return [
            replace(
                row,
                reviewed=texts[row.index - 1],
                review_note=revision_notes[row.index - 1],
                shared_indexes=decisions.shared_indexes(row.index - 1),
            )
            for row in rows
        ], decisions

    def _write_progress(
        self, progress: AuditProgress, writes: dict[Path, str] | None = None
    ):
        """Commit audit JSON alongside any changed proofreading files.

        Arguments:
            progress: candidate audit state
            writes: candidate proofread SRT and native decisions, when changed
        """
        write_files(
            {
                **(writes or {}),
                self.state_path: progress.model_dump_json(indent=2) + "\n",
            }
        )
        self._progress = progress
        self._saved_file_hashes = self._file_hashes()


def _validate_audit_notes(finding: str, notes: str):
    """Require Review explanations and empty notes for OK verdicts.

    Arguments:
        finding: normalized audit verdict
        notes: human or automated audit explanation
    Raises:
        ValueError: if Review lacks an explanation or OK has audit notes
    """
    if finding == AuditStatus.review and not notes.strip():
        raise ValueError("Audit notes are required when audit status is Review")
    if finding == AuditStatus.ok and notes:
        raise ValueError("Clear audit notes when audit status is OK")
