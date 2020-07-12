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
from datetime import datetime
from os import R_OK, W_OK, access, getcwd
from os.path import dirname, expandvars, isfile
from typing import re

import dateutil


################################## FUNCTIONS ##################################
def infile_argument(value: str) -> str:
    if not isinstance(value, str):
        raise ArgumentError()

    value = expandvars(value)
    if not isfile(value):
        raise ArgumentError(f"infile '{value}' does not exist")
    elif not access(value, R_OK):
        raise ArgumentError(f"infile '{value}' cannot be read")

    return value


def outfile_argument(value: str) -> str:
    if not isinstance(value, str):
        raise ArgumentError()

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


def date_argument(value: str) -> datetime:
    if not isinstance(value, str):
        raise ArgumentError()

    try:
        date = dateutil.parser.parse(value)
    except ValueError:
        raise ArgumentError(f"date '{value}' cannot be parsed")

    return date


def string_or_infile_argument(value: str) -> str:
    if not isinstance(value, str):
        raise ArgumentError()

    value = expandvars(value)
    if isfile(value):
        if not access(value, R_OK):
            raise ArgumentError(f"infile '{value}' exists but cannot be read")
        with open(value, "r") as file:
            value = re.sub(r"\s+", " ", file.read()).strip()

    return value
