#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Coordinate review jobs and saves for one subtitle project."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from threading import RLock

from scinoephile.common.validation import val_input_path, val_output_path
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.lang.id import get_series_language
from scinoephile.lang.review.standard import DEFAULT_PROMPTS

from .decisions import ReviewDecisions
from .edits import build_review_edit, prepare_review_edit
from .files import (
    backup_review_files,
    get_file_hashes,
    lock_review_files,
    parse_source_srt,
    render_review_files,
    validate_project_paths,
    write_files,
)
from .models import AuditFilters, AuditPage, AuditRow, AuditStatus
from .pagination import get_audit_page
from .rows import apply_audit_findings, build_audit_rows, carry_audit_progress
from .store import AuditProgress
from .verification import prepare_bulk_verification

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
            self._lock_path = self.state_path.with_name(f".{self.state_path.stem}.lock")
            self.title = title or self.infile_path.stem
            validate_project_paths(
                self.infile_path,
                self.outfile_path,
                self.state_path,
                lock_path=self._lock_path,
                json_path=self.json_path,
                report_path=report_path,
            )
            with lock_review_files(self._lock_path):
                self._load_project(language, report_path)
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
        with self._lock, lock_review_files(self._lock_path):
            if not self._auditing_running:
                raise ValueError("No audit run is active")
            self._check_file_hashes()
            updated = apply_audit_findings(self.rows(), block, findings, rerun=rerun)
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
            decisions = ReviewDecisions(source, self.language, decisions_path)
            decisions.normalize_srt_revisions()
            updated, ranges = build_audit_rows(
                source, content, self.language, decisions
            )
            updated = carry_audit_progress(self.rows(), updated)
            progress = AuditProgress(
                language=self.language,
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
        with self._lock, lock_review_files(self._lock_path):
            rows = self.rows()
            current = next((row for row in rows if row.key == key), None)
            if current is None:
                raise KeyError(key)
            draft = build_review_edit(
                current,
                reviewed=reviewed,
                review_note=review_note,
                notes=notes,
                finding=finding,
                verified=verified,
            )
            if self._proofreading_running or self._auditing_running:
                raise ValueError(
                    "Wait for proofreading or auditing to finish before editing"
                )
            if version != current.version:
                raise ValueError(
                    "This row changed in another tab. Reload before saving."
                )
            try:
                self._check_file_hashes()
                proofreading_changed = (
                    not self.outfile_path.exists()
                    or draft.reviewed != current.reviewed
                    or draft.review_note != current.review_note
                )
                updated, decisions, affected = prepare_review_edit(
                    rows,
                    draft,
                    self.decisions,
                    proofreading_changed=proofreading_changed,
                )
                progress = self._progress.with_rows(affected)
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
            return {row.key for row in affected}

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
        with self._lock, lock_review_files(self._lock_path):
            if not self.outfile_path.exists():
                raise ValueError("Run proofreading before verifying subtitles")
            if self._proofreading_running or self._auditing_running:
                raise ValueError("Wait for proofreading or auditing to finish")
            self._check_file_hashes()
            try:
                rows = prepare_bulk_verification(self.rows(), filters, token)
                if rows:
                    self._write_progress(self._progress.with_rows(rows))
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

    def _load_project(self, language: Language | None, report_path: Path | None):
        """Load the project baseline and bind its saved findings to one language.

        Arguments:
            language: explicit language, or None to use the saved or detected language
            report_path: optional old Markdown report used to seed audit notes
        Raises:
            ValueError: if the baseline or language is incompatible with the project
        """
        content = self.infile_path.read_bytes()
        write_progress = not self.state_path.exists()
        if write_progress:
            if self.outfile_path.with_suffix(".review.sqlite3").exists():
                raise ValueError("Migrate the existing audit database to JSON first")
            progress = AuditProgress(
                source=content.decode("utf-8").splitlines(keepends=True)
            )
        else:
            progress = AuditProgress.model_validate_json(self.state_path.read_bytes())
        self._source_content = "".join(progress.source).encode("utf-8")
        if not self.outfile_path.exists() and self._source_content != content:
            self._source_content = content
            progress = AuditProgress(
                language=progress.language,
                source=content.decode("utf-8").splitlines(keepends=True),
            )
            write_progress = True
        self.original = parse_source_srt(self._source_content)
        resolved = language or progress.language or get_series_language(self.original)
        if resolved is None or resolved not in DEFAULT_PROMPTS:
            raise ValueError("Specify a supported proofreading language")
        if progress.language is not None and progress.language != resolved:
            raise ValueError(
                f"Audit progress uses language {progress.language.code}. "
                f"Open it with --language {progress.language.code}."
            )
        self.language = resolved
        if progress.language is None:
            progress = progress.model_copy(update={"language": resolved})
            write_progress = True
        self._progress = progress
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
        if write_progress:
            self._write_progress(progress)
        else:
            self._saved_file_hashes = self._file_hashes()

    def _write_progress(
        self, progress: AuditProgress, writes: dict[Path, str] | None = None
    ):
        """Commit audit JSON and any proofreading files under the project lock.

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
