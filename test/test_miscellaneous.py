#!python
#   test_miscellaneous.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from os.path import expandvars
from scinoephile import embed_kw, in_ipython, StdoutLogger

################################ CONFIGURATION ################################
input_dir = expandvars("$HOME/Desktop/subtitles/test/input")
output_dir = expandvars("$HOME/Desktop/subtitles/test/output/")


#################################### TESTS ####################################
def test_miscellaneous(**kwargs):
    # Test standard output logger
    with StdoutLogger(f"{output_dir}/test_miscellaneous.log", "w", True):
        # Test IPython convenience functions
        print(embed_kw(verbosity=1))
        print(embed_kw(verbosity=2))
        print(in_ipython())


#################################### MAIN #####################################
if __name__ == "__main__":
    test_miscellaneous(verbosity=2)
