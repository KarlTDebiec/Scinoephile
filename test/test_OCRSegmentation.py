#!python
#   test_OCRSegmentation.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from os.path import expandvars
from scinoephile.ocr.segmentation import (SegmentationTrainDataset,
                                          SegmentationTestDataset)

################################ CONFIGURATION ################################
input_dir = expandvars("$HOME/Desktop/subtitles/test/input")
output_dir = expandvars("$HOME/Desktop/subtitles/test/output/")


#################################### TESTS ####################################
def test_SegmentationTrainDataset(**kwargs):
    ds = SegmentationTrainDataset(**kwargs)


def test_SegmentationTestDataset(**kwargs):
    ds = SegmentationTestDataset(**kwargs)


#################################### MAIN #####################################
if __name__ == "__main__":
    test_SegmentationTrainDataset(verbosity=2)
    test_SegmentationTestDataset(verbosity=2)
