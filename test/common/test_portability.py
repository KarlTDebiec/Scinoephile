#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Verify common works under a different project without the original package."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

from common import package_root


def test_common_runs_in_another_project(tmp_path: Path):
    """Import every copied module without access to the original project.

    Arguments:
        tmp_path: directory for the unrelated host project
    """
    host_dir_path = tmp_path / "portable_project"
    host_dir_path.mkdir()
    (host_dir_path / "__init__.py").write_text("", encoding="utf-8")
    shutil.copytree(
        package_root / "common",
        host_dir_path / "common",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    code = dedent(
        """
        import importlib
        import importlib.util
        import pkgutil
        import sys
        from pathlib import Path

        sys.path.insert(0, sys.argv[1])
        assert importlib.util.find_spec("common") is None

        import portable_project.common as common
        for module in pkgutil.walk_packages(common.__path__, f"{common.__name__}."):
            importlib.import_module(module.name)

        from portable_project.common.cli import CommandLineInterface
        from portable_project.common.cli.argument_parsing import float_arg

        assert common.package_root == Path(sys.argv[1]) / "portable_project"
        assert CommandLineInterface.__module__ == (
            "portable_project.common.cli.command_line_interface"
        )
        assert CommandLineInterface.argparser().parse_args([]).log_file is None
        assert float_arg(min_value=0)("1.5") == 1.5
        assert "common" not in sys.modules
        """
    )
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", code, str(tmp_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
