#!/usr/bin/python

################################### MODULES ###################################
from os.path import isfile
from scinoephile import SubtitleDataset
from scinoephile.ocr import ImageSubtitleDataset
from scinoephile.ocr import OCRDataset
from scinoephile.ocr import UnlabeledOCRDataset
from scinoephile.ocr import TestOCRDataset
from scinoephile.ocr import LabeledOCRDataset
from scinoephile.ocr import GeneratedOCRDataset
from scinoephile.ocr import Model
from scinoephile.ocr import AutoTrainer

#################################### MAIN #####################################
if __name__ == "__main__":
    subtitle_root = "/Users/kdebiec/Dropbox/code/subtitles/"
    kwargs = {"verbosity": 2}

    # Read text subtitles
    # SubtitleDataset(
    #     infile=subtitle_root + "youth/Youth.en-US.srt",
    #     outfile=subtitle_root + "youth/youth.hdf5",
    #     **kwargs)()
    # SubtitleDataset(
    #     infile=subtitle_root + "youth/youth.hdf5",
    #     **kwargs)()

    # Read image-based subtitles
    # ImageSubtitleDataset(
    #     infile=subtitle_root + "magnificent_mcdull/original/Magnificent Mcdull.3.zho.sup",
    #     outfile=subtitle_root + "magnificent_mcdull/mcdull_8bit.h5",
    #     mode="8 bit", interactive=False, **kwargs)()
    # ImageSubtitleDataset(
    #     infile=subtitle_root + "magnificent_mcdull/mcdull_8bit.h5",
    #     mode="8 bit", interactive=False, **kwargs)()
    # ImageSubtitleDataset(
    #     infile=subtitle_root + "magnificent_mcdull/original/Magnificent Mcdull.3.zho.sup",
    #     outfile=subtitle_root + "magnificent_mcdull/mcdull_1bit.h5",
    #     mode="1 bit", interactive=False, **kwargs)()
    # ImageSubtitleDataset(
    #     infile=subtitle_root + "magnificent_mcdull/mcdull_1bit.h5",
    #     mode="1 bit", interactive=False, **kwargs)()

    # Generate training data
    # GeneratedOCRDataset(
    #     infile="/Users/kdebiec/Desktop/docs/subtitles/trn.h5",
    #     outfile="/Users/kdebiec/Desktop/docs/subtitles/trn.h5",
    #     mode="1 bit", n_chars=10, interactive=False, **kwargs)()

    # Train model
    kwargs["n_chars"] = 200
    trn_file = "/Users/kdebiec/Desktop/docs/subtitles/trn_0200_0100.h5"
    model_file = "/Users/kdebiec/Desktop/docs/subtitles/model_0200_0100.h5"

    trn_ds = GeneratedOCRDataset(
        infile=trn_file, outfile=trn_file, mode="8 bit", **kwargs)
    if isfile(trn_file):
        trn_ds.load()
    trn_ds.generate_images(min_images=100)
    trn_ds.save()
    model = Model(
        infile=model_file, outfile=model_file, **kwargs)
    if isfile(model_file):
        model.load()
    else:
        model.build()
    model.compile()
    AutoTrainer(
        model=model,
        trn_ds=trn_ds, val_portion=0.1,
        batch_size=256, epochs=10,
        interactive=True, **kwargs)()

    # keras.callbacks.EarlyStopping(monitor="val_loss",
    #                               min_delta=0.001,
    #                               patience=10),
    # keras.callbacks.ReduceLROnPlateau(monitor="acc",
    #                                   patience=3,
    #                                   verbose=1,
    #                                   factor=0.1,
    #                                   min_lr=0.000000001)]

    # Gather test data
    # kwargs["mode"] = "8 bit"
    # kwargs["n_chars"] = 200
    # sub_ds = ImageSubtitleDataset(
    #     infile=subtitle_root + "magnificent_mcdull/mcdull_8bit.h5",
    #     **kwargs)
    # sub_ds.load()
    # model = Model(
    #     infile="/Users/kdebiec/Desktop/docs/subtitles/model_0200_0100.h5",
    #     **kwargs)
    # model.load()
    # TestOCRDataset(model=model, sub_ds=sub_ds,
    #                infile="/Users/kdebiec/Desktop/docs/subtitles/tst.h5",
    #                outfile="/Users/kdebiec/Desktop/docs/subtitles/tst.h5",
    #                interactive=True, **kwargs)()
