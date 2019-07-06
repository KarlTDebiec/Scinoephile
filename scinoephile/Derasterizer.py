#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.Derasterizer.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Converts image-based subtitles into text using a deep neural network-based
optical character recognition model.
"""
################################### MODULES ###################################
import numpy as np
import pandas as pd
from tensorflow import keras
from scinoephile import input_prefill, CLToolBase, SubtitleSeries
from scinoephile.ocr import (analyze_text_accuracy,
                             eastern_punctuation_chars, hanzi_chars,
                             numeric_chars, western_chars,
                             western_punctuation_chars, ImageSubtitleSeries)


################################### CLASSES ###################################
class Derasterizer(CLToolBase):
    """
    Converts image-based subtitles to text
    """

    # region Builtins

    def __init__(self, infile, outfile=None, overwrite=False,
                 recognition_model=None, standard_infile=None, tesseract=False,
                 **kwargs):
        """
        Initializes command-line tool and compiles list of operations
        Args:
            infile (str): Path to image-based subtitle infile
            outfile (str): Path to text-based subtitle infile
            overwrite (bool): Overwrite outfile if it exists
            recognition_model (str): Path to character recognition model
            standard_infile (str):
            tesseract (bool):
            **kwargs: Additional keyword arguments

        """

        from os import access, R_OK, W_OK
        from os.path import dirname, expandvars, isfile

        super().__init__(**kwargs)

        # Compile input operations
        infile = expandvars(str(infile))
        if isfile(infile) and access(infile, R_OK):
            self.operations["load_infile"] = infile
        else:
            raise IOError(f"Image-based subtitle infile "
                          f"'{infile}' cannot be read")
        if tesseract:
            if not recognition_model:
                self.operations["tesseract"] = "tesseract"
            else:
                raise ValueError("Use of tesseract library for OCR precludes "
                                 "use of provided recognition model infile")
        elif recognition_model:
            recognition_model = expandvars(str(recognition_model))
            if isfile(standard_infile) and access(standard_infile, R_OK):
                self.operations["load_recognition_model"] = recognition_model
                self.operations["segment_characters"] = True
                self.operations["recognize_characters"] = True
                self.operations["reconstruct_text"] = True
            else:
                raise IOError(f"Character recognition model infile "
                              f"'{recognition_model}' cannot be read")
        if standard_infile:
            standard_infile = expandvars(str(standard_infile))
            if isfile(standard_infile) and access(standard_infile, R_OK):
                self.operations["load_standard"] = standard_infile
                self.operations["compare_standard"] = True
            else:
                raise IOError(f"Standard subtitle infile "
                              f"'{standard_infile}' cannot be read")

        # Compile output operations
        if outfile:
            outfile = expandvars(str(outfile))
            if access(dirname(outfile), W_OK):
                if not isfile(outfile) or overwrite:
                    self.operations["save_outfile"] = outfile
                else:
                    raise IOError(f"Text-based Subtitle outfile "
                                  f"'{outfile}' already exists")
            else:
                raise IOError(f"Text-based subtitle outfile "
                              f"'{outfile}' is not writable")

    def __call__(self):
        """
        Performs operations
        """

        # Load infiles
        if "load_infile" in self.operations:
            self.image_subtitles = ImageSubtitleSeries.load(
                self.operations["load_infile"], verbosity=self.verbosity)
        if "load_recognition_model" in self.operations:
            self.recognition_model = keras.models.load_model(
                self.operations["load_recognition_model"])
        if "load_standard" in self.operations:
            self.standard_subtitles = SubtitleSeries.load(
                self.operations["load_standard"], verbosity=self.verbosity)

        # Derasterize
        self.chars = np.concatenate(
            (numeric_chars, western_chars, western_punctuation_chars,
             eastern_punctuation_chars, hanzi_chars[:100]))
        if "segment_characters" in self.operations:
            self.image_subtitles._initialize_data()
        if "recognize_characters" in self.operations:
            self._recognize_characters()
        if "reconstruct_text" in self.operations:
            self._reconstruct_text()
        if "tesseract" in self.operations:
            self._tesseract()

        # Analyze results
        if "compare_standard" in self.operations:
            analyze_text_accuracy(self.image_subtitles,
                                  self.standard_subtitles, self.chars,
                                  verbosity=self.verbosity)

        # Save outfile
        if "save_outfile" in self.operations:
            self.image_subtitles.save(self.operations["save_outfile"])

    # endregion

    # region Public Properties

    @property
    def chars(self):
        """list(str): Characters that may be present in this dataset"""
        if not hasattr(self, "_chars"):
            self._chars = hanzi_chars[:10]
        return self._chars

    @chars.setter
    def chars(self, value):
        # TODO: Validate
        if isinstance(value, int):
            value = np.array(hanzi_chars[:value])
        self._chars = value

    @property
    def char_predictions(self):
        """ndarray(float): Predicted confidence that each character image is
        each matchable character"""
        if not hasattr(self, "_char_predictions"):
            self._char_predictions = None
        return self._char_predictions

    @char_predictions.setter
    def char_predictions(self, value):
        if not isinstance(value, np.ndarray):
            raise ValueError(self._generate_setter_exception(value))
        if value.shape[0] != self.image_subtitles.data.shape[0]:
            raise ValueError(self._generate_setter_exception(value))
        self._char_predictions = value

    @property
    def image_subtitles(self):
        """ImageSubtitleSeries: Image-based subtitles"""
        if not hasattr(self, "_image_subtitles"):
            self._image_subtitles = None
        return self._image_subtitles

    @image_subtitles.setter
    def image_subtitles(self, value):
        if not isinstance(value, ImageSubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._image_subtitles = value

    @property
    def operations(self):
        """dict: Collection of operations to perform, with associated
        arguments"""
        if not hasattr(self, "_operations"):
            self._operations = {}
        return self._operations

    @property
    def recognition_model(self):
        """Model: Character recognition model"""
        if not hasattr(self, "_recognition_model"):
            raise ValueError()
        return self._recognition_model

    @recognition_model.setter
    def recognition_model(self, value):
        if not isinstance(value, keras.Model):
            raise ValueError(self._generate_setter_exception(value))
        self._recognition_model = value

    @property
    def standard_subtitles(self):
        """SubtitleSeries: Standard subtitles against which to compare
         results"""
        if not hasattr(self, "_standard_subtitles"):
            self._standard_subtitles = None
        return self._standard_subtitles

    @standard_subtitles.setter
    def standard_subtitles(self, value):
        if not isinstance(value, SubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._standard_subtitles = value

    # endregion

    # region Public Methods

    def get_labels_of_chars(self, chars):
        """
        Gets unique integer indexes of provided char strings

        Args:
            chars: Chars

        Returns:
             ndarray(int64): Labels
        """

        # Process arguments
        if isinstance(chars, str):
            if len(chars) == 1:
                return np.argwhere(self.chars == chars)[0, 0]
            elif len(chars) > 1:
                chars = list(chars)
        chars = np.array(chars)

        # Return labels
        sorter = np.argsort(self.chars)
        return np.array(
            sorter[np.searchsorted(self.chars, chars, sorter=sorter)])

    def get_chars_of_labels(self, labels):
        """
        Gets char strings of unique integer indexes

        Args:
            labels (ndarray(int64)): Labels

        Returns
            ndarray(U64): Chars
        """
        # TODO: Improve exception

        # Process arguments and return chars
        if isinstance(labels, int):
            return self.chars[labels]
        elif isinstance(labels, np.ndarray):
            return self.chars[labels]
        else:
            try:
                return self.chars[np.array(labels)]
            except Exception as e:
                raise e

    def manually_assign_chars(self, start_index=0):
        # TODO: Implement; propogate character updates, CL argument
        raise NotImplementedError()
        # Newer:
        # for i, event in enumerate(self.image_subtitles.events):
        #     event.show()
        #     try:
        #         text = input_prefill(f"'{event.text}': ", event.text)
        #     except EOFError:
        #         print(f"\nSkipping subtitle {i}")
        #         continue
        #     except KeyboardInterrupt:
        #         print("\nQuitting subtitle validation")
        #         break
        #     if text != event.text:
        #         if len(text) == len(event.text):
        #             for j, (yat, eee) in enumerate(zip(text, event.text)):
        #                 if yat != eee:
        #                     print(yat, eee)
        #                     print(event.char_spec.iloc[j])
        #                     embed(**self.embed_kw)
        # Older:
        # from pypinyin import pinyin
        # if self.char_predictions is not None:
        #     predictions = self.get_chars_of_labels(
        #         np.argsort(self.char_predictions, axis=1)[:, -1])
        # else:
        #     predictions = None
        # if self.verbosity >= 1:
        #     print("Assigning characters")
        #     print("  Press Enter to accept predicted character")
        #     print("  or type another character and press Enter to correct")
        #     print("  or press CTRL-D to skip character")
        #     print("  or press CTRL-C to stop assigning")
        #     print()
        # for i, spec in self.spec.iterrows():
        #     if spec.char != "":
        #         print(f"Character {i} previously assigned as '{spec.char}' "
        #               f"({pinyin(spec.char)[0][0]})")
        #         continue
        #     if i <= start_index:
        #         print(f"Skipping assignment of character {i}")
        #         continue
        #     self.show(indexes=i)
        #     try:
        #         if predictions is not None:
        #             match = input(f"'{predictions[i]}' "
        #                           f"({pinyin(predictions[i])[0][0]}): ")
        #         else:
        #             match = input(f"'' (): ")
        #     except EOFError:
        #         print(f"\nSkipping assignment of character {i}")
        #         continue
        #     except KeyboardInterrupt:
        #         print("\nQuitting character assignment")
        #         break
        #     if match == "":
        #         self.assign_char(i, predictions[i])
        #     else:
        #         self.assign_char(i, match)

    def merge_chars(self, index):
        """
        Merges two adjacent characters

        Args:
            index (int): Index of first of two characters to merge
        """
        # TODO: Implement
        raise NotImplementedError()
        # self._char_bounds = np.append(
        #     self.char_bounds.flatten()[:index * 2 + 1],
        #     self.char_bounds.flatten()[index * 2 + 3:]).reshape((-1, 2))

    # endregion

    # region Private Methods

    def _recognize_characters(self):
        # TODO: Move to function
        data = np.expand_dims(
            self.image_subtitles.data.astype(np.float16) / 255.0, axis=3)
        label_pred = self.recognition_model.predict(data)
        char_pred = self.get_chars_of_labels(
            np.argsort(label_pred, axis=1)[:, -1])
        for i, spec in self.image_subtitles.spec.iterrows():
            spec.char = char_pred[i]

    def _reconstruct_text(self):
        # TODO: Move to function
        for i, event in enumerate(self.image_subtitles.events):
            chars = event.char_spec["char"].values
            text = ""
            items = zip(chars[:-1], chars[1:], event.char_widths[:-1],
                        event.char_widths[1:], event.char_separations)
            for char_i, char_j, width_i, width_j, sep in items:
                text += char_i

                # Very large space: Two speakers
                if sep >= 100:
                    text = f"﹣{text}　　﹣"
                # Two Hanzi: separation cutoff of 40 to add double-width space
                elif width_i >= 45 and width_j >= 45 and sep >= 40:
                    # print("Adding a double-width space")
                    text += "　"
                # Two Roman: separation cutoff of 35 to add single-width space
                elif width_i < 45 and width_j < 45 and sep >= 36:
                    # print("Adding a single-width space")
                    text += " "
            text += chars[-1]
            # TODO: Reconstruct ellipsis

            event.text = text

    def _tesseract(self):
        # TODO: Move to function
        import pytesseract
        from copy import deepcopy

        if self.verbosity >= 1:
            print(f"Reconstructing text using tesseract")
        tess_subtitles = deepcopy(self.image_subtitles)
        for i, event in enumerate(tess_subtitles.events):
            if self.verbosity >= 2:
                print(
                    f"Reconstructing text for subtitle {i} using tesseract")
            event.text = pytesseract.image_to_string(
                event.img,
                config=f"--psm 7 --oem 3",
                lang="chi_sim")
            if self.verbosity >= 2:
                print(event.text)

    # endrion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs):
        """
        Constructs argument parser

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__, **kwargs)

        # Input
        parser_input = parser.add_argument_group("input arguments")
        parser_input.add_argument("-if", "--infile",
                                  help="image-based Chinese Hanzi subtitle "
                                       "infile",
                                  metavar="FILE",
                                  required=True)
        parser_input.add_argument("-rm", "--recognition_model",
                                  help="character recognition model infile",
                                  metavar="FILE")
        parser_input.add_argument("-sf", "--standard",
                                  dest="standard_infile",
                                  help="known accurate text-base Chinese "
                                       "Hanzi subtitle infile for validation "
                                       "of OCR results",
                                  metavar="FILE")
        # Operations
        parser_ops = parser.add_argument_group("operation arguments")
        parser_ops.add_argument("-t", "--tesseract",
                                action="store_true",
                                help="use tesseract library for OCR rather "
                                     "than scinoephile")

        # Output
        parser_output = parser.add_argument_group("output arguments")
        parser_output.add_argument("-of", "--outfile",
                                   help="text-based Chinese Hanzi subtitle "
                                        "outfile",
                                   metavar="FILE")
        parser_output.add_argument("-o", "--overwrite",
                                   action="store_true",
                                   help="overwrite outfile if it exists")

        return parser

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    Derasterizer.main()
