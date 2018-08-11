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


################################### CLASSES ###################################
class ModelTrainer(OCRCLToolBase):
    """
    Trains model

    Todo:
      - CL arguments
      - Validate CL arguments
      - Support western characters and punctuation
      - Look into if information needed to 'compile'  can be stored in hdf5
        with model
      - Decide whether or not to move load_labeled_data out of class
    """

    # region Instance Variables
    help_message = ("Tool for training model")

    # endregion

    # region Builtins
    def __init__(self, model_infile, trn_infile, tst_infile, n_chars,
                 shape, batch_size, epochs, model_outfile, **kwargs):
        """
        Initializes tool

        Args:
            kwargs (dict): Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.model_infile = model_infile
        self.trn_infile = trn_infile
        self.tst_infile = tst_infile
        self.n_chars = n_chars
        self.shape = shape
        self.batch_size = batch_size
        self.epochs = epochs
        self.model_outfile = model_outfile

    def __call__(self):
        """Core logic"""
        import warnings
        import numpy as np
        import tensorflow as tf
        from tensorflow import keras
        from IPython import embed

        def compile(model):
            model.compile(optimizer=tf.train.AdamOptimizer(),
                          loss="sparse_categorical_crossentropy",
                          metrics=["accuracy"])

        # Load and organize data
        trn_img, trn_lbl = self.load_labeled_data(self.trn_infile, True)
        if self.tst_infile is not None:
            tst_img, tst_lbl = self.load_labeled_data(self.tst_infile, True)

        if self.n_chars is None:
            self.n_chars = trn_lbl.max() + 1

        if self.model_infile is not None:
            # Reload model
            if self.verbosity >= 1:
                print(f"Loading model from {self.model_infile}")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = keras.models.load_model(self.model_infile)
            compile(model)
        else:
            # Define model
            model = keras.Sequential()
            for s in self.shape:
                model.add(keras.layers.Dense(
                    s,
                    input_shape=(12800,),
                    activation=tf.nn.relu))
            model.add(keras.layers.Dense(
                self.n_chars,
                input_shape=(12800,),
                activation=tf.nn.softmax), )
            compile(model)

            # Train model
            history = model.fit(trn_img, trn_lbl,
                                epochs=self.epochs,
                                batch_size=self.batch_size)

        # Save model
        if self.model_outfile is not None:
            if self.verbosity >= 1:
                print(f"Saving model to {self.model_outfile}")
            model.save(self.model_outfile)

        # Evaluate model
        trn_pred = model.predict(trn_img)
        trn_loss, trn_acc = model.evaluate(trn_img, trn_lbl)
        trn_errors = int(trn_lbl.size * (1 - trn_acc))
        print(f"Training    Count:{trn_lbl.size:5d}  Loss:{trn_loss:7.5f} "
              f"Accuracy:{trn_acc:7.5f}  Errors:{trn_errors:d}")
        if self.tst_infile is not None:
            tst_pred = model.predict(tst_img)
            tst_loss, tst_acc = model.evaluate(tst_img, tst_lbl)
            tst_errors = int(tst_lbl.size * (1 - tst_acc))
            print(f"Test        Count:{tst_lbl.size:5d}  Loss:{tst_loss:7.5f} "
                  f"Accuracy:{tst_acc:7.5f}  Errors:{tst_errors:d}")
            for i, char in enumerate(self.labels_to_chars(tst_lbl)):
                tst_poss_lbls = np.argsort(tst_pred[i])[::-1]
                tst_poss_chars = self.labels_to_chars(tst_poss_lbls)
                tst_poss_probs = np.round(tst_pred[i][tst_poss_lbls], 2)
                if char != tst_poss_chars[0]:
                    matches = [f'{a}:{b:4.2f}'
                               for a, b in zip(tst_poss_chars[:10],
                                               tst_poss_probs[:10])]
                    print(f"{char} | {' '.join(matches)}")

        # Interactive prompt
        if self.interactive:
            embed()

    # endregion

    # region Properties
    @property
    def batch_size(self):
        """int: Training batch size"""
        if not hasattr(self, "_batch_size"):
            self._batch_size = 1024
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value):
        if value is not None:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except Exception as e:
                    raise ValueError()
            if value < 1 and value is not None:
                raise ValueError()
        self._batch_size = value

    @property
    def epochs(self):
        """int: Number of epochs to train for"""
        if not hasattr(self, "_epochs"):
            self._epochs = 5
        return self._epochs

    @epochs.setter
    def epochs(self, value):
        if value is not None:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except Exception as e:
                    raise ValueError()
            if value < 1 and value is not None:
                raise ValueError()
        self._epochs = value

    @property
    def model_infile(self):
        """str: Path to input model file"""
        if not hasattr(self, "_model_infile"):
            self._model_infile = None
        return self._model_infile

    @model_infile.setter
    def model_infile(self, value):
        from os.path import expandvars, isfile

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(f"{type(value)} {value}")
            else:
                value = expandvars(value)
                if not isfile(value):
                    raise ValueError(f"{type(value)} {value}")
        self._model_infile = value

    @property
    def model_outfile(self):
        """str: Path to output model file"""
        if not hasattr(self, "_model_outfile"):
            self._model_outfile = None
        return self._model_outfile

    @model_outfile.setter
    def model_outfile(self, value):
        from os import access, R_OK, W_OK
        from os.path import dirname, expandvars, isfile

        if value is not None:
            if not isinstance(value, str):
                raise ValueError()
            else:
                value = expandvars(value)
                if isfile(value) and not access(value, R_OK):
                    raise ValueError()
                if not access(dirname(value), W_OK):
                    raise ValueError()
        self._model_outfile = value

    @property
    def n_chars(self):
        """int: Number of characters to restrict model to"""
        if not hasattr(self, "_n_chars"):
            self._n_chars = None
        return self._n_chars

    @n_chars.setter
    def n_chars(self, value):
        if value is not None:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except Exception as e:
                    raise ValueError()
            if value < 1 and value is not None:
                raise ValueError()
        self._n_chars = value

    @property
    def shape(self):
        """list(int): Shape of model"""
        if not hasattr(self, "_shape"):
            self._shape = None
        return self._shape

    @shape.setter
    def shape(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise ValueError()
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    try:
                        value[i] = int(v)
                    except Exception as e:
                        raise ValueError()
        self._shape = value

    @property
    def trn_infile(self):
        """str: Path to directory containing training character images"""
        if not hasattr(self, "_trn_input_directory"):
            self._trn_input_directory = None
        return self._trn_input_directory

    @trn_infile.setter
    def trn_infile(self, value):
        from os.path import expandvars, isdir

        if value is not None:
            if not isinstance(value, str):
                raise ValueError()
            elif isinstance(value, str):
                value = expandvars(value)
                if not isdir(value):
                    raise ValueError()
        self._trn_input_directory = value

    @property
    def tst_infile(self):
        """str: Path to directory containing test character images"""
        if not hasattr(self, "_tst_input_directory"):
            self._tst_input_directory = None
        return self._tst_input_directory

    @tst_infile.setter
    def tst_infile(self, value):
        from os.path import expandvars, isdir

        if value is not None:
            if not isinstance(value, str):
                raise ValueError()
            elif isinstance(value, str):
                value = expandvars(value)
                if not isdir(value):
                    raise ValueError()
        self._tst_input_directory = value

    # endregion

    # region Methods
    def load_labeled_data(self, directory, force_cache=False):
        import numpy as np
        from glob import iglob
        from PIL import Image
        from os.path import basename
        from os.path import isfile
        from os import remove

        if self.verbosity >= 1:
            print(f"Loading images and labels from '{directory}'")

        # Check for cache of previously-loaded image data
        if self.n_chars is not None:
            img_cache_file = f"{directory}/img_cache_n{self.n_chars}_2bitgrayscale.npy"
            lbl_cache_file = f"{directory}/lbl_cache_n{self.n_chars}_2bitgrayscale.npy"
        else:
            img_cache_file = f"{directory}/img_cache_2bitgrayscale.npy"
            lbl_cache_file = f"{directory}/lbl_cache_2bitgrayscale.npy"
        if isfile(img_cache_file) and isfile(lbl_cache_file):
            # Load cache
            if self.verbosity >= 1:
                print(f"Loading image and label cache from '{img_cache_file} "
                      f"and '{lbl_cache_file}")
            imgs = np.load(img_cache_file)
            lbls = np.load(lbl_cache_file)
            if force_cache:
                return imgs, lbls

            # Compare cache to files on disk
            infiles = sorted(iglob(f"{directory}/*.png"))
            if len(infiles) == lbls.size:
                return imgs, lbls
            if self.verbosity >= 1:
                print(f"Images files on disk do not match cache, reloading")
        else:
            infiles = sorted(iglob(f"{directory}/*.png"))
        imgs, lbls = [], []

        # Load and organize image files
        for infile in infiles:
            char = basename(infile)[0]
            lbl = self.chars_to_labels(char)
            if self.n_chars is not None and lbl >= self.n_chars - 1:
                continue
            img = Image.open(infile)
            raw = np.array(img)
            imgs += [np.append(
                np.logical_or(raw == 85, raw == 256).flatten(),
                np.logical_or(raw == 170, raw == 256).flatten())]
            lbls += [lbl]
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

    # region Class Methods
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
        parser_inp.add_argument("-i", "--model_infile",
                                type=str,
                                help="input model hdf5 file")
        parser_inp.add_argument("-r", "--train_infile",
                                type=str, required=True, dest="trn_infile",
                                help="labeled training/validation data")
        parser_inp.add_argument("-t", "--test_infile",
                                type=str, dest="tst_infile",
                                help="labeled test data")

        # Operation
        parser_ops = parser.add_argument_group("operation arguments")
        parser_ops.add_argument("-n", "--n_chars",
                                type=int,
                                help="restrict model to set number of "
                                     "characters")
        parser_ops.add_argument("-s", "--shape",
                                type=int, nargs="*",
                                help="model shape")
        parser_ops.add_argument("-b", "--batch_size",
                                type=int,
                                help="batch size")
        parser_ops.add_argument("-e", "--epochs",
                                type=int,
                                help="number of epochs")

        # Output
        parser_out = parser.add_argument_group("output arguments")
        parser_out.add_argument("-o", "--model_outfile",
                                type=str,
                                help="output model hdf5 file")

        return parser
    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    ModelTrainer.main()
