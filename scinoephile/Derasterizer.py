#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.Derasterizer.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Converts image-based subtitles into text using deep a neural network-based
optical character recognition model.
"""
################################### MODULES ###################################
import numpy as np
import pandas as pd
from os.path import expandvars, isfile
from tensorflow import keras
from IPython import embed
from scinoephile import input_prefill, CLToolBase, Metavar, SubtitleSeries
from scinoephile.ocr import (eastern_punctuation_chars, hanzi_chars,
                             numeric_chars, western_chars,
                             western_punctuation_chars, ImageSubtitleSeries)


################################### CLASSES ###################################
class Derasterizer(CLToolBase):
    """
    Converts image-based subtitles to text
    """

    # region Builtins

    def __init__(self, infile, recognition_model, outfile=None, standard=None,
                 **kwargs):
        """
        Initializes command-line tool

            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Catalogue input and output operations
        # TODO: Add useful exception text
        infile = expandvars(infile)
        if isfile(infile):
            self.operations["load_infile"] = infile
        else:
            raise ValueError()
        self.operations["segment"] = True
        recognition_model = expandvars(recognition_model)
        if isfile(recognition_model):
            self.operations["load_recognition_model"] = recognition_model
        else:
            raise ValueError()
        if outfile is not None:
            outfile = expandvars(outfile)
            self.operations["save_outfile"] = outfile
        if standard is not None:
            standard = expandvars(standard)
            self.operations["load_standard"] = standard

    def __call__(self):
        """
        Performs operations
        """

        # Read infiles
        if "load_infile" in self.operations:
            self.image_subtitles = ImageSubtitleSeries.load(
                self.operations["load_infile"], verbosity=self.verbosity)
        if "load_recognition_model" in self.operations:
            self.recognition_model = keras.models.load_model(
                self.operations["load_recognition_model"])
        if "load_standard" in self.operations:
            self.standard_subtitles = SubtitleSeries.load(
                self.operations["load_standard"], verbosity=self.verbosity)

        # Chars
        self.chars = np.concatenate(
            (numeric_chars, western_chars, western_punctuation_chars,
             eastern_punctuation_chars, hanzi_chars[:2200]))
        self.image_subtitles._initialize_data()

        # Make predictions
        if self.verbosity >= 1:
            print(f"Making character predictions")
        data = np.expand_dims(
            self.image_subtitles.data.astype(np.float16) / 255.0, axis=3)
        label_pred = self.recognition_model.predict(data)
        char_pred = self.get_chars_of_labels(
            np.argsort(label_pred, axis=1)[:, -1])

        # Assign characters
        if self.verbosity >= 1:
            print(f"Assigning characters")
        for i, spec in self.image_subtitles.spec.iterrows():
            if spec.char != "":
                continue
            if self.verbosity >= 2:
                print(f"Assigning character {i} as '{char_pred[i]}'")
            spec.char = char_pred[i]

        # Reconstruct text
        if self.verbosity >= 1:
            print(f"Reconstructing text")
        for i, event in enumerate(self.image_subtitles.events):
            if self.verbosity >= 2:
                print(f"Reconstructing text for subtitle {i}")

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
            if self.verbosity >= 2:
                print(event.text)

        # Validate assignments
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

        # embed(**self.embed_kw)

        # Compare to standard
        if self.standard_subtitles is not None:
            event_pairs = zip([e.text for e in self.image_subtitles.events],
                              [e.text for e in self.standard_subtitles.events])
            n_events = len(self.image_subtitles.events)
            n_events_correct_length = n_events
            n_chars_total = 0
            n_chars_correct = 0
            n_chars_matchable = 0
            for pred_text, true_text in event_pairs:

                # Skip whitespace
                pred_text = pred_text.replace("　", "").replace(" ", "")
                true_text = true_text.replace("　", "").replace(" ", "")
                n_chars_total += len(true_text)

                # Loop over characters
                if len(pred_text) != len(true_text):
                    n_events_correct_length -= 1
                else:
                    for pred_char, true_char in zip(pred_text, true_text):
                        if true_char in self.chars:
                            n_chars_matchable += 1
                            if pred_char == true_char:
                                n_chars_correct += 1
            print(f"{n_events_correct_length}/{n_events} "
                  f"subtitles segmented correctly (accuracy = "
                  f"{n_events_correct_length / n_events:6.4})")
            print(f"{n_chars_correct}/{n_chars_total} "
                  f"characters recognized correctly (accuracy = "
                  f"{n_chars_correct / n_chars_total:6.4})")
            print(f"{n_chars_correct}/{n_chars_matchable} "
                  f"matchable characters recognized correctly (accuracy = "
                  f"{n_chars_correct / n_chars_matchable:6.4f})")

        # from IPython import embed
        # embed(**self.embed_kw)
        import pytesseract
        from copy import deepcopy

        if self.verbosity >= 1:
            print(f"Reconstructing text using tesseract")
        tess_subtitles = deepcopy(self.image_subtitles)
        for i, event in enumerate(tess_subtitles.events):
            if self.verbosity >= 2:
                print(f"Reconstructing text for subtitle {i} using tesseract")
            event.text = pytesseract.image_to_string(
                event.img,
                config=f"--psm 7 --oem 3",
                lang="chi_sim")
            if self.verbosity >= 2:
                print(event.text)

        # Compare to standard
        if self.standard_subtitles is not None:
            event_pairs = zip([e.text for e in tess_subtitles.events],
                              [e.text for e in self.standard_subtitles.events])
            n_events = len(tess_subtitles.events)
            n_events_correct_length = n_events
            n_chars_total = 0
            n_chars_correct = 0
            n_chars_matchable = 0
            for pred_text, true_text in event_pairs:

                # Skip whitespace
                pred_text = pred_text.replace("　", "").replace(" ", "")
                true_text = true_text.replace("　", "").replace(" ", "")
                n_chars_total += len(true_text)

                # Loop over characters
                if len(pred_text) != len(true_text):
                    n_events_correct_length -= 1
                else:
                    for pred_char, true_char in zip(pred_text, true_text):
                        if true_char in self.chars:
                            n_chars_matchable += 1
                            if pred_char == true_char:
                                n_chars_correct += 1
            print(f"{n_events_correct_length}/{n_events} "
                  f"subtitles segmented correctly (accuracy = "
                  f"{n_events_correct_length / n_events:6.4})")
            print(f"{n_chars_correct}/{n_chars_total} "
                  f"characters recognized correctly (accuracy = "
                  f"{n_chars_correct / n_chars_total:6.4})")
            print(f"{n_chars_correct}/{n_chars_matchable} "
                  f"matchable characters recognized correctly (accuracy = "
                  f"{n_chars_correct / n_chars_matchable:6.4f})")

        # # Write outfiles
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
        # TODO: Improve exception text

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
        pass
        # from pypinyin import pinyin
        #
        # if self.char_predictions is not None:
        #     predictions = self.get_chars_of_labels(
        #         np.argsort(self.char_predictions, axis=1)[:, -1])
        # else:
        #     predictions = None
        #
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
        #
        #     self.show(indexes=i)
        #
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
        #
        # embed(**self.embed_kw)

    def merge_chars(self, index):
        """
        Merges two adjacent characters

        Args:
            index (int): Index of first of two characters to merge
        """
        pass
        # self._char_bounds = np.append(
        #     self.char_bounds.flatten()[:index * 2 + 1],
        #     self.char_bounds.flatten()[index * 2 + 3:]).reshape((-1, 2))

    # endregion

    # region Private Methods

    def _analyze_predictions(self, img, lbl, model, title="", verbosity=1,
                             **kwargs):
        pass
        # pred = model.predict(img)
        # loss, acc = model.evaluate(img, lbl)
        # if verbosity >= 1:
        #     print(f"{title:10s}  Count:{lbl.size:5d}  Loss:{loss:7.5f} "
        #           f"Accuracy:{acc:7.5f}")
        # if verbosity >= 2:
        #     for i, char in enumerate(get_chars_of_labels(lbl)):
        #         poss_lbls = np.argsort(pred[i])[::-1]
        #         poss_chars = get_chars_of_labels(poss_lbls)
        #         poss_probs = np.round(pred[i][poss_lbls], 2)
        #         if char != poss_chars[0]:
        #             if verbosity >= 2:
        #                 matches = [f"{a}:{b:4.2f}" for a, b in
        #                            zip(poss_chars[:10], poss_probs[:10])]
        #                 print(f"{char} | {' '.join(matches)}")
        #
        # return loss, acc

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs):
        """
        Constructs argument parser

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__, **kwargs)

        # Files
        parser_file = parser.add_argument_group("file arguments")
        parser_file.add_argument("-i", "--infile", type=str,
                                 nargs="+", required=True,
                                 action=cls.get_filepath_action(),
                                 metavar="FILE",
                                 help="Input image-based subtitle file")
        parser_file.add_argument("-m", "--model", type=str,
                                 nargs="+",
                                 action=cls.get_filepath_action(),
                                 metavar="FILE", dest="recognition_model",
                                 help="Input model file")
        parser_file.add_argument("-o", "--outfile", type=str,
                                 nargs="+",
                                 action=cls.get_filepath_action(),
                                 metavar="FILE",
                                 help="Output subtitle file")
        parser_file.add_argument("-s", "--standard", type=str,
                                 nargs="+",
                                 action=cls.get_filepath_action(),
                                 metavar=Metavar(["FILE", "overwrite"]),
                                 help="Standard subtitle file against which "
                                      "to compare results")
        # Model file for recognition

        # Operations
        parser_ops = parser.add_argument_group("operation arguments")

        return parser

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    Derasterizer.main()
