#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Editable proofreading sessions with native decision JSON and subtitle output."""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import closing
from copy import deepcopy
from dataclasses import dataclass, replace
from enum import StrEnum
from hashlib import sha256
from html import unescape
from os import fsync
from pathlib import Path
from shutil import copy2
from tempfile import NamedTemporaryFile, mkdtemp
from threading import RLock

from scinoephile.analysis.alignment import pairwise
from scinoephile.common.file import open_atomic_text_file
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.lang.id import get_series_language
from scinoephile.lang.review.standard import DEFAULT_PROMPTS

from .decisions import ReviewDecisions

__all__ = [
    "AuditBlock",
    "AuditFilters",
    "AuditPage",
    "AuditRow",
    "AuditSession",
    "AuditStatus",
]


class AuditStatus(StrEnum):
    """Explicit verdict for an independent proofreading audit."""

    unaudited = "unaudited"
    """No audit verdict has been recorded."""
    review = "review"
    """The subtitle needs human review."""
    ok = "ok"
    """The audit found no issue."""


_LEGACY_STATUSES = {
    "unassessed": AuditStatus.unaudited,
    "incorrect": AuditStatus.review,
    "check": AuditStatus.review,
    "flagged": AuditStatus.review,
}


@dataclass(frozen=True)
class AuditFilters:
    """Bookmarkable audit filters."""

    verification: str = "all"
    """all, verified, or unverified audit progress."""
    changes: str = "all"
    """all, changed, or unchanged subtitle text."""
    finding: str = "all"
    """all, unaudited, review, or ok audit statuses."""
    q: str = ""
    """Unicode text search or an exact block selector such as block 160."""

    def __post_init__(self):
        """Normalize bookmarks using the previous audit categories."""
        object.__setattr__(
            self, "finding", _LEGACY_STATUSES.get(self.finding, self.finding)
        )

    def counts(self, rows: list[AuditRow]) -> dict[str, dict[str, int]]:
        """Count each option with search and the other status filters applied.

        Arguments:
            rows: complete current subtitle snapshot, before pagination
        Returns:
            option counts keyed by filter name and option value
        """
        self.validate()
        counts: dict[str, dict[str, int]] = {}
        for name in ("changes", "finding", "verification"):
            other_filters = replace(self, **{name: "all"})
            matching = [row for row in rows if other_filters.matches(row)]
            if name == "changes":
                changed = sum(row.changed for row in matching)
                options = {"changed": changed, "unchanged": len(matching) - changed}
            elif name == "verification":
                verified = sum(row.verified for row in matching)
                options = {"verified": verified, "unverified": len(matching) - verified}
            else:
                options = {
                    status: sum(row.finding == status for row in matching)
                    for status in AuditStatus
                }
            counts[name] = {"all": len(matching), **options}
        return counts

    def matches(self, row: AuditRow) -> bool:
        """Check whether one row matches these filters.

        Arguments:
            row: current audit row
        Returns:
            whether the row matches
        """
        if not {
            "all": True,
            "verified": row.verified,
            "unverified": not row.verified,
        }.get(self.verification, False):
            return False
        if not {"all": True, "changed": row.changed, "unchanged": not row.changed}.get(
            self.changes, False
        ):
            return False
        if self.finding not in {"all", row.finding}:
            return False
        block = re.fullmatch(r"block\s*[:#]?\s*(\d+)", self.q.strip(), re.IGNORECASE)
        if block is not None:
            return row.block_number == int(block[1])
        searchable = (
            f"{row.index} {row.original} {row.reviewed} {row.notes} {row.review_note}"
        )
        return self.q.casefold() in searchable.casefold()

    def validate(self):
        """Reject unsupported filter values.

        Raises:
            ValueError: if a filter is unsupported
        """
        for value, choices in (
            (self.verification, {"all", "verified", "unverified"}),
            (self.changes, {"all", "changed", "unchanged"}),
            (self.finding, {"all", *AuditStatus}),
        ):
            if value not in choices:
                raise ValueError(f"Unknown audit filter: {value}")


@dataclass(frozen=True)
class AuditRow:
    """A subtitle pair, provenance, and its independent human audit state."""

    key: str
    """Content identity; changed inputs get fresh audit progress."""
    track_id: str
    """Track identifier."""
    label: str
    """Track display label."""
    language: str
    """Subtitle language tag."""
    index: int
    """One-based subtitle number."""
    start: int
    """Start time in milliseconds."""
    end: int
    """End time in milliseconds."""
    original: str
    """Validated source text."""
    reviewed: str
    """Proposed proofread text."""
    review_note: str
    """Read-only model explanation."""
    notes: str
    """Independent audit notes."""
    finding: AuditStatus = AuditStatus.unaudited
    """Independent audit verdict."""
    verified: bool = False
    """Human audit progress, independent of proofreading JSON verification."""
    version: int = 0
    """Optimistic concurrency version."""

    shared_indexes: tuple[int, ...] = ()
    """One-based subtitle indexes sharing this JSON decision."""

    block_number: int = 0
    """Stable one-based proofreading block number."""

    @property
    def changed(self) -> bool:
        """Whether proofreading changed this subtitle."""
        return self.original != self.reviewed

    @property
    def differences(self) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
        """CLI-compatible pairwise diff spans with safely escaped text."""
        if self.original == self.reviewed:
            return [(self.original, "match")], [(self.reviewed, "match")]
        original: list[tuple[str, str]] = []
        reviewed: list[tuple[str, str]] = []
        for column in pairwise.Alignment(self.original, self.reviewed).columns:
            kind = column.operation.name.lower()
            for character, spans in ((column.one, original), (column.two, reviewed)):
                if character is None:
                    continue
                if spans and spans[-1][1] == kind:
                    spans[-1] = (spans[-1][0] + character, kind)
                else:
                    spans.append((character, kind))
        return original, reviewed

    @property
    def time_label(self) -> str:
        """Start and end times including milliseconds."""
        return f"{_format_time(self.start)} – {_format_time(self.end)}"


@dataclass(frozen=True)
class AuditBlock:
    """A complete proofreading query group and its visible filtered rows."""

    number: int
    """Stable one-based block number in the complete subtitle track."""
    first_index: int
    """First one-based subtitle index in the complete block."""
    last_index: int
    """Last one-based subtitle index in the complete block."""
    rows: list[AuditRow]
    """Rows matching the active filters."""
    start: int
    """Start of the complete block in milliseconds."""
    end: int
    """End of the complete block in milliseconds."""

    @property
    def count(self) -> int:
        """Total subtitle count before filtering."""
        return self.last_index - self.first_index + 1

    @property
    def time_label(self) -> str:
        """Full block time range in whole seconds, including hidden rows."""
        start = _format_time(self.start, include_milliseconds=False)
        end = _format_time(self.end, include_milliseconds=False)
        return f"{start} – {end}"


@dataclass(frozen=True)
class AuditPage:
    """A bounded batch or loaded prefix and project-wide progress counts."""

    rows: list[AuditRow]
    """Visible rows."""
    blocks: list[AuditBlock]
    """Loaded matching query groups, with filtered rows inside."""
    filters: AuditFilters
    """Normalized filters."""
    total: int
    """Total current source rows."""
    verified: int
    """Verified current source rows."""
    matching: int
    """Rows matching all filters, including unloaded blocks."""
    filter_counts: dict[str, dict[str, int]]
    """Dependent option counts before pagination."""
    last_block: int
    """Stable source block cursor through which rows have loaded."""
    has_more: bool
    """Whether more matching blocks follow the loaded cursor."""


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
        self.infile_path = infile_path.resolve()
        self.outfile_path = outfile_path.resolve()
        self.json_path = None
        if json_path is not None:
            self.json_path = json_path.resolve()
        self.state_path = self.outfile_path.with_suffix(".review.sqlite3")
        self.title = title or self.infile_path.stem
        self._lock = RLock()
        self._auditing_running = False
        self._proofreading_running = False
        self._proofreading_source: Series | None = None
        self._proofreading_content: bytes | None = None
        self._proofreading_fingerprints: tuple[bytes | None, ...] | None = None
        try:
            self._validate_paths(report_path)
            self._source_content = self.infile_path.read_bytes()
            if self.state_path.exists() and self.outfile_path.exists():
                with closing(sqlite3.connect(self.state_path)) as db:
                    if db.execute(
                        "SELECT 1 FROM sqlite_master WHERE name='review_metadata'"
                    ).fetchone():
                        stored = db.execute(
                            "SELECT value FROM review_metadata WHERE name='source'"
                        ).fetchone()
                        if stored is not None:
                            self._source_content = bytes(stored[0])
            self.original = Series.from_string(
                self._source_content.decode("utf-8-sig")
                .replace("\r\n", "\n")
                .replace("\r", "\n"),
                format_="srt",
            )
            detected = language or get_series_language(self.original)
            if detected is None or detected not in DEFAULT_PROMPTS:
                raise ValueError("Specify a supported proofreading language")
            self.language = detected
            self.decisions = None
            if self.json_path is not None:
                self.decisions = ReviewDecisions(
                    self.original, self.language, self.json_path
                )
            self._block_ranges = self._get_block_ranges()
            block_numbers = {
                index: number
                for number, (first, last) in enumerate(self._block_ranges, 1)
                for index in range(first, last)
            }
            self._rows = [
                replace(row, block_number=block_numbers[row.index - 1])
                for row in self._load_rows(report_path)
            ]
            self._rows_by_key = {row.key: row for row in self._rows}
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with closing(sqlite3.connect(self.state_path)) as db, db:
                db.execute(
                    "CREATE TABLE IF NOT EXISTS review_edits ("
                    "key TEXT PRIMARY KEY, reviewed TEXT NOT NULL, "
                    "review_note TEXT NOT NULL, notes TEXT NOT NULL, "
                    "finding TEXT NOT NULL, verified INTEGER NOT NULL, "
                    "version INTEGER NOT NULL)"
                )
                db.execute(
                    "CREATE TABLE IF NOT EXISTS review_metadata ("
                    "name TEXT PRIMARY KEY, value BLOB NOT NULL)"
                )
                db.execute(
                    "INSERT OR REPLACE INTO review_metadata VALUES ('source', ?)",
                    (self._source_content,),
                )
                for previous, status in _LEGACY_STATUSES.items():
                    db.execute(
                        "UPDATE review_edits SET finding = ?, version = version + 1 "
                        "WHERE finding = ?",
                        (status.value, previous),
                    )
            self._fingerprints = self._file_fingerprints()
        except (OSError, ValueError, sqlite3.Error) as exc:
            raise ScinoephileError(f"Unable to open review editor: {exc}") from exc

    @property
    def auditing_running(self) -> bool:
        """Return whether an independent audit currently owns the review state."""
        with self._lock:
            return self._auditing_running

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
        with self._lock, closing(sqlite3.connect(self.state_path)) as db:
            stored = db.execute(
                "SELECT value FROM review_metadata WHERE name='proofreading'"
            ).fetchone()
        if stored is None:
            return {}
        return json.loads(bytes(stored[0]).decode("utf-8"))

    def begin_auditing(
        self, *, rerun: bool = False
    ) -> tuple[tuple[AuditRow, ...], ...]:
        """Reserve saved proofreading for an initial audit or whole-file re-audit.

        Arguments:
            rerun: replace existing findings for all subtitles, retaining verification
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
            self._check_file_fingerprints()
            rows = self.rows()
            blocks = tuple(
                tuple(rows[first:last])
                for first, last in self._block_ranges
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
            fingerprints = self._file_fingerprints()
            if fingerprints[1:] != self._fingerprints[1:]:
                raise ValueError("Output or JSON changed outside this session")
            content = self.infile_path.read_bytes()
            source = Series.from_string(
                content.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n"),
                format_="srt",
            )
            if [(s.start, s.end) for s in source] != [
                (s.start, s.end) for s in self.original
            ]:
                raise ValueError("OCR reload must preserve subtitle counts and timings")
            if sha256(content).digest() != fingerprints[0]:
                raise ValueError("OCR input changed while it was being loaded")
            self._proofreading_source = source
            self._proofreading_content = content
            self._proofreading_fingerprints = fingerprints
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
            self._proofreading_fingerprints = None

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
        rows = self.rows()
        matching = [row for row in rows if filters.matches(row)]
        by_block: dict[int, list[AuditRow]] = {}
        for row in matching:
            by_block.setdefault(row.block_number, []).append(row)
        blocks = []
        for number, visible in by_block.items():
            first, last = self._block_ranges[number - 1]
            blocks.append(
                AuditBlock(
                    number=number,
                    first_index=first + 1,
                    last_index=last,
                    rows=visible,
                    start=rows[first].start,
                    end=max(row.end for row in rows[first:last]),
                )
            )
        visible_blocks = [block for block in blocks if block.number > after][
            : self.page_size
        ]
        last_block = after
        if through is not None:
            visible_blocks = [block for block in blocks if block.number <= through]
            last_block = through
        elif visible_blocks:
            last_block = visible_blocks[-1].number
        return AuditPage(
            rows=[row for block in visible_blocks for row in block.rows],
            blocks=visible_blocks,
            filters=filters,
            total=len(rows),
            verified=sum(row.verified for row in rows),
            matching=len(matching),
            filter_counts=filters.counts(rows),
            last_block=last_block,
            has_more=any(block.number > last_block for block in blocks),
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
        with self._lock, closing(sqlite3.connect(self.state_path)) as db:
            if not self._auditing_running:
                raise ValueError("No audit run is active")
            self._check_file_fingerprints()
            if set(findings) != {row.index for row in block}:
                raise ValueError("Audit findings must cover the complete block")
            current = {row.key: row for row in self.rows()}
            try:
                with db:
                    for row in block:
                        if not rerun and (
                            row.verified or row.finding != AuditStatus.unaudited
                        ):
                            continue
                        if current[row.key] != row:
                            raise ValueError("Subtitle changed during auditing")
                        status, note = findings[row.index]
                        if status not in {AuditStatus.ok, AuditStatus.review}:
                            raise ValueError("Invalid automated audit verdict")
                        if (status == AuditStatus.review) != bool(note.strip()):
                            raise ValueError("Only Review verdicts require audit notes")
                        db.execute(
                            "INSERT OR REPLACE INTO review_edits VALUES "
                            "(?, ?, ?, ?, ?, ?, ?)",
                            (
                                row.key,
                                row.reviewed,
                                row.review_note,
                                note.strip(),
                                status,
                                int(row.verified),
                                row.version + 1,
                            ),
                        )
            except sqlite3.Error as exc:
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
            ValueError: if the run lost its reservation or project files changed
            ScinoephileError: if publishing files or progress fails
        """
        with self._lock, closing(sqlite3.connect(self.state_path)) as db:
            if not self._proofreading_running:
                raise ValueError("No proofreading run is active")
            if (
                self.outfile_path.exists() and not rerun
            ) or self._file_fingerprints() != self._proofreading_fingerprints:
                raise ValueError(
                    "Project files changed during proofreading; restart the app. "
                    "Output was not replaced."
                )
            source = self._proofreading_source
            content = self._proofreading_content
            assert source is not None and content is not None
            source_digest = sha256(content).hexdigest()
            decisions = ReviewDecisions(source, self.language, decisions_path)
            texts, notes = decisions.render()
            ranges = self._get_block_ranges(decisions, source=source)
            blocks = {
                index: number
                for number, (first, last) in enumerate(ranges, 1)
                for index in range(first, last)
            }
            previous = self.rows()
            updated = []
            for row in previous:
                current = replace(
                    row,
                    key=sha256(
                        f"{source_digest}:{self.language.code}:{row.index - 1}".encode()
                    ).hexdigest(),
                    original=source.events[row.index - 1].text_with_newline,
                    reviewed=texts[row.index - 1],
                    review_note=notes[row.index - 1],
                    block_number=blocks[row.index - 1],
                    shared_indexes=decisions.shared_indexes(row.index - 1),
                    version=row.version + 1,
                )
                if (
                    current.original != row.original
                    or current.reviewed != row.reviewed
                    or current.review_note != row.review_note
                ):
                    current = replace(
                        current, finding=AuditStatus.unaudited, notes="", verified=False
                    )
                updated.append(current)
            originals = None
            try:
                if rerun:
                    self._backup_proofreading(db)
                db.execute("BEGIN IMMEDIATE")
                db.executemany(
                    "DELETE FROM review_edits WHERE key=?",
                    [(row.key,) for row in previous],
                )
                db.executemany(
                    "INSERT OR REPLACE INTO review_edits VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [
                        (
                            row.key,
                            row.reviewed,
                            row.review_note,
                            row.notes,
                            row.finding,
                            int(row.verified),
                            row.version,
                        )
                        for row in updated
                    ],
                )
                db.execute(
                    "INSERT OR REPLACE INTO review_metadata VALUES ('source', ?)",
                    (content,),
                )
                if settings is not None:
                    db.execute(
                        "INSERT OR REPLACE INTO review_metadata "
                        "VALUES ('proofreading', ?)",
                        (json.dumps(settings).encode("utf-8"),),
                    )
                originals = self._write_files(updated, decisions, source=source)
                db.commit()
            except (OSError, sqlite3.Error) as exc:
                db.rollback()
                if originals is not None:
                    _restore_files(originals)
                raise ScinoephileError(
                    f"Unable to publish proofreading: {exc}"
                ) from exc
            self.original = source
            self._source_content = content
            self.decisions = decisions
            self._block_ranges = ranges
            self._rows = updated
            self._rows_by_key = {row.key: row for row in updated}
            self._fingerprints = self._file_fingerprints()

    def rows(self) -> list[AuditRow]:
        """Read current text and independent progress without stale form caching.

        Returns:
            current editable rows and their audit progress
        """
        with self._lock, closing(sqlite3.connect(self.state_path)) as db:
            saved = {
                row[0]: row[1:] for row in db.execute("SELECT * FROM review_edits")
            }
            rows = []
            for row in self._rows:
                current = row
                if row.key in saved:
                    text, note, notes, finding, verified, version = saved[row.key]
                    current = replace(row, version=version)
                    native_matches = note == row.review_note
                    if self.decisions is None or not self.decisions.cases:
                        native_matches = True
                    if text == row.reviewed and native_matches:
                        current = replace(
                            current,
                            review_note=note,
                            notes=notes,
                            finding=AuditStatus(finding),
                            verified=bool(verified),
                        )
                rows.append(current)
            return rows

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
        """Save edited subtitles and optional native JSON with stale-write checks.

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
        if key not in self._rows_by_key:
            raise KeyError(key)
        reviewed = reviewed.replace("\r\n", "\n").replace("\r", "\n")
        if not reviewed.strip() or len(reviewed) > 1000 or "\n\n" in reviewed:
            raise ValueError(
                "Subtitle text must contain 1–1000 characters and no blank lines"
            )
        if reviewed != self._rows_by_key[key].original and not review_note.strip():
            raise ValueError("A note is required for changed proofreading text")
        if len(review_note) > 1000:
            raise ValueError("Revision notes must not exceed 1000 characters")
        try:
            finding = AuditStatus(_LEGACY_STATUSES.get(finding, finding))
        except ValueError as exc:
            raise ValueError("Unknown audit verdict") from exc
        _validate_audit_notes(finding, notes)
        with self._lock, closing(sqlite3.connect(self.state_path)) as db:
            if self._proofreading_running or self._auditing_running:
                raise ValueError(
                    "Wait for proofreading or auditing to finish before editing"
                )
            originals = None
            try:
                db.execute("BEGIN IMMEDIATE")
                rows = self.rows()
                current = next(row for row in rows if row.key == key)
                if version != current.version:
                    raise ValueError(
                        "This row changed in another tab. Reload before saving."
                    )
                self._check_file_fingerprints()
                updated, decisions = self._prepare_edit(
                    rows, current, reviewed, review_note
                )
                affected = {row.key for row in updated if row != rows[row.index - 1]}
                affected.add(key)
                for row in updated:
                    if row.key not in affected:
                        continue
                    saved = replace(
                        row, verified=False, finding=AuditStatus.unaudited, notes=""
                    )
                    if row.key == key:
                        saved = replace(
                            saved, notes=notes, finding=finding, verified=verified
                        )
                    db.execute(
                        "INSERT INTO review_edits VALUES (?, ?, ?, ?, ?, ?, ?) "
                        "ON CONFLICT(key) DO UPDATE SET reviewed=excluded.reviewed, "
                        "review_note=excluded.review_note, notes=excluded.notes, "
                        "finding=excluded.finding, verified=excluded.verified, "
                        "version=excluded.version",
                        (
                            saved.key,
                            saved.reviewed,
                            saved.review_note,
                            saved.notes,
                            saved.finding,
                            int(saved.verified),
                            saved.version + 1,
                        ),
                    )
                originals = self._write_files(updated, decisions)
                db.commit()
            except (OSError, sqlite3.Error) as exc:
                db.rollback()
                if originals is not None:
                    _restore_files(originals)
                raise ScinoephileError(f"Unable to save review edits: {exc}") from exc
            self.decisions = decisions
            self._rows = updated
            self._rows_by_key = {row.key: row for row in updated}
            self._fingerprints = self._file_fingerprints()
            return affected

    def verification_token(self, filters: AuditFilters) -> str:
        """Identify the full filtered selection, including unloaded subtitles.

        Arguments:
            filters: current browser filters
        Returns:
            digest of matching row identities and edit versions
        """
        filters.validate()
        selection = [
            (row.key, row.version) for row in self.rows() if filters.matches(row)
        ]
        return sha256(repr(selection).encode()).hexdigest()

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
        with self._lock, closing(sqlite3.connect(self.state_path)) as db:
            if not self.outfile_path.exists():
                raise ValueError("Run proofreading before verifying subtitles")
            if self._proofreading_running or self._auditing_running:
                raise ValueError("Wait for proofreading or auditing to finish")
            self._check_file_fingerprints()
            try:
                db.execute("BEGIN IMMEDIATE")
                if token != self.verification_token(filters):
                    raise ValueError(
                        "The matching subtitles changed. Reload before verifying."
                    )
                rows = [
                    row
                    for row in self.rows()
                    if filters.matches(row) and not row.verified
                ]
                for row in rows:
                    _validate_audit_notes(row.finding, row.notes)
                db.executemany(
                    "INSERT OR REPLACE INTO review_edits VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [
                        (
                            row.key,
                            row.reviewed,
                            row.review_note,
                            row.notes,
                            row.finding,
                            1,
                            row.version + 1,
                        )
                        for row in rows
                    ],
                )
                db.commit()
            except sqlite3.Error as exc:
                raise ScinoephileError(f"Unable to verify subtitles: {exc}") from exc
            return len(rows)

    def _backup_proofreading(self, db: sqlite3.Connection):
        """Snapshot existing output and review state before a successful rerun.

        Arguments:
            db: current review database before its write transaction begins
        """
        backup_dir_path = Path(
            mkdtemp(
                prefix=f"{self.outfile_path.stem}.before-reproofread-",
                dir=self.outfile_path.parent,
            )
        )
        copy2(self.outfile_path, backup_dir_path / "proofread.srt")
        if self.json_path is not None and self.json_path.exists():
            copy2(self.json_path, backup_dir_path / "review.json")
        with closing(sqlite3.connect(backup_dir_path / "review.sqlite3")) as backup_db:
            db.backup(backup_db)

    def _check_file_fingerprints(self):
        """Reject changes made outside the active editor's write transaction.

        Raises:
            ValueError: if original, output, or native decisions changed externally
        """
        if self.input_changed:
            raise ValueError(
                "OCR input changed. Re-proofread before editing or auditing."
            )
        if self._file_fingerprints() != self._fingerprints:
            raise ValueError(
                "A subtitle or JSON file changed outside this session. "
                "Restart before saving."
            )

    def _file_fingerprints(self) -> tuple[bytes | None, ...]:
        """Hash source and writable files to reject external edits on save.

        Returns:
            content digests, including absent optional files
        """
        fingerprints = []
        for file_path in (self.infile_path, self.outfile_path, self.json_path):
            value = None
            if file_path is not None and file_path.exists():
                value = sha256(file_path.read_bytes()).digest()
            fingerprints.append(value)
        return tuple(fingerprints)

    def _get_block_ranges(
        self, decisions: ReviewDecisions | None = None, *, source: Series | None = None
    ) -> list[tuple[int, int]]:
        """Resolve logged query boundaries, falling back to original pause blocks.

        Arguments:
            decisions: candidate decisions, or current session decisions
            source: candidate input, or the published source baseline
        Returns:
            nonoverlapping zero-based inclusive/exclusive subtitle ranges
        """
        if decisions is None:
            decisions = self.decisions
        if source is None:
            source = self.original
        count = len(source)
        if not count:
            return []
        joined = [False] * (count - 1)
        covered = set()
        if decisions is not None:
            for case_index, starts in decisions.locations.items():
                size = len(decisions.cases[case_index].query.subtitles)
                for first in starts:
                    covered.update(range(first, first + size))
                    for index in range(first, first + size - 1):
                        joined[index] = True
        for first, last in Series.get_block_indexes_by_pause(source):
            for index in range(first, last - 1):
                if index not in covered and index + 1 not in covered:
                    joined[index] = True
        boundaries = [0]
        boundaries.extend(index + 1 for index, value in enumerate(joined) if not value)
        boundaries.append(count)
        return list(zip(boundaries[:-1], boundaries[1:], strict=True))

    def _load_output(self) -> tuple[list[str], list[str]]:
        """Load output or native proposals and validate their correspondence.

        Returns:
            editable output text and native revision explanations
        Raises:
            ValueError: if output timings or JSON answers disagree
        """
        texts = [s.text_with_newline for s in self.original]
        revision_notes = [""] * len(texts)
        if self.decisions is not None:
            texts, revision_notes = self.decisions.render()
        if self.outfile_path.exists():
            output = Series.load(self.outfile_path)
            if [(s.start, s.end) for s in output] != [
                (s.start, s.end) for s in self.original
            ]:
                raise ValueError("Original and output subtitle timings must match")
            output_texts = [s.text_with_newline for s in output]
            if self.decisions is not None and self.decisions.cases:
                if output_texts != texts:
                    raise ValueError("Output subtitles disagree with the review JSON")
            else:
                texts = output_texts
        return texts, revision_notes

    def _load_rows(self, report_path: Path | None) -> list[AuditRow]:
        """Load saved output or native proposals and optional independent notes.

        Arguments:
            report_path: optional report used only for audit-note import
        Returns:
            source rows with editable text and revision notes
        Raises:
            ValueError: if output timings or decision answers conflict
        """
        texts, revision_notes = self._load_output()
        imported = {}
        if report_path is not None:
            imported = _load_report_notes(report_path, len(self.original))
        label = self.language.code
        if self.language == Language.eng:
            label = "English"
        source_digest = sha256(self._source_content).hexdigest()
        rows = []
        for index, source in enumerate(self.original.events):
            note = imported.get(index + 1, "")
            finding = AuditStatus.unaudited
            if note == "OK":
                finding = AuditStatus.ok
                note = ""
            elif note.startswith(("Review;", "Incorrect;", "Check;")):
                finding = AuditStatus.review
            shared = (index + 1,)
            if self.decisions is not None:
                shared = self.decisions.shared_indexes(index)
            key = sha256(
                f"{source_digest}:{self.language.code}:{index}".encode()
            ).hexdigest()
            rows.append(
                AuditRow(
                    key=key,
                    track_id=self.language.code,
                    label=label,
                    language=self.language.code,
                    index=index + 1,
                    start=source.start,
                    end=source.end,
                    original=source.text_with_newline,
                    reviewed=texts[index],
                    review_note=revision_notes[index],
                    notes=note,
                    finding=finding,
                    shared_indexes=shared,
                )
            )
        return rows

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

    def _validate_paths(self, report_path: Path | None):
        """Require distinct subtitle, JSON, progress and optional report files.

        Arguments:
            report_path: optional read-only report path
        Raises:
            ValueError: if paths collide or the output is not an SRT
        """
        paths = [self.infile_path, self.outfile_path, self.state_path]
        if self.json_path is not None:
            paths.append(self.json_path)
        if report_path is not None:
            paths.append(report_path.resolve())
        if len(set(paths)) != len(paths):
            raise ValueError(
                "Input, output, JSON, progress and report paths must differ"
            )
        for index, left_path in enumerate(paths):
            for right_path in paths[index + 1 :]:
                if (
                    left_path.exists()
                    and right_path.exists()
                    and left_path.samefile(right_path)
                ):
                    raise ValueError(
                        "Input and writable files must not alias each other"
                    )
        if self.outfile_path.suffix.lower() != ".srt":
            raise ValueError("The edited subtitle output must be an SRT file")

    def _write_files(
        self,
        rows: list[AuditRow],
        decisions: ReviewDecisions | None,
        *,
        source: Series | None = None,
    ) -> dict[Path, bytes | None]:
        """Replace each output atomically and restore files on an I/O failure.

        Arguments:
            rows: validated final subtitle rows
            decisions: candidate native JSON decisions
            source: candidate input, or the published source baseline
        Returns:
            original file contents for rollback if the database commit fails
        Raises:
            BaseException: if writing fails, after restoring replaced files
        """
        if source is None:
            source = self.original
        output = deepcopy(source)
        for subtitle, row in zip(output, rows, strict=True):
            subtitle.text = row.reviewed.replace("\n", "\\N")
        writes = {self.outfile_path: output.to_string("srt")}
        if decisions is not None and self.json_path is not None:
            writes[self.json_path] = decisions.serialize()
        originals: dict[Path, bytes | None] = {p: None for p in writes}
        for file_path in writes:
            if file_path.exists():
                originals[file_path] = file_path.read_bytes()
        written = []
        try:
            for file_path, content in writes.items():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open_atomic_text_file(file_path) as handle:
                    handle.write(content)
                written.append(file_path)
        except BaseException:
            _restore_files({p: originals[p] for p in reversed(written)})
            raise
        return originals


def _format_time(milliseconds: int, *, include_milliseconds: bool = True) -> str:
    """Format a subtitle timestamp with optional millisecond precision.

    Arguments:
        milliseconds: subtitle timestamp
        include_milliseconds: whether to append fractional seconds
    Returns:
        hours, minutes, seconds and milliseconds
    """
    seconds, remainder = divmod(milliseconds, 1000)
    formatted = f"{seconds // 3600:02d}:{seconds // 60 % 60:02d}:{seconds % 60:02d}"
    if include_milliseconds:
        formatted += f".{remainder:03d}"
    return formatted


def _load_report_notes(file_path: Path, count: int) -> dict[int, str]:
    """Import only Notes from a generated audit table, never its rendered text.

    Arguments:
        file_path: existing Markdown audit report
        count: number of source subtitles
    Returns:
        independent notes keyed by one-based subtitle number
    Raises:
        ValueError: if the table is malformed, duplicated, or out of range
    """
    columns = []
    notes = {}
    for line in file_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line)[1:-1]]
        if cells and cells[0] == "Subtitle":
            columns = cells
            continue
        if not cells or not cells[0].isdigit():
            continue
        if len(cells) != len(columns) or "Notes" not in columns:
            raise ValueError("Audit report has no valid Notes column")
        index = int(cells[0])
        if not 1 <= index <= count or index in notes:
            raise ValueError("Audit report has duplicate or out-of-range row indexes")
        notes[index] = unescape(
            cells[columns.index("Notes")].replace("\\|", "|").replace("<br>", "\n")
        )
    if not notes:
        raise ValueError("Audit report contains no subtitle rows")
    return notes


def _restore_files(originals: dict[Path, bytes | None]):
    """Restore replaced files byte-for-byte after a failed save.

    Arguments:
        originals: old file bytes, or None for newly created outputs
    Raises:
        OSError: if restoring a file fails
    """
    for file_path, original in originals.items():
        if original is None:
            file_path.unlink(missing_ok=True)
            continue
        with NamedTemporaryFile("wb", dir=file_path.parent, delete=False) as handle:
            temp_path = Path(handle.name)
            try:
                handle.write(original)
                handle.flush()
                fsync(handle.fileno())
            except BaseException:
                handle.close()
                temp_path.unlink(missing_ok=True)
                raise
        try:
            temp_path.replace(file_path)
        finally:
            temp_path.unlink(missing_ok=True)


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
