#!/usr/bin/python

################################### MODULES ###################################
from scinoephile import SubtitleDataset
from scinoephile.ocr import ImageSubtitleDataset
from scinoephile.ocr import OCRDataset
from scinoephile.ocr import TestOCRDataset
from scinoephile.ocr import LabeledOCRDataset
from scinoephile.ocr import TrainOCRDataset
from scinoephile.ocr import Model
from scinoephile.ocr import AutoTrainer
from os.path import isfile
from IPython import embed

#################################### MAIN #####################################
if __name__ == "__main__":
    subtitle_root = "/Users/kdebiec/Dropbox/code/subtitles/"
    data_root = "/Users/kdebiec/Desktop/docs/subtitles/"
    kwargs = {"verbosity": 2}


    # Read and write text subtitles
    # SubtitleDataset(
    #     infile=f"{subtitle_root}/youth/Youth.en-US.srt",
    #     outfile=f"{subtitle_root}/youth/youth.hdf5",
    #     interactive=False, **kwargs)()
    # SubtitleDataset(
    #     infile=f"{subtitle_root}/youth/youth.hdf5",
    #     interactive=False, **kwargs)()

    # Read and write image-based subtitles
    # ImageSubtitleDataset(
    #     infile=f"{subtitle_root}/magnificent_mcdull/original/Magnificent Mcdull.3.zho.sup",
    #     outfile=f"{subtitle_root}/magnificent_mcdull/mcdull_8bit.h5",
    #     mode="8 bit", interactive=False, **kwargs)()
    # ImageSubtitleDataset(
    #     infile=f"{subtitle_root}/magnificent_mcdull/mcdull_8bit.h5",
    #     mode="8 bit", interactive=False, **kwargs)()
    # ImageSubtitleDataset(
    #     infile=f"{subtitle_root}/magnificent_mcdull/original/Magnificent Mcdull.3.zho.sup",
    #     outfile=f"{subtitle_root}/magnificent_mcdull/mcdull_1bit.h5",
    #     mode="1 bit", interactive=False, **kwargs)()
    # ImageSubtitleDataset(
    #     infile=f"{subtitle_root}/magnificent_mcdull/mcdull_1bit.h5",
    #     mode="1 bit", interactive=True, **kwargs)()

    # Generate training data
    # kwargs["n_chars"] = 100
    # TrainOCRDataset(
    #     infile=f"{data_root}/trn_8bit.h5",
    #     outfile=f"{data_root}/trn_8bit.h5",
    #     mode="8 bit", interactive=False, **kwargs)()
    # TrainOCRDataset(
    #     infile=f"{data_root}/trn_1bit.h5",
    #     outfile=f"{data_root}/trn_1bit.h5",
    #     mode="1 bit", interactive=False, **kwargs)()

    # Train model
    def test_training():
        trn_ds = TrainOCRDataset(
            infile=trn_file, outfile=trn_file, **kwargs)
        if isfile(trn_file):
            trn_ds.load()
        trn_ds.generate_training_data(min_images=100)
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


    # kwargs["n_chars"] = 100
    # kwargs["mode"] = "8 bit"
    # trn_file = f"{data_root}/trn_0100_0100_8bit.h5"
    # model_file = f"{data_root}/model_0100_0100_8bit.h5"
    # test_training()
    # kwargs["mode"] = "1 bit"
    # trn_file = f"{data_root}/trn_0100_0100_1bit.h5"
    # model_file = f"{data_root}/model_0100_0100_1bit.h5"
    # test_training()

    # keras.callbacks.EarlyStopping(monitor="val_loss",
    #                               min_delta=0.001,
    #                               patience=10),
    # keras.callbacks.ReduceLROnPlateau(monitor="acc",
    #                                   patience=3,
    #                                   verbose=1,
    #                                   factor=0.1,
    #                                   min_lr=0.000000001)]

    # Gather test data
    def gather_test():
        sub_ds = ImageSubtitleDataset(infile=trn_file, **kwargs)
        sub_ds.load()
        model = Model(infile=model_file, **kwargs)
        model.load()
        TestOCRDataset(model=model, sub_ds=sub_ds,
                       infile=tst_file, outfile=tst_file,
                       interactive=True, **kwargs)()


    kwargs["n_chars"] = 100
    # kwargs["mode"] = "8 bit"
    # model_file = f"{data_root}/model_0100_0100_8bit.h5"
    # trn_file = f"{subtitle_root}/magnificent_mcdull/mcdull_8bit.h5"
    # tst_file = f"{data_root}/tst_8bit.h5"
    # gather_test()
    kwargs["mode"] = "1 bit"
    model_file = f"{data_root}/model_0100_0100_1bit.h5"
    trn_file = f"{subtitle_root}/magnificent_mcdull/mcdull_1bit.h5"
    tst_file = f"{data_root}/tst_1bit.h5"
    gather_test()