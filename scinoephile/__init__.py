#!/usr/bin/env python3
#   scinoephile.__init__.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from os.path import dirname
from sys import modules
from typing import List

################################## VARIABLES ##################################
package_root = dirname(modules[__name__].__file__)

##################################### ALL #####################################
__all__: List[str] = [
    "package_root",
]
