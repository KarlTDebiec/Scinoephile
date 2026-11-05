#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of logging arguments across the installed CLI command hierarchy."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pytest import CaptureFixture, MonkeyPatch, raises

from scinoephile.cli.media.media_probe_cli import MediaProbeCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.core.cli.scinoephile_cli_base import ScinoephileCliBase
from test.helpers import parametrize


@parametrize(
    ("root_arguments", "middle_arguments", "leaf_arguments", "verbosity", "log_file"),
    [
        ([], [], [], 1, None),
        (["-v"], [], [], 2, None),
        (["-vv"], [], [], 3, None),
        (["--quiet"], [], [], 0, None),
        ([], ["--verbose"], [], 2, None),
        ([], ["-vv"], [], 3, None),
        ([], ["-q"], [], 0, None),
        (["-vv"], ["-v"], [], 2, None),
        (["-q"], ["-vv"], [], 3, None),
        (["-vv"], [], ["-q"], 0, None),
        (["-q"], ["-vv"], ["-v"], 2, None),
        (["-v"], ["-q"], ["-vv"], 3, None),
        (["-l", "root.log"], [], [], 1, "root.log"),
        ([], ["--log-file", "middle.log"], [], 1, "middle.log"),
        (["-l", "root.log"], ["-l", "middle.log"], [], 1, "middle.log"),
        (["-l", "root.log"], ["-l", "middle.log"], ["-l", "leaf.log"], 1, "leaf.log"),
    ],
)
def test_nested_logging_arguments(
    root_arguments: list[str],
    middle_arguments: list[str],
    leaf_arguments: list[str],
    verbosity: int,
    log_file: str | None,
    tmp_path: Path,
):
    """Preserve ancestor logging options until a descendant explicitly overrides them.

    Arguments:
        root_arguments: options before the top-level subcommand
        middle_arguments: options before the media subcommand
        leaf_arguments: options after the probe subcommand
        verbosity: expected selected verbosity
        log_file: expected selected log file
        tmp_path: temporary directory for the input file
    """
    infile_path = tmp_path / "input.mkv"
    infile_path.touch()
    parsed = ScinoephileCli.argparser().parse_args(
        [
            *root_arguments,
            "media",
            *middle_arguments,
            "probe",
            *leaf_arguments,
            "--infile",
            str(infile_path),
        ]
    )

    assert parsed.verbosity == verbosity
    assert parsed.log_file == log_file


def test_nested_logging_arguments_do_not_leak_between_parses(tmp_path: Path):
    """Reset parser state between calls without losing standalone leaf defaults.

    Arguments:
        tmp_path: temporary directory for the input file
    """
    infile_path = tmp_path / "input.mkv"
    infile_path.touch()
    parser = ScinoephileCli.argparser()
    arguments = ["media", "probe", "--infile", str(infile_path)]

    configured = parser.parse_args(["-vv", "-l", "root.log", *arguments])
    defaults = parser.parse_args(arguments)
    assert configured.verbosity == 3
    assert configured.log_file == "root.log"
    assert defaults.verbosity == 1
    assert defaults.log_file is None

    leaf_parser = MediaProbeCli.argparser()
    leaf_defaults = leaf_parser.parse_args(["--infile", str(infile_path)])
    leaf_configured = leaf_parser.parse_args(
        ["-vv", "-l", "leaf.log", "--infile", str(infile_path)]
    )
    assert leaf_defaults.verbosity == 1
    assert leaf_defaults.log_file is None
    assert leaf_configured.verbosity == 3
    assert leaf_configured.log_file == "leaf.log"


@parametrize(
    ("locale_name", "quiet_help"),
    [("zh-hans", "仅显示错误"), ("zh-hant", "僅顯示錯誤")],
)
def test_nested_logging_help_is_localized(
    locale_name: str,
    quiet_help: str,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
):
    """Keep translated logging help available after suppressing child defaults.

    Arguments:
        locale_name: locale used to construct the command hierarchy
        quiet_help: expected translated quiet-option help
        monkeypatch: fixture isolating the active CLI locale
        capsys: fixture capturing command help output
    """
    monkeypatch.setattr(ScinoephileCliBase, "locale_name", locale_name)
    parser = ScinoephileCli.argparser()

    for arguments in (["--help"], ["media", "--help"], ["media", "probe", "--help"]):
        with raises(SystemExit) as excinfo:
            parser.parse_args(arguments)
        assert excinfo.value.code == 0
        assert quiet_help in capsys.readouterr().out


def test_nested_main_uses_parent_logging_options(tmp_path: Path):
    """Create the requested ancestor log file before invoking a nested command.

    Arguments:
        tmp_path: temporary directory for input and log files
    """
    infile_path = tmp_path / "input.mkv"
    infile_path.touch()
    log_file_path = tmp_path / "root.log"
    with patch.object(MediaProbeCli, "_main") as mock_main:
        with patch(
            "scinoephile.common.cli.command_line_interface.configure_logging"
        ) as mock_logging:
            with patch(
                "scinoephile.common.cli.command_line_interface.getLogger"
            ) as mock_get_logger:
                mock_get_logger.return_value.level = 10
                ScinoephileCli.main(
                    [
                        "-vv",
                        "--log-file",
                        str(log_file_path),
                        "media",
                        "probe",
                        "--infile",
                        str(infile_path),
                    ]
                )
                file_handler = mock_get_logger.return_value.addHandler.call_args.args[0]
                file_handler.close()

    mock_logging.assert_called_once_with(3)
    mock_main.assert_called_once()
    assert log_file_path.is_file()
