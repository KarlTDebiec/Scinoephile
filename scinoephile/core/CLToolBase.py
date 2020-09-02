#!/usr/bin/env python
#   scinoephile.core.CLToolBase.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from abc import ABC, abstractmethod
from argparse import (ArgumentParser, RawDescriptionHelpFormatter,
                      _SubParsersAction)
from typing import Any, Optional

import pandas as pd

from scinoephile.core.Base import Base


################################### CLASSES ###################################
class CLToolBase(Base, ABC):
    """Base for command line tools"""

    # region Builtins

    @abstractmethod
    def __call__(self) -> None:
        """ Core logic """
        pass

    # endregion

    # region Public Class Methods

    @classmethod
    def construct_argparser(cls, description: Optional[str] = None,
                            parser: Optional[ArgumentParser] = None,
                            **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser

        Returns:
            parser (ArgumentParser): Argument parser
        """
        if isinstance(parser, ArgumentParser):
            parser = parser
        elif isinstance(parser, _SubParsersAction):
            parser = parser.add_parser(
                name=cls.__name__.lower(),
                description=description,
                help=description,
                formatter_class=RawDescriptionHelpFormatter)
        elif parser is None:
            parser = ArgumentParser(
                description=description,
                formatter_class=RawDescriptionHelpFormatter)

        # General
        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument("-v", "--verbose",
                               action="count",
                               default=1,
                               dest="verbosity",
                               help="enable verbose output, may be specified "
                                    "more than once")
        verbosity.add_argument("-q", "--quiet",
                               action="store_const",
                               const=0,
                               dest="verbosity",
                               help="disable verbose output")

        return parser

    # endregion

    @classmethod
    def main(cls) -> None:
        """Parses and validates arguments, constructs and calls object"""
        pd.set_option("display.width", 110)
        pd.set_option("display.max_colwidth", 16)
        pd.set_option("display.max_rows", None)

        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())
        cls(**kwargs)()
