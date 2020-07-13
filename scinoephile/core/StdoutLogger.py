#!/usr/bin/env python3
#   scinoephile.core.StdoutLogger.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import io
import re
import sys
from shutil import copyfile
from tempfile import NamedTemporaryFile
from typing import Any


################################### CLASSES ###################################
class StdoutLogger():
    """Logs print statements to both stdout and file; use with 'with'"""

    # region Builtins

    def __init__(self, outfile: str, mode: str = "a",
                 process_carriage_returns: bool = True) -> None:
        self.process_carriage_returns = process_carriage_returns
        self.outfile = outfile
        self.mode = mode

    def __enter__(self) -> None:
        self.file = open(self.outfile, self.mode)
        self.stdout = sys.stdout
        sys.stdout = self

    def __exit__(self, _type: Any, _value: Any, _traceback: Any) -> None:
        sys.stdout = self.stdout
        self.file.close()

        if self.process_carriage_returns:
            with io.open(self.file.name, "r", newline="\n") as file:
                with NamedTemporaryFile("w") as temp:
                    for i, line in enumerate(file):
                        temp.write(re.sub("^.*\r", "", line))
                    temp.flush()
                    copyfile(temp.name, f"{file.name}")

    # endregion

    # region Public Methods

    def flush(self) -> None:
        self.file.flush()

    def write(self, text: str) -> None:
        self.file.write(text)
        self.stdout.write(text)

    # endregion
