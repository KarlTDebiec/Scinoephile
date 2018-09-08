#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.AutoTrainer.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from zysyzm.ocr import OCRCLToolBase
from IPython import embed
from sys import exit


################################### CLASSES ###################################
class AutoTrainer(OCRCLToolBase):
    """
    Trains model

    Todo:
      - [ ] Generate fitting and validation sets with new class
      - [ ] Validate CL arguments
      - [ ] Support western characters and punctuation
      - [ ] Look into if information needed to 'compile' can be stored in hdf5
            with model
    """

    # region Instance Variables

    help_message = ("Tool for automatic model training")

    # endregion

    # region Builtins

    def __init__(self, model_infile=None, trn_infile=None, val_portion=None,
                 tst_infile=None, n_chars=None, shape=None, batch_size=None,
                 epochs=None, model_outfile=None, **kwargs):
        """
        Initializes tool

        Args:
            kwargs (dict): Additional keyword arguments
        """
        from os.path import isdir, isfile
        from zysyzm.ocr import LabeledOCRDataset, GeneratedOCRDataset

        super().__init__(**kwargs)

        # Store property values
        if model_infile is not None:
            self.model_infile = model_infile
        if val_portion is not None:
            self.val_portion = val_portion
        if n_chars is not None:
            self.n_chars = n_chars
        if shape is not None:
            self.shape = shape
        if batch_size is not None:
            self.batch_size = batch_size
        if epochs is not None:
            self.epochs = epochs
        if model_outfile is not None:
            self.model_outfile = model_outfile

        # Temporary manual configuration for testing
        trn_infile = "/Users/kdebiec/Desktop/docs/subtitles/trn.h5"
        tst_infile = "/Users/kdebiec/Desktop/docs/subtitles/tst"

        # Initialize training dataset
        self.trn_dataset = GeneratedOCRDataset(n_chars=self.n_chars)
        if trn_infile is not None:
            if isdir(trn_infile):
                self.trn_dataset.input_image_dir = trn_infile
                self.trn_dataset.read_image_dir()
            elif isfile(trn_infile):
                self.trn_dataset.input_hdf5 = trn_infile
                self.trn_dataset.read_hdf5()
            else:
                raise ValueError()

        # Initialize test dataset
        if tst_infile is not None:
            self.tst_dataset = LabeledOCRDataset()
            if isdir(tst_infile):
                self.tst_dataset.input_image_dir = tst_infile
                self.tst_dataset.read_image_dir()
            elif isfile(tst_infile):
                self.tst_dataset.input_hdf5 = tst_infile
                self.tst_dataset.read_hdf5()
            else:
                raise ValueError()

    def __call__(self):
        """Core logic"""
        import warnings
        import numpy as np
        import tensorflow as tf
        from tensorflow import keras

        def analyze(title, img, lbl, missed_chars=None):
            pred = model.predict(img)
            loss, acc = model.evaluate(img, lbl)
            errors = int(lbl.size * (1 - acc))
            if self.verbosity >= 1:
                print(f"{title:10s}  Count:{lbl.size:5d}  Loss:{loss:7.5f} "
                      f"Accuracy:{acc:7.5f}  Errors:{errors:d}")
            for i, char in enumerate(self.labels_to_chars(lbl)):
                poss_lbls = np.argsort(pred[i])[::-1]
                poss_chars = self.labels_to_chars(poss_lbls)
                poss_probs = np.round(pred[i][poss_lbls], 2)
                if char != poss_chars[0]:
                    if missed_chars is not None:
                        missed_chars.add(char)
                        # missed_chars.add(poss_chars[0])
                    if self.verbosity >= 2:
                        matches = [f"{a}:{b:4.2f}" for a, b in
                                   zip(poss_chars[:10], poss_probs[:10])]
                        print(f"{char} | {' '.join(matches)}")

        # Prepare training and validation data
        self.trn_dataset.generate_minimal_images()
        if self.trn_dataset.input_hdf5 is not None:
            self.trn_dataset.write_hdf5()
        trn_img, trn_lbl, val_img, val_lbl = \
            self.trn_dataset.get_data_for_training(
                val_portion=self.val_portion)
        trn_img = self.format_data_for_model(trn_img)
        val_img = self.format_data_for_model(val_img)

        # Prepare test data
        if self.tst_dataset is not None:
            tst_img, tst_lbl = self.tst_dataset.get_images_and_labels()
            tst_img = self.format_data_for_model(tst_img)
            tst_img = tst_img[tst_lbl < self.n_chars]
            tst_lbl = tst_lbl[tst_lbl < self.n_chars]

        # Prepare model
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

        # while True:
        # Train model
        # history = model.fit(dataset, steps_per_epoch=10)  # ,
        # trn_img, trn_lbl,
        # validation_data=(val_img, val_lbl),
        # epochs=self.epochs)  # ,
        # batch_size=self.batch_size)

        # Evaluate model
        # missed_chars = set()
        # analyze("Training", trn_img, trn_lbl, missed_chars)
        # analyze("Validation", val_img, val_lbl, missed_chars)

        # Expand fitting set
        # if len(missed_chars) > 1:
        #     if self.verbosity >= 1:
        #         print(f"Missed the following "
        #               f"{len(missed_chars)}/{self.n_chars} "
        #               f"characters: {''.join(missed_chars)}")
        # else:
        #     exit()
        #     self.trn_dataset.write_hdf5()
        #     self.n_chars += 10
        #     self.trn_dataset.n_chars += 10
        #     if self.verbosity >= 1:
        #         print(f"\n\n\nINCREASING N_CHARS TO {self.n_chars}\n\n\n")
        #     self.trn_dataset.generate_minimal_images()
        #     self.trn_dataset.generate_additional_images(
        #         self.chars[:self.n_chars], 1000)

    # endregion

    # region Public Properties

    @property
    def batch_size(self):
        """int: Training batch size"""
        if not hasattr(self, "_batch_size"):
            self._batch_size = 32
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value):
        if value is not None:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except Exception as e:
                    raise ValueError(self._generate_setter_exception(value))
            if value < 1 and value is not None:
                raise ValueError(self._generate_setter_exception(value))
        self._batch_size = value

    @property
    def epochs(self):
        """int: Number of epochs to train for"""
        if not hasattr(self, "_epochs"):
            self._epochs = 10
        return self._epochs

    @epochs.setter
    def epochs(self, value):
        if value is not None:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except Exception as e:
                    raise ValueError(self._generate_setter_exception(value))
            if value < 1 and value is not None:
                raise ValueError(self._generate_setter_exception(value))
        self._epochs = value

    @property
    def model_infile(self):
        """str: Path to input model file"""
        if not hasattr(self, "_model_infile"):
            self._model_infile = None
        return self._model_infile

    @model_infile.setter
    def model_infile(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._model_infile = value

    @property
    def model_outfile(self):
        """str: Path to output model file"""
        if not hasattr(self, "_model_outfile"):
            self._model_outfile = None
        return self._model_outfile

    @model_outfile.setter
    def model_outfile(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._model_outfile = value

    @property
    def n_chars(self):
        """int: Number of unique characters to support"""
        if not hasattr(self, "_n_chars"):
            self._n_chars = 10
        return self._n_chars

    @n_chars.setter
    def n_chars(self, value):
        if value is not None:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except Exception as e:
                    raise ValueError(self._generate_setter_exception(value))
            if value < 1:
                raise ValueError(self._generate_setter_exception(value))
        self._n_chars = value

    @property
    def shape(self):
        """list(int): Shape of model"""
        if not hasattr(self, "_shape"):
            self._shape = [128, 128, 128]
        return self._shape

    @shape.setter
    def shape(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise ValueError(self._generate_setter_exception(value))
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    try:
                        value[i] = int(v)
                    except Exception as e:
                        raise ValueError(self._generate_setter_exception(value))
        self._shape = value

    @property
    def trn_dataset(self):
        """zysyzm.ocr.GeneratedOCRDataset: Training/validation dataset"""
        if not hasattr(self, "_trn_dataset"):
            self._trn_dataset = None
        return self._trn_dataset

    @trn_dataset.setter
    def trn_dataset(self, value):
        from zysyzm.ocr import GeneratedOCRDataset

        if value is not None:
            if not isinstance(value, GeneratedOCRDataset):
                raise ValueError(self._generate_setter_exception(value))
        self._trn_dataset = value

    @property
    def tst_dataset(self):
        """zysyzm.ocr.GeneratedOCRDataset: Test dataset"""
        if not hasattr(self, "_tst_dataset"):
            self._tst_dataset = None
        return self._tst_dataset

    @tst_dataset.setter
    def tst_dataset(self, value):
        from zysyzm.ocr import LabeledOCRDataset

        if value is not None:
            if not isinstance(value, LabeledOCRDataset):
                raise ValueError(self._generate_setter_exception(value))
        self._tst_dataset = value

    @property
    def val_portion(self):
        """float: Portion of training data to set aside for validation"""
        if not hasattr(self, "_val_portion"):
            self._val_portion = 0.1
        return self._val_portion

    @val_portion.setter
    def val_portion(self, value):
        if value is not None:
            if not isinstance(value, float):
                try:
                    value = float(value)
                except Exception as e:
                    raise ValueError(self._generate_setter_exception(value))
            if value == 0:
                value = None
            elif not 0 < value < 1:
                raise ValueError(self._generate_setter_exception(value))
        self._val_portion = value

    # endregion

    # region Public Methpds

    def format_data_for_model(self, data):
        import numpy as np

        bit1 = data[:, 0::2]
        bit2 = data[:, 1::2]
        formatted = np.zeros((data.shape[0], 19200), np.bool)
        formatted[:, :6400] = np.logical_and(np.logical_not(bit1),
                                             np.logical_not(bit2))
        formatted[:, 6400:12800] = np.logical_and(np.logical_not(bit1), bit2)
        formatted[:, 12800:] = np.logical_and(bit1, np.logical_not(bit2))
        return formatted

    # endregion

    # region Public Class Methods

    @classmethod
    def construct_argparser(cls, parser=None):
        """
        Constructs argument parser

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        import argparse

        # Prepare parser
        if isinstance(parser, argparse.ArgumentParser):
            parser = parser
        elif isinstance(parser, argparse._SubParsersAction):
            parser = parser.add_parser(name="extraction",
                                       description=cls.help_message,
                                       help=cls.help_message)
        elif parser is None:
            parser = argparse.ArgumentParser(description=cls.help_message)
        super().construct_argparser(parser)

        # Input
        parser_inp = parser.add_argument_group("input arguments")
        # parser_inp.add_argument("-i", "--model_infile",
        #                         type=str,
        #                         help="input model hdf5 file")
        # parser_inp.add_argument("-r", "--train_data",
        #                         type=str, dest="train",
        #                         help="labeled training/validation data")
        # parser_inp.add_argument("-t", "--test_infile",
        #                         type=str, dest="tst_infile",
        #                         help="labeled test data")
        parser_inp.add_argument("-V", "--val_portion", type=float,
                                help="portion of training data to set aside "
                                     "for validation")

        # Operation
        parser_ops = parser.add_argument_group("operation arguments")
        parser_ops.add_argument("-n", "--n_chars",
                                type=int,
                                help="restrict model to set number of "
                                     "characters")

        # parser_ops.add_argument("-s", "--shape",
        #                         type=int, nargs="*",
        #                         help="model shape")
        # parser_ops.add_argument("-b", "--batch_size",
        #                         type=int,
        #                         help="batch size")
        # parser_ops.add_argument("-e", "--epochs",
        #                         type=int,
        #                         help="number of epochs")

        # Output
        # parser_out = parser.add_argument_group("output arguments")
        # parser_out.add_argument("-o", "--model_outfile",
        #                         type=str,
        #                         help="output model hdf5 file")

        return parser

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    AutoTrainer.main()
