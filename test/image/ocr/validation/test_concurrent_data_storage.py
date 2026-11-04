#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Regressions for OCR approval updates from stale and concurrent sessions."""

from __future__ import annotations

from copy import deepcopy
from functools import partial
from pathlib import Path
from subprocess import PIPE, Popen
from sys import executable
from textwrap import dedent
from time import monotonic, sleep
from unittest.mock import Mock

from PIL import Image
from pytest import MonkeyPatch, fixture, raises

from scinoephile.common.file import file_lock
from scinoephile.core import ScinoephileError
from scinoephile.image.bbox import Bbox
from scinoephile.image.ocr.validation import ValidationManager, validation_manager
from scinoephile.image.ocr.validation.char_pair_gaps import (
    get_default_char_pair_cutoffs,
    load_char_pair_gaps,
)
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from scinoephile.web.ocr_validation.session import OcrValidationSession
from test.helpers import parametrize
from test.helpers.ocr_validation import make_ocr_html_dir, patch_ocr_validation_bboxes


@fixture
def repo_root_path(tmp_path: Path, monkeypatch: MonkeyPatch) -> Path:
    """Provide isolated repository OCR data for both runtime and development modes.

    Arguments:
        tmp_path: temporary directory for all approval files
        monkeypatch: fixture redirecting the validation manager's repository root
    """
    repo_path = tmp_path / "repo"
    (repo_path / "data/ocr").mkdir(parents=True)
    monkeypatch.setattr(validation_manager, "package_root", repo_path)
    return repo_path


@parametrize("dev", [False, True])
def test_stale_managers_preserve_all_approval_types(
    tmp_path: Path, repo_root_path: Path, dev: bool
):
    """Merge each approval into current storage instead of a session snapshot.

    Arguments:
        tmp_path: temporary directory for runtime data
        repo_root_path: isolated repository data root
        dev: whether approvals belong to repository data
    """
    data_dir_path = tmp_path / "data"
    first = ValidationManager(validation_data_dir_path=data_dir_path, dev=dev)
    second = ValidationManager(validation_data_dir_path=data_dir_path, dev=dev)

    first.update_char_dims("A", (10, 20))
    second.update_char_dims("A", (11, 21))
    first.update_char_dims("B", (30, 40))
    first._update_char_grp_dims("AB", (50, 20))
    second._update_char_grp_dims("AB", (51, 21))
    second._update_char_grp_dims("CD", (60, 20))
    first.update_pair_gaps(("A", "B"), (1, 2, 3, 4))
    second.update_pair_gaps(("C", "D"), (5, 6, 7, 8))

    loaded = ValidationManager(validation_data_dir_path=data_dir_path, dev=dev)
    assert loaded.char_dims_by_n[1] == {"A": {(10, 20), (11, 21)}, "B": {(30, 40)}}
    assert loaded.char_grp_dims_by_n == {
        2: {"AB": {(50, 20), (51, 21)}, "CD": {(60, 20)}}
    }
    assert loaded.char_pair_gaps == {("A", "B"): (1, 2, 3, 4), ("C", "D"): (5, 6, 7, 8)}
    if dev:
        assert (repo_root_path / "data/ocr/char_dims_1.csv").is_file()
        assert not data_dir_path.exists()


@parametrize("dev", [False, True])
@parametrize("entrypoint", ["manager", "web"])
def test_first_gap_lookup_preserves_another_sessions_approval(
    tmp_path: Path,
    repo_root_path: Path,
    monkeypatch: MonkeyPatch,
    dev: bool,
    entrypoint: str,
):
    """Use a newly saved spacing approval when a stale session first sees the pair.

    Arguments:
        tmp_path: temporary directory for runtime data and subtitle images
        repo_root_path: isolated repository data root
        monkeypatch: fixture replacing bbox detection with known character positions
        dev: whether approvals belong to repository data
        entrypoint: validation path encountering the previously unseen pair
    """
    data_dir_path = tmp_path / "data"
    first = ValidationManager(validation_data_dir_path=data_dir_path, dev=dev)
    session = None
    if entrypoint == "web":
        html_dir_path = make_ocr_html_dir(tmp_path, text="A B")
        session = OcrValidationSession.from_dir_path(
            html_dir_path, validation_data_dir_path=data_dir_path, dev=dev
        )
        second = session.manager
        bbox_target = "scinoephile.web.ocr_validation.session.get_bboxes"
    else:
        second = ValidationManager(validation_data_dir_path=data_dir_path, dev=dev)
        bbox_target = "scinoephile.image.ocr.validation.validation_manager.get_bboxes"
    second.char_dims_by_n[1] = {"A": {(10, 20)}, "B": {(10, 20)}}
    assert ("A", "B") not in second.char_pair_gaps
    patch_ocr_validation_bboxes(
        monkeypatch, [Bbox(0, 10, 0, 20), Bbox(13, 23, 0, 20)], target=bbox_target
    )

    first.update_pair_gaps(("A", "B"), (1, 2, 3, 4))
    output_dir_path = data_dir_path
    if dev:
        output_dir_path = repo_root_path / "data/ocr"
    saved_path = output_dir_path / "char_pair_gaps.csv"
    saved_data = saved_path.read_bytes()

    if session is not None:
        row = session.subtitle_row(0)
        actual_text = row.text
        assert row.concern is None
    else:
        series = ImageSeries(
            events=[
                ImageSubtitle(
                    start=1000,
                    end=2000,
                    img=Image.new("LA", (40, 24), (255, 255)),
                    text="A B",
                )
            ]
        )
        actual_text = second.validate(series).events[0].text

    assert saved_path.read_bytes() == saved_data
    assert second.char_pair_gaps[("A", "B")] == (1, 2, 3, 4)
    assert actual_text == "A B"


@parametrize("dev", [False, True])
def test_stale_pair_gap_reset_removes_only_its_current_override(
    tmp_path: Path, repo_root_path: Path, dev: bool
):
    """Apply a reset despite a stale default, preserving unrelated newer decisions.

    Arguments:
        tmp_path: temporary directory for runtime data
        repo_root_path: isolated repository data root
        dev: whether approvals belong to repository data
    """
    data_dir_path = tmp_path / "data"
    first = ValidationManager(validation_data_dir_path=data_dir_path, dev=dev)
    second = ValidationManager(validation_data_dir_path=data_dir_path, dev=dev)
    default_cutoffs = get_default_char_pair_cutoffs("A", "B")
    first.update_pair_gaps(("A", "B"), default_cutoffs)
    second.update_pair_gaps(("A", "B"), (1, 2, 3, 4))
    second.update_pair_gaps(("C", "D"), (5, 6, 7, 8))

    first.update_pair_gaps(("A", "B"), default_cutoffs)
    second.update_pair_gaps(("E", "F"), (2, 3, 4, 5))

    output_dir_path = data_dir_path
    if dev:
        output_dir_path = repo_root_path / "data/ocr"
    assert load_char_pair_gaps(output_dir_path / "char_pair_gaps.csv") == {
        ("C", "D"): (5, 6, 7, 8),
        ("E", "F"): (2, 3, 4, 5),
    }
    assert first.char_pair_gaps[("A", "B")] == default_cutoffs


@parametrize("dev", [False, True])
@parametrize("has_saved_approval", [False, True])
def test_default_gap_lookup_does_not_change_saved_approvals(
    tmp_path: Path, repo_root_path: Path, dev: bool, has_saved_approval: bool
):
    """Keep heuristic defaults in memory without creating or rewriting CSV data.

    Arguments:
        tmp_path: temporary directory for runtime data
        repo_root_path: isolated repository data root
        dev: whether approvals belong to repository data
        has_saved_approval: whether another session has saved an unrelated approval
    """
    data_dir_path = tmp_path / "data"
    first = ValidationManager(validation_data_dir_path=data_dir_path, dev=dev)
    second = ValidationManager(validation_data_dir_path=data_dir_path, dev=dev)
    output_dir_path = data_dir_path
    if dev:
        output_dir_path = repo_root_path / "data/ocr"
    saved_path = output_dir_path / "char_pair_gaps.csv"
    saved_data = None
    if has_saved_approval:
        first.update_pair_gaps(("C", "D"), (5, 6, 7, 8))
        saved_data = saved_path.read_bytes()

    default_cutoffs = get_default_char_pair_cutoffs("A", "B")
    assert second.get_pair_gaps(("A", "B")) == default_cutoffs
    assert second.get_pair_gaps(("A", "B")) == default_cutoffs
    assert second.char_pair_gaps[("A", "B")] == default_cutoffs
    if saved_data is None:
        assert not saved_path.exists()
    else:
        assert saved_path.read_bytes() == saved_data
        assert second.char_pair_gaps[("C", "D")] == (5, 6, 7, 8)


@parametrize("operation", ["character", "group", "gap", "lookup"])
def test_lock_contention_is_user_facing_and_preserves_session_state(
    tmp_path: Path, repo_root_path: Path, monkeypatch: MonkeyPatch, operation: str
):
    """Report an occupied lock without changing approval data or session state.

    Arguments:
        tmp_path: temporary directory for runtime data
        repo_root_path: isolated repository data root
        monkeypatch: fixture selecting immediate lock-conflict reporting
        operation: approval blocked by another writer
    """
    data_dir_path = tmp_path / "data"
    manager = ValidationManager(validation_data_dir_path=data_dir_path)
    state = deepcopy(vars(manager))
    monkeypatch.setattr(validation_manager, "file_lock", partial(file_lock, timeout=0))
    with file_lock(data_dir_path / ".validation.lock"):
        with raises(ScinoephileError, match="File lock is held"):
            if operation == "character":
                manager.update_char_dims("A", (10, 20))
            elif operation == "group":
                manager._update_char_grp_dims("AB", (50, 20))
            elif operation == "lookup":
                manager.get_pair_gaps(("A", "B"))
            else:
                manager.update_pair_gaps(("A", "B"), (1, 2, 3, 4))
    assert vars(manager) == state
    assert list(data_dir_path.glob("*.csv")) == []


@parametrize("dev", [False, True])
@parametrize("operation", ["character", "group", "gap", "reset"])
def test_failed_serialization_preserves_memory_and_durable_data(
    tmp_path: Path,
    repo_root_path: Path,
    monkeypatch: MonkeyPatch,
    dev: bool,
    operation: str,
):
    """Keep saved approvals and session state intact if CSV serialization fails.

    Arguments:
        tmp_path: temporary directory for runtime data
        repo_root_path: isolated repository data root
        monkeypatch: fixture replacing CSV serialization with a failing writer
        dev: whether approvals belong to repository data
        operation: approval or reset that fails during persistence
    """
    data_dir_path = tmp_path / "data"
    manager = ValidationManager(validation_data_dir_path=data_dir_path, dev=dev)
    manager.update_char_dims("A", (10, 20))
    manager._update_char_grp_dims("AB", (50, 20))
    manager.update_pair_gaps(("A", "B"), (1, 2, 3, 4))
    output_dir_path = data_dir_path
    if dev:
        output_dir_path = repo_root_path / "data/ocr"
    originals = {path.name: path.read_bytes() for path in output_dir_path.glob("*.csv")}
    state = deepcopy(vars(manager))
    with monkeypatch.context() as patcher:
        patcher.setattr(
            "scinoephile.image.ocr.validation.csv.csv.writer",
            Mock(side_effect=ValueError("serialization failed")),
        )
        with raises(ScinoephileError, match="serialization failed"):
            if operation == "character":
                manager.update_char_dims("B", (30, 40))
            elif operation == "group":
                manager._update_char_grp_dims("CD", (60, 20))
            elif operation == "gap":
                manager.update_pair_gaps(("C", "D"), (5, 6, 7, 8))
            else:
                manager.update_pair_gaps(
                    ("A", "B"), get_default_char_pair_cutoffs("A", "B")
                )
    assert vars(manager) == state
    assert {
        path.name: path.read_bytes() for path in output_dir_path.glob("*.csv")
    } == originals
    assert list(output_dir_path.glob("*.tmp")) == []
    with file_lock(output_dir_path / ".validation.lock", timeout=0):
        pass


def test_competing_processes_reload_under_the_data_lock(
    tmp_path: Path, repo_root_path: Path
):
    """Serialize two competing process updates through loading, merging, and saving.

    Arguments:
        tmp_path: temporary directory for worker coordination and runtime data
        repo_root_path: isolated repository data root
    """
    data_dir_path = tmp_path / "data"
    data_dir_path.mkdir()
    (data_dir_path / "char_dims_1.csv").write_text("C,30,40\n", encoding="utf-8")
    worker_code = dedent(
        """
        import sys
        from pathlib import Path
        from time import monotonic, sleep

        data_path, repo_path, label, source_path = sys.argv[1:]
        sys.path.insert(0, source_path)
        from scinoephile.image.ocr.validation import ValidationManager
        from scinoephile.image.ocr.validation import validation_manager

        assert Path(validation_manager.__file__).is_relative_to(source_path)
        data_path = Path(data_path)
        validation_manager.package_root = Path(repo_path)
        manager = ValidationManager(validation_data_dir_path=data_path)
        original_load = validation_manager.load_char_dims
        def delayed_load(file_path):
            data = original_load(file_path)
            (data_path / f'reading-{label}').touch()
            sleep(0.2)
            return data
        validation_manager.load_char_dims = delayed_load
        (data_path / f'ready-{label}').touch()
        deadline = monotonic() + 20
        while not (data_path / 'start').exists():
            if monotonic() > deadline:
                raise TimeoutError('Parent did not start the worker')
            sleep(0.01)
        manager.update_char_dims(label, (10, 20))
        """
    )
    workers: list[Popen[str]] = []
    try:
        with file_lock(data_dir_path / ".validation.lock"):
            for label in ("A", "B"):
                # Preserve each worker for cleanup if starting its successor fails
                workers.append(  # noqa: PERF401
                    Popen(
                        [
                            executable,
                            "-c",
                            worker_code,
                            str(data_dir_path),
                            str(repo_root_path),
                            label,
                            str(Path(__file__).resolve().parents[4]),
                        ],
                        stdout=PIPE,
                        stderr=PIPE,
                        text=True,
                        encoding="utf-8",
                    )
                )
            deadline = monotonic() + 20
            while not all(
                (data_dir_path / f"ready-{label}").exists() for label in ("A", "B")
            ):
                assert monotonic() < deadline, "Workers did not initialize"
                assert all(worker.poll() is None for worker in workers)
                sleep(0.01)
            (data_dir_path / "start").touch()
            sleep(0.2)
            assert list(data_dir_path.glob("reading-*")) == []
        for worker in workers:
            stdout, stderr = worker.communicate(timeout=20)
            assert worker.returncode == 0, f"{stdout}\n{stderr}"
    finally:
        for worker in workers:
            if worker.poll() is None:
                worker.kill()
            worker.communicate(timeout=5)
    loaded = ValidationManager(validation_data_dir_path=data_dir_path)
    assert loaded.user_char_dims_by_n[1] == {
        "A": {(10, 20)},
        "B": {(10, 20)},
        "C": {(30, 40)},
    }
