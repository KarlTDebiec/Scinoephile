#################################### TESTS #####################################
# test1("magnificent_madame_mak", "cmn-Hans", "8 bit")
# test1("magnificent_madame_mak", "cmn-Hans", "1 bit")
# test1("magnificent_madame_mak", "cmn-Hant", "8 bit")  # Fails to split
# test1("magnificent_madame_mak", "cmn-Hant", "1 bit")

# test1("mcdull_kung_fu_ding_ding_dong", "cmn-Hans", "8 bit")
# test1("mcdull_kung_fu_ding_ding_dong", "cmn-Hans", "1 bit")
# test1("mcdull_kung_fu_ding_ding_dong", "cmn-Hant", "8 bit")  # Fails to split
# test1("mcdull_kung_fu_ding_ding_dong", "cmn-Hant", "1 bit")  # Fails to split

# test1("mcdull_me_and_my_mum", "cmn-Hans", "8 bit")  # Fails to split
# test1("mcdull_me_and_my_mum", "cmn-Hans", "1 bit")  # Fails to split
# test1("mcdull_me_and_my_mum", "cmn-Hant", "8 bit")  # Fails to split
# test1("mcdull_me_and_my_mum", "cmn-Hant", "1 bit")  # Fails to split

# test1("mcdull_prince_de_la_bun", "cmn-Hans", "8 bit")
# test1("mcdull_prince_de_la_bun", "cmn-Hans", "1 bit")
# test1("mcdull_prince_de_la_bun", "cmn-Hant", "8 bit")  # Fails to split
# test1("mcdull_prince_de_la_bun", "cmn-Hant", "1 bit")

# test1("mcdull_rise_of_the_rice_cooker", "cmn-Hans", "8 bit")  # Bad sup?
# test1("mcdull_rise_of_the_rice_cooker", "cmn-Hans", "1 bit")  # Bad sup?
# test1("mcdull_rise_of_the_rice_cooker", "cmn-Hant", "8 bit")  # Bad sup?
# test1("mcdull_rise_of_the_rice_cooker", "cmn-Hant", "1 bit")  # Bad sup?

# test1("mcdull_the_pork_of_music", "cmn-Hant", "8 bit")  # Fails to split
# test1("mcdull_the_pork_of_music", "cmn-Hant", "1 bit")  # Fails to split

# test1("my_life_as_mcdull", "cmn-Hans", "8 bit")
# test1("my_life_as_mcdull", "cmn-Hans", "1 bit")
# test1("my_life_as_mcdull", "cmn-Hant", "8 bit")  # Fails to split
# test1("my_life_as_mcdull", "cmn-Hant", "1 bit")  # Fails to split


# Test model training
# def test3(n_chars, n_images, mode):
#     kwargs = {"interactive": False, "mode": mode, "n_chars": n_chars, "verbosity": 1}
#     mod_file = f"{data_root}/model/{n_chars:05d}_{n_images:05d}_{mode.replace(' ', '')}.h5"
#     log_file = f"{data_root}/model/{n_chars:05d}_{n_images:05d}_{mode.replace(' ', '')}.log"
#
#     model = Model(infile=mod_file, outfile=mod_file, **kwargs)
#     if isfile(mod_file):
#         model.load()
#     else:
#         model.build()
#         model.compile()
#         trn_ds = test2(n_chars, n_images, mode)
#         with StdoutLogger(log_file, "w"):
#             from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
#
#             callbacks = [ReduceLROnPlateau(monitor="val_loss", min_delta=0.01,
#                                            patience=3, factor=0.2, min_lr=0.001,
#                                            verbose=1),
#                          EarlyStopping(monitor="val_loss", min_delta=0.01,
#                                        patience=5, verbose=1)]
#             AutoTrainer(model=model, trn_ds=trn_ds, val_portion=0.1,
#                         batch_size=4096, epochs=1000, callbacks=callbacks, **kwargs)()
#     return model


# Test reconstruction
# def test4(movie, language, n_chars, n_images, mode, calculate_accuracy=False):
#     kwargs = {"interactive": False, "mode": mode, "n_chars": n_chars, "verbosity": 2}
#     h5_file = f"{data_root}/{movie}/{language}_{mode.replace(' ', '')}.h5"
#     srt_file = f"{data_root}/{movie}/{language}_{mode.replace(' ', '')}.srt"
#
#     model = test3(n_chars, n_images, mode)
#
#     subs = ImageSubtitleSeries.load(infile=h5_file, **kwargs)
# subs.predict(model)
# subs.reconstruct_text()
# subs.save(srt_file)
# if calculate_accuracy:
#     std_file = f"{data_root}/{movie}/standard.srt"
#     subs.calculate_accuracy(std_file, n_chars)
# subs.manually_assign_chars(start_index=0)
# subs.save(h5_file)

# test4("magnificent_madame_mak", "cmn-Hans", 10, 100, "8 bit", False)
# test4("magnificent_madame_mak", "cmn-Hans", 10, 100, "1 bit", False)
# test4("mcdull_kung_fu_ding_ding_dong", "cmn-Hans", 10, 100, "8 bit", False)
# test4("mcdull_kung_fu_ding_ding_dong", "cmn-Hans", 10, 100, "1 bit", False)
# test4("mcdull_prince_de_la_bun", "cmn-Hans", 1000, 500, "8 bit", True)
# test4("mcdull_prince_de_la_bun", "cmn-Hans", 10, 100, "1 bit", True)

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
# trn_file = f"{sub_root}/magnificent_mcdull/mcdull_8bit.h5"
# tst_file = f"{data_root}/tst_8bit.h5"
# gather_test()
# kwargs["mode"] = "1 bit"
# model_file = f"{data_root}/model_0100_0100_1bit.h5"
# trn_file = f"{sub_root}/magnificent_mcdull/mcdull_1bit.h5"
# tst_file = f"{data_root}/tst_1bit.h5"
# gather_test()
