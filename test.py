#!/usr/bin/python

################################### MODULES ###################################
from scinoephile import SubtitleDataset
from scinoephile.ocr import ImageSubtitleDataset

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
    ImageSubtitleDataset(
        infile=subtitle_root + "magnificent_mcdull/mcdull_1bit.h5",
        image_mode="1 bit", interactive=False, **kwargs)()
