#!python
#   scinoephile.testing.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################## MODULES ###################################
from hashlib import md5
from os import devnull
from subprocess import PIPE, Popen


################################## FUNCTIONS ##################################
def cmp_h5(file_1, file_2):
    """
    Checks if two hdf5 files contain the same data

    Args:
        file_1 (str): Path to first hdf5 file
        file_2 (str): Path to second hdf5 file

    Returns:
        bool: True if the files are identical, false otherwise
    """
    with open(devnull, "w") as fnull:
        output = Popen(f"h5diff {file_1} {file_2}", stdout=PIPE,
                       stderr=fnull, shell=True).stdout.read().decode("utf-8")

    if output == "":
        return True
    else:
        return False


def get_md5(x):
    """
    Calculates the md5 hash of a provided value

    Args:
        x (object): value(s) for which to calculate md5, if list, values
          will be joined by '_'

    Returns:
        str: 32-character hexadecimal digest of md5 hash
    """
    if isinstance(x, list):
        return md5("_".join(map(str, x)).encode("utf-8")).hexdigest()
    else:
        return md5(str(x).encode("utf-8")).hexdigest()
