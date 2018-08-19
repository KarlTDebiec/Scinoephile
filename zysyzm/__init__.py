#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.__init__.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### CLASSES ###################################
class Base(object):
    """Base for all zysyzm classes"""

    # region Builtins

    def __init__(self, verbosity=1, **kwargs):
        """
        Initializes tool

        Args:
            verbosity (int): Level of verbose output
            interactive (bool): Show IPython prompt
            kwargs (dict): Additional keyword arguments
        """
        self.verbosity = verbosity

    # endregion

    # region Properties
    @property
    def embed_kw(self):
        """dict: """
        from inspect import currentframe, getframeinfo

        frameinfo = getframeinfo(currentframe().f_back)
        file = frameinfo.filename.replace(self.package_root, "")
        func = frameinfo.function
        number = frameinfo.lineno - 1
        if self.verbosity >= 1:
            header = f"IPython prompt in file {file}, function {func}," \
                     f" line {number}\n"
        if self.verbosity >= 2:
            header += "\n"
            with open(frameinfo.filename, "r") as infile:
                lines = [(i, line) for i, line in enumerate(infile)
                         if i in range(number - 6, number + 5)]
            for i, line in lines:
                header += f"{i:5d} {'>' if i == number else ' '} " \
                          f"{line.rstrip()}\n"

        return {"header": header}

    @property
    def package_root(self):
        """str: path to package root directory"""
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
            raise ValueError()
        self._verbosity = value

    # endregion


class CLToolBase(Base):
    """Base for zysyzm command line tools"""

    # region Instance Variables

    help_message = "Base for command line tools"

    # endregion

    # region Builtins

    def __init__(self, interactive=False, **kwargs):
        """
        Initializes tool

        Args:
            interactive (bool): Show IPython prompt
            kwargs (dict): Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.interactive = interactive

    def __call__(self):
        """ Core logic """

        if isinstance(self, CLToolBase):
            raise NotImplementedError("zysyzm.CLToolBase class is not to "
                                      "be used directly")
        else:
            raise NotImplementedError(f"{self.__class__.__name__}.__call__ "
                                      "method has not been implemented")

    # endregion

    # region Properties

    @property
    def interactive(self):
        """bool: Present IPython prompt after processing subtitles"""
        if not hasattr(self, "_interactive"):
            self._interactive = False
        return self._interactive

    @interactive.setter
    def interactive(self, value):
        if not isinstance(value, bool):
            raise ValueError()
        self._interactive = value

    # endregion Properties

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
            parser = argparse.ArgumentParser(description=cls.help_message)

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
        """ Parses and validates arguments, constructs and calls object """

        parser = cls.construct_argparser()
        args = parser.parse_args()
        cls.validate_args(parser, args)
        cls(**vars(args))()
