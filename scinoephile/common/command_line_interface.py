#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for command-line interfaces."""

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
from logging import FileHandler, basicConfig, getLogger, info
from pathlib import Path
from sys import argv
from typing import Any

from .logs import set_logging_verbosity


class CommandLineInterface(ABC):
    """Abstract base class for command-line interfaces."""

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

        # Stdout logging
        logger = getLogger()
        logger.handlers.clear()
        basicConfig()
        verbosity = kwargs.pop("verbosity", 1)
        set_logging_verbosity(verbosity)

        # File logging
        log_file = kwargs.pop("log_file")
        if log_file:
            log_file_path = Path(log_file).resolve()
            file_logger = FileHandler(log_file_path)
            logger.addHandler(file_logger)
            info(f"Logging to {log_file_path} at level {logger.level}")

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
        info(f"Run with command line: {command_line}")

    @classmethod
    @abstractmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments."""
        raise NotImplementedError()
