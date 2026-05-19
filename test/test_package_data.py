#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of package data included in distribution artifacts."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def test_installed_wheel_includes_runtime_data_files(tmp_path: Path):
    """Test installed wheels expose runtime data files under package_root."""
    project_root_path = Path(__file__).resolve().parents[1]
    build_source_dir_path = _copy_build_source(project_root_path, tmp_path / "source")
    source_data_dir_path = build_source_dir_path / "scinoephile/data"
    ignored_local_dump_path = (
        source_data_dir_path / "dictionaries/wiktionary/entries.jsonl"
    )
    wheel_dir_path = tmp_path / "wheel"
    install_dir_path = tmp_path / "install"

    expected_data_file_paths = sorted(
        path.relative_to(source_data_dir_path).as_posix()
        for path in source_data_dir_path.rglob("*")
        if path.is_file() and path != ignored_local_dump_path
    )
    ignored_local_dump_path.parent.mkdir(parents=True, exist_ok=True)
    ignored_local_dump_path.write_text("{}\n", encoding="utf-8")

    uv_path = shutil.which("uv")
    assert uv_path is not None

    command_env = os.environ.copy()
    command_env["UV_CACHE_DIR"] = command_env.get("UV_CACHE_DIR", "/tmp/uv-cache")

    _run_required_command(
        [
            uv_path,
            "build",
            "--wheel",
            "--out-dir",
            str(wheel_dir_path),
        ],
        cwd_path=build_source_dir_path,
        env=command_env,
    )
    wheel_path = _get_single_wheel_path(wheel_dir_path)

    _run_required_command(
        [
            uv_path,
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(install_dir_path),
            str(wheel_path),
        ],
        cwd_path=tmp_path,
        env=command_env,
    )

    smoke_env = command_env.copy()
    smoke_env["EXPECTED_DATA_FILES"] = json.dumps(expected_data_file_paths)
    smoke_env["PYTHONPATH"] = str(install_dir_path)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import json
import os

from scinoephile.common import package_root

expected_data_file_paths = json.loads(os.environ["EXPECTED_DATA_FILES"])
missing_data_file_paths = [
    data_file_path
    for data_file_path in expected_data_file_paths
    if not (package_root / "data" / data_file_path).is_file()
]
if missing_data_file_paths:
    raise AssertionError(
        f"Missing installed data files: {missing_data_file_paths}"
    )
if (package_root / "data/dictionaries/wiktionary/entries.jsonl").exists():
    raise AssertionError("Installed wheel includes ignored Wiktionary dump")
""",
        ],
        cwd=tmp_path,
        env=smoke_env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def _copy_build_source(project_root_path: Path, output_dir_path: Path) -> Path:
    """Copy the project files needed to build a wheel.

    Arguments:
        project_root_path: source project root directory
        output_dir_path: temporary directory to receive the build source
    Returns:
        copied project root directory
    """
    shutil.copytree(
        project_root_path / "scinoephile",
        output_dir_path / "scinoephile",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    for file_name in (
        "LICENSE",
        "MANIFEST.in",
        "README.md",
        "pyproject.toml",
        "uv.lock",
    ):
        file_path = project_root_path / file_name
        if file_path.exists():
            shutil.copy2(file_path, output_dir_path / file_name)
    return output_dir_path


def _get_single_wheel_path(wheel_dir_path: Path) -> Path:
    """Get the only scinoephile wheel path from a directory.

    Arguments:
        wheel_dir_path: directory containing build output
    Returns:
        path to the built wheel
    """
    wheel_paths = sorted(wheel_dir_path.glob("scinoephile-*.whl"))
    if len(wheel_paths) != 1:
        found_file_names = sorted(path.name for path in wheel_dir_path.iterdir())
        pytest.fail(
            "Expected exactly one scinoephile wheel in "
            f"{wheel_dir_path}, found {len(wheel_paths)}: {found_file_names}"
        )
    return wheel_paths[0]


def _run_required_command(
    args: list[str],
    *,
    cwd_path: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    """Run a required subprocess command.

    Arguments:
        args: command and arguments to run
        cwd_path: working directory
        env: environment variables
    Returns:
        completed subprocess result
    """
    result = subprocess.run(
        args,
        cwd=cwd_path,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.fail(
            f"Command failed: {' '.join(args)}\n{result.stdout}\n{result.stderr}"
        )
    return result
