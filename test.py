#!/usr/bin/python

# Modules
from scinoephile import SubtitleDataset
from scinoephile.ocr import ImageSubtitleDataset
from scinoephile.ocr import OCRDataset
from scinoephile.ocr import TestOCRDataset
from scinoephile.ocr import LabeledOCRDataset
from scinoephile.ocr import TrainOCRDataset
from scinoephile.ocr import Model
from scinoephile.ocr import AutoTrainer
from os.path import isfile

# Root paths and configuration
subtitle_root = "/Users/kdebiec/Dropbox/code/subtitles/"
data_root = "/Users/kdebiec/Desktop/subtitles/"


# Test reading and writing text subtitles
# kwargs = {"interactive": False, "verbosity": 1}
# SubtitleDataset(
#     infile=f"{subtitle_root}/youth/Youth.en-US.srt",
#     outfile=f"{subtitle_root}/youth/youth.hdf5",
#     **kwargs)()
# SubtitleDataset(
#     infile=f"{subtitle_root}/youth/youth.hdf5",
#     **kwargs)()

# Test reading and writing image-based subtitles
def test(movie, language, mode):
    kwargs = {"interactive": False, "mode": mode, "verbosity": 2}
    sup_file = f"{data_root}/{movie}/{language}.sup"
    h5_file = f"{data_root}/{movie}/{language}_{mode.replace(' ','')}.h5"
    png_file = f"{data_root}/{movie}/{language}_{mode.replace(' ','')}/"
    ImageSubtitleDataset(infile=sup_file, outfile=h5_file, **kwargs)()
    ImageSubtitleDataset(infile=h5_file, outfile=png_file, **kwargs)()

# test("magnificent_mcdull", "cmn-Hans", "8 bit")
# test("magnificent_mcdull", "cmn-Hans", "1 bit")
# test("mcdull_kung_fu_ding_ding_dong", "cmn-Hans", "8 bit")
# test("mcdull_kung_fu_ding_ding_dong", "cmn-Hans", "1 bit")
# test("mcdull_prince_de_la_bun", "cmn-Hans", "8 bit")
# test("mcdull_prince_de_la_bun", "cmn-Hans", "1 bit")

# Test generating training dataset in 8 bit mode
# kwargs = {"interactive": False, "mode": "8 bit", "n_chars": 100, "verbosity": 1}
# TrainOCRDataset(
#     infile=f"{data_root}/trn_8bit.h5",
#     outfile=f"{data_root}/trn_8bit.h5",
#     **kwargs)()

# Train model
# def test_training():
#    trn_ds = TrainOCRDataset(
#        infile=trn_file, outfile=trn_file, **kwargs)
#    if isfile(trn_file):
#        trn_ds.load()
#    trn_ds.generate_training_data(min_images=100)
#    trn_ds.save()
#    model = Model(
#        infile=model_file, outfile=model_file, **kwargs)
#    if isfile(model_file):
#        model.load()
#    else:
#        model.build()
#    model.compile()
#    AutoTrainer(
#        model=model,
#        trn_ds=trn_ds, val_portion=0.1,
#        batch_size=256, epochs=10,
#        interactive=False, **kwargs)()

# kwargs["n_chars"] = 200
# kwargs["mode"] = "8 bit"
# trn_file = f"{data_root}/trn_0200_0100_8bit.h5"
# model_file = f"{data_root}/model_0200_0100_8bit.h5"
# test_training()
# kwargs["mode"] = "1 bit"
# trn_file = f"{data_root}/trn_0200_0100_1bit.h5"
# model_file = f"{data_root}/model_0200_0100_1bit.h5"
# test_training()
#
# keras.callbacks.EarlyStopping(monitor="val_loss",
#                               min_delta=0.001,
#                               patience=10),
# keras.callbacks.ReduceLROnPlateau(monitor="acc",
#                                   patience=3,
#                                   verbose=1,
#                                   factor=0.1,
#                                   min_lr=0.000000001)]

# Gather test data
# def gather_test():
#    sub_ds = ImageSubtitleDataset(infile=trn_file, **kwargs)
#    sub_ds.load()
#    model = Model(infile=model_file, **kwargs)
#    model.load()
#    TestOCRDataset(model=model, sub_ds=sub_ds,
#                   infile=tst_file, outfile=tst_file,
#                   interactive=True, **kwargs)()

# kwargs["n_chars"] = 100
# kwargs["mode"] = "8 bit"
# model_file = f"{data_root}/model_0100_0100_8bit.h5"
# trn_file = f"{subtitle_root}/magnificent_mcdull/mcdull_8bit.h5"
# tst_file = f"{data_root}/tst_8bit.h5"
# gather_test()
# kwargs["mode"] = "1 bit"
# model_file = f"{data_root}/model_0100_0100_1bit.h5"
# trn_file = f"{subtitle_root}/magnificent_mcdull/mcdull_1bit.h5"
# tst_file = f"{data_root}/tst_1bit.h5"
# gather_test()

# Test reconstruction
# def reconstruct():
#     sub_ds = ImageSubtitleDataset(
#         infile=sub_file, interactive=False, **kwargs)
#     sub_ds()
#     model = Model(
#         infile=mod_file, **kwargs)
#     model.load()
#     embed()

# kwargs["n_chars"] = 100
# kwargs["mode"] = "8 bit"
# sub_file = f"{subtitle_root}/magnificent_mcdull/mcdull_8bit.h5"
# mod_file = f"{data_root}/model_0100_0100_8bit.h5"
# reconstruct()

# tst_file = f"{data_root}/tst_8bit.h5"
# trn_file = f"{data_root}/trn_0100_0100_8bit.h5"
# trn_ds = TrainOCRDataset(infile=trn_file, **kwargs)
# trn_ds.load()
# tst_ds = TestOCRDataset(infile=tst_file, **kwargs)
# tst_ds.load()
# tst_ds.calculate_diff(trn_ds=trn_ds)
