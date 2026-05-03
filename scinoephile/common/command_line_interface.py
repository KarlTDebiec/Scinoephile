#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for command-line interfaces."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from argparse import (
    ArgumentParser,
    RawDescriptionHelpFormatter,
    _SubParsersAction,  # noqa pylint
)
from datetime import datetime
from inspect import cleandoc
from logging import FileHandler, Formatter, getLogger
from pathlib import Path
from sys import argv
from typing import Any, Unpack

from typing_extensions import TypedDict

from .logs import DEFAULT_LOG_FORMAT, configure_logging

__all__ = [
    "CLIKwargs",
    "CommandLineInterface",
]

logger = getLogger(__name__)


class CLIKwargs(TypedDict, total=False, extra_items=Any):
    """Keyword arguments for command-line interface _main methods."""

    _parser: ArgumentParser
    """Argument parser used for user-facing errors."""
    clean: bool
    """Whether to clean subtitles."""
    convert: Any
    """Conversion configuration."""
    flatten: bool
    """Whether to flatten subtitles."""
    infile: Any
    """Input file path."""
    interactive: bool
    """Whether to run interactively."""
    lens_infile: Any
    """Google Lens OCR input file path."""
    mode: str
    """Processing mode."""
    outfile: Any
    """Output file path."""
    overwrite: bool
    """Whether existing output files may be overwritten."""
    paddle_infile: Any
    """PaddleOCR input file path."""
    proofread: Any
    """Whether to proofread subtitles."""
    romanize: bool
    """Whether to romanize subtitles."""
    script: str
    """Requested written script."""
    stop_at_idx: int | None
    """Index at which to stop processing."""
    tesseract_infile: Any
    """Tesseract OCR input file path."""
    yue_infile: Any
    """Cantonese input file path."""
    zho_infile: Any
    """Standard Chinese input file path."""


class CommandLineInterface(ABC):
    """ABC for command-line interfaces."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=1,
            dest="verbosity",
            help="enable verbose output, may be specified more than once",
        )
        verbosity.add_argument(
            "-q",
            "--quiet",
            action="store_const",
            const=0,
            dest="verbosity",
            help="disable verbose output",
        )

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        parser.add_argument(
            "-l",
            "--log-file",
            nargs="?",
            const=f"{cls.name()}.{timestamp}.log",
            required=False,
            type=str,
            help="log to file (default: 'YYYY-MM-DD_hh-mm-ss.log')",
        )

    @classmethod
    def argparser(
        cls, *, subparsers: _SubParsersAction | None = None
    ) -> ArgumentParser:
        """Construct argument parser.

        Arguments:
            subparsers: Subparsers group to which a new subparser will be added; if
              None, a new ArgumentParser will be created
        Returns:
            Argument parser
        """
        if not subparsers:
            parser = ArgumentParser(
                description=str(cls.description()),
                formatter_class=RawDescriptionHelpFormatter,
            )
        else:
            parser = subparsers.add_parser(
                name=cls.name(),
                description=cls.description(),
                help=cls.help(),
                formatter_class=RawDescriptionHelpFormatter,
            )

        cls.add_arguments_to_argparser(parser)

        return parser

    @classmethod
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        return cleandoc(cls.__doc__) if cls.__doc__ else ""

    @classmethod
    def help(cls) -> str:
        """Short description of this tool used when it is a subparser."""
        text = re.split(r"\.\s+", str(cls.description()))[0].rstrip(".")
        return text[0].lower() + text[1:]

    @classmethod
    def main(cls):
        """Execute from command line."""
        parser = cls.argparser()
        kwargs = vars(parser.parse_args())

        # Configure logging
        verbosity = kwargs.pop("verbosity", 1)
        configure_logging(verbosity)

        # File logging
        log_file = kwargs.pop("log_file")
        if log_file:
            log_file_path = Path(log_file).resolve()
            file_handler = FileHandler(log_file_path)
            file_handler.setLevel(getLogger().level)
            formatter = Formatter(DEFAULT_LOG_FORMAT)
            file_handler.setFormatter(formatter)
            getLogger().addHandler(file_handler)
            logger.info(f"Logging to {log_file_path} at level {getLogger().level}")

        cls._main(**kwargs)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        name = cls.__name__
        if name.endswith("Cli"):
            name = name[:-3]
        return name.lower()

    @staticmethod
    def log_command_line():
        """Log the command line with which the script was run."""
        args = argv[:]
        command_line = " ".join(args)
        logger.info(f"Run with command line: {command_line}")

    @classmethod
    @abstractmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments."""
        raise NotImplementedError()
