#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.__init__.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################## MODULES ###################################
from abc import ABC, abstractmethod
from IPython import embed


################################### CLASSES ###################################
class Base(ABC):
    """Base including convenience methods and properties"""

    # region Builtins

    def __init__(self, interactive=None, verbosity=None, **kwargs):
        """
        Initializes class

        Args:
            interactive (bool): Show IPython prompt
            verbosity (int): Level of verbose output
            kwargs (dict): Additional keyword arguments
        """

        # Store property values
        if interactive is not None:
            self.interactive = interactive
        if verbosity is not None:
            self.verbosity = verbosity

    # endregion

    # region Properties

    @property
    def embed_kw(self):
        """dict: use ``IPython.embed(**self.embed_kw)`` for more useful prompt"""
        from inspect import currentframe, getframeinfo

        frameinfo = getframeinfo(currentframe().f_back)
        file = frameinfo.filename.replace(self.package_root, "")
        func = frameinfo.function
        number = frameinfo.lineno - 1
        header = ""
        if self.verbosity >= 1:
            header = f"IPython prompt in file {file}, function {func}," \
                f" line {number}\n"
        if self.verbosity >= 2:
            header += "\n"
            with open(frameinfo.filename, "r") as infile:
                lines = [(i, line) for i, line in enumerate(infile)
                         if i in range(number - 5, number + 6)]
            for i, line in lines:
                header += f"{i:5d} {'>' if i == number else ' '} " \
                    f"{line.rstrip()}\n"

        return {"header": header}

    @property
    def interactive(self):
        """bool: present IPython prompt after processing subtitles"""
        if not hasattr(self, "_interactive"):
            self._interactive = False
        return self._interactive

    @interactive.setter
    def interactive(self, value):
        if not isinstance(value, bool):
            try:
                value = bool(value)
            except Exception:
                raise ValueError(self._generate_setter_exception(value))
        self._interactive = value

    @property
    def package_root(self):
        """str: Path to package root directory"""
        if not hasattr(self, "_package_root"):
            from os.path import dirname
            from sys import modules

            self._package_root = dirname(modules[__name__].__file__)
        return self._package_root

    @property
    def verbosity(self):
        """int: Level of output to provide"""
        if not hasattr(self, "_verbosity"):
            self._verbosity = 1
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value):
        if not isinstance(value, int) and value >= 0:
            raise ValueError(self._generate_setter_exception(value))
        self._verbosity = value

    # endregion

    # region Private methods

    def _generate_setter_exception(self, value):
        """
        Generates Exception text for setters that are passed invalid values

        Returns:
            str: Exception text
        """
        from inspect import currentframe, getframeinfo

        frameinfo = getframeinfo(currentframe().f_back)
        return f"Property '{type(self).__name__}.{frameinfo.function}' " \
            f"was passed invalid value '{value}' " \
            f"of type '{type(value).__name__}'. " \
            f"Expects '{getattr(type(self), frameinfo.function).__doc__}'."

    # endregion


class CLToolBase(Base, ABC):
    """Base for scinoephile command line tools"""

    # region Builtins

    @abstractmethod
    def __call__(self):
        """ Core logic """
        pass

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, parser=None):
        """
        Constructs argument parser

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        import argparse

        if parser is None:
            if hasattr(cls, "helptext"):
                description = cls.helptext
            else:
                try:
                    description = cls.__doc__.split("\n")[1].strip()
                except IndexError:
                    description = cls.__doc__
            parser = argparse.ArgumentParser(description=description)

        # General
        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument("-v", "--verbose", action="count",
                               dest="verbosity", default=1,
                               help="enable verbose output, may be specified "
                                    "more than once")
        verbosity.add_argument("-q", "--quiet", action="store_const",
                               dest="verbosity", const=0,
                               help="disable verbose output")
        parser.add_argument("-I", "--interactive", action="store_true",
                            dest="interactive",
                            help="present IPython prompt")

        return parser

    @classmethod
    def validate_args(cls, parser, args):
        """
        Validates arguments provided to an argument parser

        Args:
            parser (argparse.ArgumentParser): Argument parser
            args (argparse.Namespace): Arguments
        """
        pass

    # endregion

    @classmethod
    def main(cls):
        """Parses and validates arguments, constructs and calls object"""

        parser = cls.construct_argparser()
        args = parser.parse_args()
        cls.validate_args(parser, args)
        cls(**vars(args))()


class DatasetBase(Base, ABC):
    """Base for datasets"""

    # region Builtins

    def __init__(self, infile=None, outfile=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if infile is not None:
            self.infile = infile
        if outfile is not None:
            self.outfile = outfile

    def __call__(self):
        """ Core logic """

        # Input
        if self.infile is not None:
            self.load()

        # Present IPython prompt
        if self.interactive:
            embed(**self.embed_kw)

        # Output
        if self.outfile is not None:
            self.save()

    # endregion

    # region Public Properties

    @property
    def infile(self):
        """str: Path to input file"""
        if not hasattr(self, "_infile"):
            self._infile = None
        return self._infile

    @infile.setter
    def infile(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value).replace("//", "/")
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._infile = value

    @property
    def outfile(self):
        """str: Path to output file"""
        if not hasattr(self, "_outfile"):
            self._outfile = None
        return self._outfile

    @outfile.setter
    def outfile(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value).replace("//", "/")
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._outfile = value

    # endregion

    # region Public Methods

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def save(self):
        pass

    # endregion


class StdoutLogger(object):
    """Logs print statements to both stdout and file; use with 'with'"""

    # region Builtins

    def __init__(self, outfile, mode, process_carriage_returns=True):
        import sys

        self.process_carriage_returns = process_carriage_returns

        self.file = open(outfile, mode)
        self.stdout = sys.stdout
        sys.stdout = self

    def __enter__(self):
        pass

    def __exit__(self, _type, _value, _traceback):
        import sys

        sys.stdout = self.stdout
        self.file.close()

        if self.process_carriage_returns:
            from io import open
            from re import sub
            from shutil import copyfile
            from tempfile import NamedTemporaryFile

            with open(self.file.name, "r", newline="\n") as file:
                with NamedTemporaryFile("w") as temp:
                    for i, line in enumerate(file):
                        temp.write(sub("^.*\r", "", line))
                    temp.flush()
                    copyfile(temp.name, f"{file.name}")

    # endregion

    # region Public Methods

    def flush(self):
        self.file.flush()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    # endregion


################################### MODULES ###################################
from scinoephile.SubtitleEvent import SubtitleEvent
from scinoephile.SubtitleSeries import SubtitleSeries
