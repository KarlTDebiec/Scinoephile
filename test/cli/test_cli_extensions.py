#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Exercise installed CLI extensions through Scinoephile's command entry point."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from pytest import fixture, mark

from scinoephile.common import package_root


@fixture
def extension_site_path(tmp_path: Path) -> Path:
    """Provide an installed-layout distribution exposing a nested command.

    Arguments:
        tmp_path: temporary directory for the isolated distribution
    """
    (tmp_path / "sample_extension.py").write_text(
        '''from scinoephile.core.cli import ScinoephileCliBase

class EchoCli(ScinoephileCliBase):
    """Echo a supplied value."""

    @classmethod
    def add_arguments_to_argparser(cls, parser):
        super().add_arguments_to_argparser(parser)
        parser.add_argument("subcommand_name")

    @classmethod
    def _main(cls, *, subcommand_name):
        print(subcommand_name)

class ToolsCli(ScinoephileCliBase):
    """Group extension commands."""

    @classmethod
    def add_arguments_to_argparser(cls, parser):
        super().add_arguments_to_argparser(parser)
        subparsers = parser.add_subparsers(dest=cls.subcommand_dest(), required=True)
        EchoCli.argparser(subparsers=subparsers)

    @classmethod
    def _main(cls, **kwargs):
        assert kwargs.pop(cls.subcommand_dest()) == EchoCli.name()
        EchoCli._main(**kwargs)
''',
        encoding="utf-8",
    )
    metadata_dir_path = tmp_path / "sample_extension-1.0.dist-info"
    metadata_dir_path.mkdir()
    (metadata_dir_path / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: sample-extension\nVersion: 1.0\n",
        encoding="utf-8",
    )
    (metadata_dir_path / "entry_points.txt").write_text(
        "[scinoephile.cli.commands]\ntools = sample_extension:ToolsCli\n",
        encoding="utf-8",
    )
    return tmp_path


@mark.parametrize(
    ("arguments", "expected"),
    [
        (["--help"], ["tools", "media"]),
        (["tools", "echo", "extension works"], ["extension works"]),
    ],
)
def test_installed_extension(
    extension_site_path: Path, arguments: list[str], expected: list[str]
):
    """Discover real installed metadata and preserve the leaf command's arguments.

    Arguments:
        extension_site_path: isolated extension and its distribution metadata
        arguments: help or command tokens to pass to the application
        expected: expected fragments of the command output
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(extension_site_path), str(package_root.parent)]
    )
    result = subprocess.run(
        [
            sys.executable,
            # Apply the pytest warning filter to this separate interpreter
            "-W",
            "ignore:Couldn't find ffmpeg or avconv:RuntimeWarning:pydub.utils",
            "-c",
            "from scinoephile.cli.scinoephile_cli import ScinoephileCli; "
            "ScinoephileCli.main()",
            *arguments,
        ],
        cwd=package_root.parent,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert all(fragment in result.stdout for fragment in expected)
    assert result.stderr == ""
