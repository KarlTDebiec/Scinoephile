#!/usr/bin/python

################################### MODULES ###################################
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
    # kwargs["n_chars"] = 100
    # trn_ds = GeneratedOCRDataset(
    #     infile="/Users/kdebiec/Desktop/docs/subtitles/trn_0100_0100.h5",
    #     outfile="/Users/kdebiec/Desktop/docs/subtitles/trn_0100_0100.h5",
    #     mode="8 bit", **kwargs)
    # trn_ds.load()
    # trn_ds.generate_images(min_images=100)
    # trn_ds.save()
    # AutoTrainer(
    #     model_infile=None,
    #     model_outfile="/Users/kdebiec/Desktop/docs/subtitles/model_0100_0100.h5",
    #     trn_ds=trn_ds, val_portion=0.1, batch_size=128, epochs=10,
    #     interactive=True, **kwargs)()

    # Gather test data
    kwargs["mode"] = "8 bit"
    kwargs["n_chars"] = 100
    sub_ds = ImageSubtitleDataset(
        infile=subtitle_root + "magnificent_mcdull/mcdull_8bit.h5",
        **kwargs)
    sub_ds.load()
    model = Model(
        infile="/Users/kdebiec/Desktop/docs/subtitles/model_0100_0100.h5",
        **kwargs)
    model.load()
    model.prepare_model()
    TestOCRDataset(model=model, sub_ds=sub_ds,
                   infile="/Users/kdebiec/Desktop/docs/subtitles/tst_0100_0100.h5",
                   outfile="/Users/kdebiec/Desktop/docs/subtitles/tst_0100_0100.h5",
                   interactive=True, **kwargs)()

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
