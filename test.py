#!/usr/bin/python

################################### MODULES ###################################
from scinoephile import SubtitleDataset
from scinoephile.ocr import ImageSubtitleDataset
from scinoephile.ocr import OCRDataset
from scinoephile.ocr import UnlabeledOCRDataset
from scinoephile.ocr import LabeledOCRDataset
from scinoephile.ocr import GeneratedOCRDataset

#################################### MAIN #####################################
if __name__ == "__main__":
    subtitle_root = "/Users/kdebiec/Dropbox/code/subtitles/"
    kwargs = {"verbosity": 2}

    # SubtitleDataset(
    #     infile=subtitle_root + "youth/Youth.en-US.srt",
    #     outfile=subtitle_root + "youth/youth.hdf5",
    #     **kwargs)()
    # SubtitleDataset(
    #     infile=subtitle_root + "youth/youth.hdf5",
    #     **kwargs)()

    # ImageSubtitleDataset(
    #     infile=subtitle_root + "magnificent_mcdull/original/Magnificent Mcdull.3.zho.sup",
    #     outfile=subtitle_root + "magnificent_mcdull/mcdull_8bit.h5",
    #     image_mode="8 bit", interactive=False, **kwargs)()
    # ImageSubtitleDataset(
    #     infile=subtitle_root + "magnificent_mcdull/mcdull_8bit.h5",
    #     image_mode="8 bit", interactive=False, **kwargs)()
    # ImageSubtitleDataset(
    #     infile=subtitle_root + "magnificent_mcdull/original/Magnificent Mcdull.3.zho.sup",
    #     outfile=subtitle_root + "magnificent_mcdull/mcdull_1bit.h5",
    #     image_mode="1 bit", interactive=False, **kwargs)()
    # ImageSubtitleDataset(
    #     infile=subtitle_root + "magnificent_mcdull/mcdull_1bit.h5",
    #     image_mode="1 bit", interactive=False, **kwargs)()

    GeneratedOCRDataset(
        infile="/Users/kdebiec/Desktop/docs/subtitles/trn.h5",
        outfile="/Users/kdebiec/Desktop/docs/subtitles/trn/",
        image_mode="1 bit", n_chars=50, interactive=True, **kwargs)()

    # UnlabeledOCRDataset(
    # self.input_image_dir = \
    #     "/Users/kdebiec/Desktop/docs/subtitles/magnificent_mcdull"
    # self.input_hdf5 = \
    #     "/Users/kdebiec/Desktop/docs/subtitles/magnificent_mcdull/unlabeled.h5"
    # self.output_hdf5 = \
    #     "/Users/kdebiec/Desktop/docs/subtitles/magnificent_mcdull/unlabeled.h5"
    # self.output_image_dir = \
    #     "/Users/kdebiec/Desktop/unlabeled"

    # LabeledOCRDataset(
    # self.input_image_dir = \
    #     "/Users/kdebiec/Desktop/docs/subtitles/tst"
    # self.input_hdf5 = \
    #     "/Users/kdebiec/Desktop/docs/subtitles/tst/labeled.h5"
    # self.output_hdf5 = \
    #     "/Users/kdebiec/Desktop/docs/subtitles/tst/labeled.h5"
    # self.output_image_dir = \
    #     "/Users/kdebiec/Desktop/labeled"
