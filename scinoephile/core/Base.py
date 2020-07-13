#!/usr/bin/env python3
#   scinoephile.core.Base.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from abc import ABC
from inspect import currentframe, getframeinfo
from typing import Any, Dict

from scinoephile import package_root


################################### CLASSES ###################################
class Base(ABC):
    """Base including convenience methods and properties"""

    # region Builtins

    def __init__(self, verbosity: int = 1, **kwargs: Any) -> None:
        """
        Initializes class

        Args:
            verbosity (int): Level of verbose output
            kwargs (dict): Additional keyword arguments
        """

        # Store property values
        self.verbosity = verbosity

    # endregion

    # region Properties

    @property
    def embed_kw(self) -> Dict[str, str]:
        """Use ``IPython.embed(**self.embed_kw)`` for better prompt"""
        frame = currentframe()
        if frame is None:
            raise ValueError()
        frameinfo = getframeinfo(frame.f_back)
        file = frameinfo.filename.replace(package_root, "")
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
    def verbosity(self) -> int:
        """int: Level of output to provide"""
        if not hasattr(self, "_verbosity"):
            self._verbosity = 1
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value: int) -> None:
        if not isinstance(value, int) and value >= 0:
            raise ValueError(self._generate_setter_exception(value))
        self._verbosity = value

    # endregion

    # region Private methods

    def _generate_setter_exception(self, value: Any) -> str:
        """
        Generates Exception text for setters that are passed invalid values

        Returns:
            str: Exception text
        """
        frame = currentframe()
        if frame is None:
            raise ValueError()
        frameinfo = getframeinfo(frame.f_back)
        return f"Property '{type(self).__name__}.{frameinfo.function}' " \
               f"was passed invalid value '{value}' " \
               f"of type '{type(value).__name__}'. " \
               f"Expects '{getattr(type(self), frameinfo.function).__doc__}'."

    # endregion
