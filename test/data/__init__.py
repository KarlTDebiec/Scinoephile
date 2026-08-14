#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Data for tests.

Each directory corresponds to a set of test cases associated with a specific set of
subtitles. Each directory contains the following:
* `input` directory - authoritative input subtitle files
* `output` directory - processed output subtitle files
* `__init__.py` - test fixtures for the test cases in the directory
* a Python generation script - reads the input files and creates the output files
"""
