#!python
#   test_OCRRecognition.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from os.path import expandvars
from scinoephile.ocr import ImageSubtitleSeries
from scinoephile.ocr.recognition import (RecognitionTrainDataset,
                                         RecognitionTestDataset)

################################ CONFIGURATION ################################
input_dir = expandvars("$HOME/Desktop/subtitles/test/input")
output_dir = expandvars("$HOME/Desktop/subtitles/test/output/")


#################################### TESTS ####################################
def test_RecognitionTrainDataset(**kwargs):
    ds = RecognitionTrainDataset(**kwargs)
    ds.generate_training_data(min_images=20)
    ds.get_data_for_tensorflow()
    ds.get_data_for_tensorflow(val_portion=0)
    ds.save(f"{output_dir}/ocr/recognition_training.h5")

    ds = RecognitionTrainDataset.load(
        f"{output_dir}/ocr/recognition_training.h5")
    ds.show()


def test_RecognitionTestDataset(**kwargs):
    subs = ImageSubtitleSeries.load(
        f"{input_dir}/mcdull_prince_de_la_bun/cmn-Hans.h5", **kwargs)
    ds = RecognitionTestDataset(subtitle_series=subs, **kwargs)
    ds.get_data_for_tensorflow()
    ds.show()


#################################### MAIN #####################################
if __name__ == "__main__":
    test_RecognitionTrainDataset(verbosity=2)
    test_RecognitionTestDataset(verbosity=2)
