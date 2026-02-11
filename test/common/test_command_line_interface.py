#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.command_line_interface."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import getLogger
from typing import TYPE_CHECKING, TypedDict, Unpack
from unittest.mock import patch

import pytest
from common.command_line_interface import (  # ty:ignore[unresolved-import]
    CommandLineInterface,
)

if TYPE_CHECKING:
    from pathlib import Path


class CliTestKwargs(TypedDict, total=False):
    """Keyword arguments for TestCli _main method."""

    pass


class TestCli(CommandLineInterface):
    """Test CLI implementation.

    This is a test CLI implementation with a detailed description.
    It has multiple sentences to test the help method.
    """

    @classmethod
    def _main(cls, **kwargs: Unpack[CliTestKwargs]):
        """Execute test CLI."""
        pass


class TestCliWithoutDoc(CommandLineInterface):
    """Test CLI without detailed documentation."""

    @classmethod
    def _main(cls, **kwargs: Unpack[CliTestKwargs]):
        """Execute test CLI."""
        pass


class AnotherTestCli(CommandLineInterface):
    """Another test CLI."""

    @classmethod
    def _main(cls, **kwargs: Unpack[CliTestKwargs]):
        """Execute test CLI."""
        pass


def test_name():
    """Test name() class method."""
    assert TestCli.name() == "test"


def test_name_with_cli_suffix():
    """Test name() strips 'Cli' suffix."""
    assert TestCli.name() == "test"


def test_name_without_cli_suffix():
    """Test name() with class name ending in 'Cli'."""
    # AnotherTestCli ends with 'Cli', so it gets stripped
    assert AnotherTestCli.name() == "anothertest"


def test_description():
    """Test description() class method."""
    desc = TestCli.description()
    assert "This is a test CLI implementation" in desc
    assert "It has multiple sentences" in desc


def test_description_no_docstring():
    """Test description() with no docstring."""

    class NoDocCli(CommandLineInterface):
        @classmethod
        def _main(cls, **kwargs: Unpack[CliTestKwargs]):
            """Execute test CLI."""
            pass

    assert NoDocCli.description() == ""


def test_help():
    """Test help() class method."""
    help_text = TestCli.help()
    # Should return first sentence with first letter lowercased
    assert help_text == "test CLI implementation"
    assert not help_text.endswith(".")


def test_help_single_sentence():
    """Test help() with single sentence description."""
    help_text = TestCliWithoutDoc.help()
    assert help_text == "test CLI without detailed documentation"


def test_add_arguments_to_argparser():
    """Test add_arguments_to_argparser() adds expected arguments."""
    parser = ArgumentParser()
    TestCli.add_arguments_to_argparser(parser)

    # Parse with verbose flag
    args = parser.parse_args(["-v"])
    assert args.verbosity == 2  # default is 1, -v increments

    # Parse with quiet flag
    args = parser.parse_args(["-q"])
    assert args.verbosity == 0

    # Parse with multiple verbose flags
    args = parser.parse_args(["-vv"])
    assert args.verbosity == 3

    # Parse with log file
    args = parser.parse_args(["-l", "test.log"])
    assert args.log_file == "test.log"

    # Parse with log file using default
    args = parser.parse_args(["-l"])
    assert args.log_file is not None
    assert args.log_file.endswith(".log")


def test_argparser_without_subparsers():
    """Test argparser() creates new ArgumentParser."""
    parser = TestCli.argparser()

    assert isinstance(parser, ArgumentParser)
    assert TestCli.description() in parser.format_help()


def test_argparser_with_subparsers():
    """Test argparser() with subparsers."""
    main_parser = ArgumentParser()
    subparsers = main_parser.add_subparsers()

    parser = TestCli.argparser(subparsers=subparsers)

    assert isinstance(parser, ArgumentParser)


def test_log_command_line():
    """Test log_command_line() logs the command line."""
    with patch("common.command_line_interface.argv", ["script.py", "arg1", "arg2"]):
        with patch("common.command_line_interface.logger.info") as mock_info:
            TestCli.log_command_line()
            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "script.py arg1 arg2" in call_args


def test_main_basic():
    """Test main() method basic execution."""
    with patch.object(TestCli, "_main") as mock_main:
        with patch("sys.argv", ["test_script.py"]):
            TestCli.main()
            mock_main.assert_called_once()


def test_main_with_verbosity():
    """Test main() method handles verbosity."""
    with patch.object(TestCli, "_main") as mock_main:
        with patch("sys.argv", ["test_script.py", "-v"]):
            TestCli.main()
            mock_main.assert_called_once()
            # Verbosity should not be passed to _main
            call_kwargs = mock_main.call_args[1]
            assert "verbosity" not in call_kwargs


def test_main_with_log_file(tmp_path: Path):
    """Test main() method handles log file."""
    log_file = tmp_path / "test.log"

    with patch.object(TestCli, "_main") as mock_main:
        with patch("sys.argv", ["test_script.py", "-l", str(log_file)]):
            TestCli.main()
            mock_main.assert_called_once()
            # Log file should be created
            assert log_file.exists()


def test_main_clears_handlers():
    """Test main() clears existing logger handlers."""
    logger = getLogger()

    with patch.object(TestCli, "_main"):
        with patch("sys.argv", ["test_script.py"]):
            TestCli.main()

    # Logger should have handlers managed
    assert logger.handlers is not None


def test_abstract_main():
    """Test that _main is abstract and must be implemented."""
    with pytest.raises(TypeError):
        # Cannot instantiate ABC without implementing abstract method
        CommandLineInterface()
