#!/usr/bin/python

# Modules
from scinoephile import StdoutLogger, SubtitleDataset
from scinoephile.ocr import ImageSubtitleDataset
from scinoephile.ocr import OCRDataset
from scinoephile.ocr import TestOCRDataset
from scinoephile.ocr import LabeledOCRDataset
from scinoephile.ocr import TrainOCRDataset
from scinoephile.ocr import Model
from scinoephile.ocr import AutoTrainer
from os.path import isfile
from IPython import embed

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
def test1(movie, language, mode):
    kwargs = {"interactive": False, "mode": mode, "verbosity": 2}
    sup_file = f"{data_root}/{movie}/{language}.sup"
    h5_file = f"{data_root}/{movie}/{language}_{mode.replace(' ','')}.h5"
    png_file = f"{data_root}/{movie}/{language}_{mode.replace(' ','')}/"

    sub_ds = ImageSubtitleDataset(infile=sup_file, outfile=h5_file, **kwargs)
    sub_ds.load()
    sub_ds.save()
    sub_ds = ImageSubtitleDataset(infile=h5_file, outfile=png_file, **kwargs)
    sub_ds.load()
    sub_ds.save()


# test1("magnificent_mcdull", "cmn-Hans", "8 bit")
# test1("magnificent_mcdull", "cmn-Hans", "1 bit")
# Traditional fails in 8 bit mode; cannot handle overlapping Western characters
# test1("magnificent_mcdull", "cmn-Hant", "1 bit")

# test1("mcdull_kung_fu_ding_ding_dong", "cmn-Hans", "8 bit")
# test1("mcdull_kung_fu_ding_ding_dong", "cmn-Hans", "1 bit")
# Traditional fails; cannot handle overlapping Western characters

# test1("mcdull_prince_de_la_bun", "cmn-Hans", "8 bit")
# test1("mcdull_prince_de_la_bun", "cmn-Hans", "1 bit")
# Traditional fails in 8 bit mode; cannot handle overlapping Western characters
# test1("mcdull_prince_de_la_bun", "cmn-Hant", "1 bit")


# Test generating training dataset
def test2(n_chars, n_images, mode):
    kwargs = {"interactive": False, "mode": mode, "n_chars": n_chars, "verbosity": 1}
    trn_file = f"{data_root}/trn/{n_chars:05d}_{n_images:05d}_{mode.replace(' ','')}.h5"

    trn_ds = TrainOCRDataset(infile=trn_file, outfile=trn_file, **kwargs)
    if isfile(trn_file):
        trn_ds.load()
    trn_ds.generate_training_data(min_images=n_images)
    trn_ds.save()

    return trn_ds


# Test model training
def test3(n_chars, n_images, mode):
    kwargs = {"interactive": False, "mode": mode, "n_chars": n_chars, "verbosity": 1}
    mod_file = f"{data_root}/model/{n_chars:05d}_{n_images:05d}_{mode.replace(' ','')}.h5"
    log_file = f"{data_root}/model/{n_chars:05d}_{n_images:05d}_{mode.replace(' ','')}.log"

    trn_ds = test2(n_chars, n_images, mode)

    model = Model(infile=mod_file, outfile=mod_file, **kwargs)
    if isfile(mod_file):
        model.load()
    else:
        model.build()
    model.compile()
    with StdoutLogger(log_file, "w"):
        AutoTrainer(model=model, trn_ds=trn_ds, val_portion=0.1,
                    batch_size=256, epochs=10, **kwargs)()


# for n_chars in [100, 200]:
#     for n_images in [100, 200]:
#         for mode in ["1 bit", "8 bit"]:
#             mod_file = f"{data_root}/model/{n_chars:05d}_{n_images:05d}_{mode.replace(' ','')}.h5"
#             if not isfile(mod_file):
#                 test3(n_chars, n_images, mode)

# Test reconstruction
def test4(movie, language, n_chars, n_images, mode, calculate_accuracy=False):
    kwargs = {"interactive": False, "mode": mode, "n_chars": n_chars, "verbosity": 2}
    h5_file = f"{data_root}/{movie}/{language}_{mode.replace(' ','')}.h5"
    srt_file = f"{data_root}/{movie}/{language}_{mode.replace(' ','')}.srt"
    mod_file = f"{data_root}/model/{n_chars:05d}_{n_images:05d}_{mode.replace(' ','')}.h5"

    sub_ds = ImageSubtitleDataset(infile=h5_file, **kwargs)
    sub_ds.load()
    model = Model(infile=mod_file, **kwargs)
    model.load()
    sub_ds.subtitles.predict(model)
    sub_ds.subtitles.reconstruct_text()
    sub_ds.save(srt_file)
    if calculate_accuracy:
        std_file = f"{data_root}/{movie}/standard.srt"
        sub_ds.subtitles.calculate_accuracy(std_file, n_chars)


# test4("magnificent_mcdull", "cmn-Hans", 100, 100, "8 bit")
# test4("magnificent_mcdull", "cmn-Hans", 100, 100, "1 bit")
# test4("mcdull_kung_fu_ding_ding_dong", "cmn-Hans", 100, 100, "8 bit")
# test4("mcdull_kung_fu_ding_ding_dong", "cmn-Hans", 100, 100, "1 bit")
test4("mcdull_prince_de_la_bun", "cmn-Hans", 200, 100, "8 bit", True)
# test4("mcdull_prince_de_la_bun", "cmn-Hans", 100, 100, "1 bit", True)

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
