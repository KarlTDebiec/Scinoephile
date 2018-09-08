#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.Trainer.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from zysyzm.ocr import OCRCLToolBase
from IPython import embed


################################### CLASSES ###################################
class ModelTrainer(OCRCLToolBase):
    """
    Trains model

    Todo:
      - CL arguments
      - Support for western characters and punctuation
      - Look into whether or not more data can be stored in hdf5 with model
      - Decide whether or not to move load_labeled_data out of class
    """

    # region Instance Variables

    help_message = ("Tool for training model")

    # endregion

    # region Builtins

    def __init__(self, **kwargs):
        """
        Initializes tool
        Args:
            kwargs (dict): Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.n_chars = 100
        self.trn_input_directory = "/Users/kdebiec/Desktop/docs/subtitles/trn"
        self.val_input_directory = "/Users/kdebiec/Desktop/docs/subtitles/val"
        self.tst_input_directory = "/Users/kdebiec/Desktop/docs/subtitles/tst"
        # self.model_infile = "/Users/kdebiec/Desktop/docs/subtitles/model.h5"
        self.model_outfile = "/Users/kdebiec/Desktop/docs/subtitles/model.h5"

    def __call__(self):
        """Core logic"""
        import numpy as np
        import tensorflow as tf
        from tensorflow import keras
        from zysyzm.ocr import GeneratedOCRDataset

        # Load and organize data
        trn_img, trn_lbl = self.load_labeled_data(self.trn_input_directory)
        trn_dataset = GeneratedOCRDataset(input_image_dir=self.trn_input_directory)
        trn_dataset.read_image_dir()
        nay_img, nay_lbl = trn_dataset.get_images_and_labels()
        val_img, val_lbl = self.load_labeled_data(self.val_input_directory)
        tst_img, tst_lbl = self.load_labeled_data(self.tst_input_directory)
        tst_img = tst_img[tst_lbl < self.n_chars]
        tst_lbl = tst_lbl[tst_lbl < self.n_chars]

        if self.n_chars is None:
            self.n_chars = trn_lbl.max() + 1

        # Prepare and train model
        if self.model_infile is not None:
            # Reload model
            if self.verbosity >= 1:
                print(f"Loading model from {self.model_infile}")
            model = keras.models.load_model(self.model_infile)
            model.compile(optimizer=tf.train.AdamOptimizer(),
                          loss='sparse_categorical_crossentropy',
                          metrics=['accuracy'])
        else:
            # Define model
            model = keras.Sequential([
                keras.layers.Dense(256,
                                   # input_shape=(12800,),
                                   input_shape=(19200,),
                                   activation=tf.nn.relu),
                keras.layers.Dense(self.n_chars,
                                   activation=tf.nn.softmax)
            ])
            model.compile(optimizer=tf.train.AdamOptimizer(),
                          loss='sparse_categorical_crossentropy',
                          metrics=['accuracy'])

            # Train model
            model.fit(trn_img, trn_lbl, epochs=10,
                      validation_data=(val_img, val_lbl))

        # Evaluate model
        trn_pred = model.predict(trn_img)
        trn_loss, trn_acc = model.evaluate(trn_img, trn_lbl)
        val_pred = model.predict(val_img)
        val_loss, val_acc = model.evaluate(val_img, val_lbl)
        tst_pred = model.predict(tst_img)
        tst_loss, tst_acc = model.evaluate(tst_img, tst_lbl)

        # Print Evaluation
        print(f"Training    Count:{trn_lbl.size:5d} Loss:{trn_loss:7.5f} Accuracy:{trn_acc:7.5f}")
        print(f"Validation  Count:{val_lbl.size:5d} Loss:{val_loss:7.5f} Accuracy:{val_acc:7.5f}")
        print(f"Test        Count:{tst_lbl.size:5d} Loss:{tst_loss:7.5f} Accuracy:{tst_acc:7.5f}")
        for i, char in enumerate(self.labels_to_chars(tst_lbl)):
            tst_poss_lbls = np.argsort(tst_pred[i])[::-1]
            tst_poss_chars = self.labels_to_chars(tst_poss_lbls)
            tst_poss_probs = np.round(tst_pred[i][tst_poss_lbls], 2)
            if char != tst_poss_chars[0]:
                matches = [f'{a}:{b:4.2f}'
                           for a, b in zip(tst_poss_chars[:10],
                                           tst_poss_probs[:10])]
                print(f"{char} | {' '.join(matches)}")

        # Save model
        if self.model_outfile is not None:
            if self.verbosity >= 1:
                print(f"Saving model to {self.model_outfile}")
            model.save(self.model_outfile)

        # Interactive prompt
        if self.interactive:
            embed()

    # endregion

    # region Public Properties

    @property
    def model_infile(self):
        """str: Path to input model file"""
        if not hasattr(self, "_model_infile"):
            self._model_infile = None
        return self._model_infile

    @model_infile.setter
    def model_infile(self, value):
        from os.path import expandvars, isfile

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        else:
            value = expandvars(value)
            if not isfile(value):
                raise ValueError()
        self._model_infile = value

    @property
    def model_outfile(self):
        """str: Path to output model file"""
        if not hasattr(self, "_model_outfile"):
            self._model_outfile = None
        return self._model_outfile

    @model_outfile.setter
    def model_outfile(self, value):
        from os import access, W_OK
        from os.path import dirname, expandvars

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        else:
            value = expandvars(value)
            if not access(dirname(value), W_OK):
                raise ValueError()
        self._model_outfile = value

    @property
    def n_chars(self):
        """int: Number of characters to match against"""
        if not hasattr(self, "_n_chars"):
            self._n_chars = None
        return self._n_chars

    @n_chars.setter
    def n_chars(self, value):
        if not isinstance(value, int) and value is not None:
            try:
                value = int(value)
            except Exception as e:
                raise ValueError()
        if value < 1 and value is not None:
            raise ValueError()
        self._n_chars = value

    @property
    def trn_input_directory(self):
        """str: Path to directory containing training character images"""
        if not hasattr(self, "_trn_input_directory"):
            self._trn_input_directory = None
        return self._trn_input_directory

    @trn_input_directory.setter
    def trn_input_directory(self, value):
        from os.path import expandvars, isdir

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        elif isinstance(value, str):
            value = expandvars(value)
            if not isdir(value):
                raise ValueError()
        self._trn_input_directory = value

    @property
    def tst_input_directory(self):
        """str: Path to directory containing test character images"""
        if not hasattr(self, "_tst_input_directory"):
            self._tst_input_directory = None
        return self._tst_input_directory

    @tst_input_directory.setter
    def tst_input_directory(self, value):
        from os.path import expandvars, isdir

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        elif isinstance(value, str):
            value = expandvars(value)
            if not isdir(value):
                raise ValueError()
        self._tst_input_directory = value

    @property
    def val_input_directory(self):
        """str: Path to directory containing validation character images"""
        if not hasattr(self, "_val_input_directory"):
            self._val_input_directory = None
        return self._val_input_directory

    @val_input_directory.setter
    def val_input_directory(self, value):
        from os.path import expandvars, isdir

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        elif isinstance(value, str):
            value = expandvars(value)
            if not isdir(value):
                raise ValueError()
        self._val_input_directory = value

    # endregion

    # region Public Methods

    def load_labeled_data(self, directory):
        import numpy as np
        from glob import iglob
        from PIL import Image
        from os.path import basename
        from os.path import isfile
        from os import remove

        if self.verbosity >= 1:
            print(f"Loading images and labels from '{directory}'")
        infiles = sorted(iglob(f"{directory}/*.png"))
        imgs, lbls = [], []

        # Check for cache of previously-loaded image data
        img_cache_file = f"{directory}/img_cache_2bitgrayscale.npy"
        lbl_cache_file = f"{directory}/lbl_cache_2bitgrayscale.npy"
        if isfile(img_cache_file) and isfile(lbl_cache_file):
            if self.verbosity >= 1:
                print(f"Loading image and label cache from '{img_cache_file} "
                      f"and '{lbl_cache_file}")
            imgs = np.load(img_cache_file)
            lbls = np.load(lbl_cache_file)
            if lbls.size == len(infiles):
                return imgs, lbls
            else:
                print(f"More image files present on disk than in cache, "
                      "reloading")
                imgs, lbls = [], []

        # Load and organize image files
        for infile in infiles:
            img = Image.open(infile)
            raw = np.array(img)
            # ORIGINAL LINE THAT WORKED VERY WELL
            # imgs += [np.append(
            #     np.logical_or(raw == 85, raw == 256).flatten(),
            #     np.logical_or(raw == 170, raw == 256).flatten())]
            # ACTUAL LOGIC IT WAS CARRYING OUT
            # imgs += [np.append(
            #     (raw == 85).flatten(),
            #     (raw == 170).flatten())]
            # TESTS
            imgs += [np.concatenate((
                (raw == 0).flatten(),
                (raw == 85).flatten(),
                (raw == 170).flatten()))]
            lbls += [np.argwhere(self.chars == basename(infile)[0])[0, 0]]
        imgs = np.stack(imgs)
        lbls = np.array(lbls, np.int16)

        # Write Cache files
        if self.verbosity >= 1:
            print(f"Saving image and label cache to '{img_cache_file} "
                  f"and '{lbl_cache_file}")
        if isfile(img_cache_file):
            remove(img_cache_file)
        np.save(img_cache_file, imgs)
        if isfile(lbl_cache_file):
            remove(lbl_cache_file)
        np.save(lbl_cache_file, lbls)

        return imgs, lbls

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    ModelTrainer.main()
