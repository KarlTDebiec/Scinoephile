#!python
#   scinoephile.core.cltools.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from argparse import ArgumentError
from os import R_OK, W_OK, access, getcwd
from os.path import dirname, expandvars, isfile


################################## FUNCTIONS ##################################
def infile_argument(value: str) -> str:
    value = expandvars(value)

    if not isfile(value):
        raise ArgumentError(f"infile '{value}' does not exist")
    elif not access(value, R_OK):
        raise ArgumentError(f"infile '{value}' cannot be read")

    return value


def outfile_argument(value: str) -> str:
    value = expandvars(value)

    if isfile(value):
        if not access(value, W_OK):
            raise ArgumentError(f"outfile '{value}' cannot be written")
    else:
        directory = dirname(value)
        if directory == "":
            directory = getcwd()
        if not access(directory, W_OK):
            raise ArgumentError(f"outfile '{value}' cannot be written")

    return value
