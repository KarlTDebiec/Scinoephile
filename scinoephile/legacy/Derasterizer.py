#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Converts image-based subtitles into text using a deep neural network-based
optical character recognition model."""
from __future__ import annotations

import numpy as np
from tensorflow import keras

from scinoephile import (
    CLToolBase,
    SubtitleSeries,
    input_prefill,
    is_readable,
    is_writable,
)
from scinoephile.ocr import (
    ImageSubtitleSeries,
    analyze_text_accuracy,
    eastern_punctuation_chars,
    get_reconstructed_text,
    get_tesseract_text,
    hanzi_chars,
    numeric_chars,
    western_chars,
    western_punctuation_chars,
)


class Derasterizer(CLToolBase):
    """Converts image-based Chinese subtitles to text."""

    # region Builtins

    def __init__(
        self,
        infile,
        interactive=False,
        overwrite=False,
        outfile=None,
        recognition_model=None,
        standard_infile=None,
        tesseract=False,
        **kwargs,
    ):
        """
        Initializes command-line tool and compiles list of operations.

        Args:
            infile (str): Path to image-based Chinese Hanzi subtitle infile
            outfile (str): Path to text-based Chinese Hanzi subtitle outfile
            overwrite (bool): Overwrite outfile if it exists
            recognition_model (str): Path to character recognition model infile
            standard_infile (str): Path to known accurate text-based Chinese
              Hanzi subtitle infile
            tesseract (bool): Use tesseract library for OCR rather than
              scinoephile
            interactive (bool): Interactively validate results
            **kwargs: Additional keyword arguments
        """
        from os.path import expandvars, isfile

        super().__init__(**kwargs)

        # Compile input operations
        infile = expandvars(str(infile))
        if is_readable(infile):
            self.operations["load_infile"] = infile
        else:
            raise IOError(f"Image-based subtitle infile " f"'{infile}' cannot be read")
        if tesseract:
            if not recognition_model:
                self.operations["derasterize_using_tesseract"] = True
            else:
                raise ValueError(
                    "Use of tesseract library for OCR precludes "
                    "use of provided recognition model infile"
                )
        elif recognition_model:
            recognition_model = expandvars(str(recognition_model))
            if is_readable(recognition_model):
                self.operations["load_recognition_model"] = recognition_model
                self.operations["segment_characters"] = True
                self.operations["recognize_characters"] = True
                self.operations["reconstruct_text"] = True
            else:
                raise IOError(
                    f"Character recognition model infile "
                    f"'{recognition_model}' cannot be read"
                )
        else:
            raise ValueError(
                "Must provide either recognition model or "
                "use tesseract; neither provided"
            )
        if standard_infile:
            standard_infile = expandvars(str(standard_infile))
            if is_readable(standard_infile):
                self.operations["load_standard"] = standard_infile
                self.operations["compare_standard"] = True
            else:
                raise IOError(
                    f"Standard subtitle infile " f"'{standard_infile}' cannot be read"
                )

        # Compile output operations
        if outfile:
            outfile = expandvars(str(outfile))
            if is_writable(outfile):
                if not isfile(outfile) or overwrite:
                    self.operations["save_outfile"] = outfile
                else:
                    raise IOError(
                        f"Text-based subtitle outfile " f"'{outfile}' already exists"
                    )
            else:
                raise IOError(
                    f"Text-based subtitle outfile " f"'{outfile}' is not writable"
                )

        # Compile additional operations
        if interactive:
            self.operations["interactive"] = True

    def __call__(self):
        """Performs operations."""

        # Load infiles
        if "load_infile" in self.operations:
            self.image_subtitles = ImageSubtitleSeries.load(
                self.operations["load_infile"], verbosity=self.verbosity
            )
        if "load_recognition_model" in self.operations:
            self.recognition_model = keras.models.load_model(
                self.operations["load_recognition_model"]
            )
        if "load_standard" in self.operations:
            self.standard_subtitles = SubtitleSeries.load(
                self.operations["load_standard"], verbosity=self.verbosity
            )

        # Derasterize
        # TODO: Don't hardcode characters
        self.chars = np.concatenate(
            (
                numeric_chars,
                western_chars,
                western_punctuation_chars,
                eastern_punctuation_chars,
                hanzi_chars[:9933],
            )
        )
        self.reassigned_chars
        if "segment_characters" in self.operations:
            self.image_subtitles._initialize_data()
        if "recognize_characters" in self.operations:
            self._recognize_characters()
        if "interactive" in self.operations:
            self._validate_chars_interactively()
        if "reconstruct_text" in self.operations:
            self._reconstruct_text()
        if "derasterize_using_tesseract" in self.operations:
            self._derasterize_using_tesseract()

        # Analyze results
        if "compare_standard" in self.operations:
            analyze_text_accuracy(
                self.image_subtitles,
                self.standard_subtitles,
                self.chars,
                verbosity=self.verbosity,
            )

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
    def reassigned_chars(self):
        """set(str): Characters that have been reassigned"""
        if not hasattr(self, "_reassigned_chars"):
            self._reassigned_chars = set()
        return self._reassigned_chars

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
        Gets unique integer indexes of provided char strings.

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
        return np.array(sorter[np.searchsorted(self.chars, chars, sorter=sorter)])

    def get_chars_of_labels(self, labels):
        """
        Gets char strings of unique integer indexes.

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

    # endregion

    # region Private Methods

    def _derasterize_using_tesseract(self):
        from multiprocessing import Pool, cpu_count

        if self.verbosity >= 1:
            print(f"Reconstructing text using tesseract")

        for i, text in enumerate(
            Pool(cpu_count()).imap(
                get_tesseract_text, [e.img for e in self.image_subtitles.events]
            )
        ):
            self.image_subtitles.events[i].text = text
            if self.verbosity >= 3:
                print(f"{i:4d} | {text}")

    def _recognize_characters(self):
        # TODO: Move to function
        data = np.expand_dims(
            self.image_subtitles.data.astype(np.float16) / 255.0, axis=3
        )
        label_pred = self.recognition_model.predict(data)
        char_pred = self.get_chars_of_labels(np.argsort(label_pred, axis=1)[:, -1])
        for i in self.image_subtitles.spec.index:
            if self.image_subtitles.spec.at[i, "confirmed"]:
                if self.image_subtitles.spec.at[i, "char"] != char_pred[i]:
                    self.reassigned_chars.add(self.image_subtitles.spec.at[i, "char"])
                    self.reassigned_chars.add(char_pred[i])
            else:
                self.image_subtitles.spec.at[i, "char"] = char_pred[i]

        # Replace half-width punctuation with full-width
        for i, char in self.image_subtitles.spec.iterrows():
            if char["char"] == "．" or char["char"] == ".":
                if self.verbosity >= 1:
                    print(f"Reassigning char {i} from " f"'{char['char']}' to '。'")
                self.image_subtitles.spec.at[i, "char"] = "。"
            elif char["char"] == "!":
                if self.verbosity >= 1:
                    print(f"Reassigning char {i} from " f"'{char['char']}' to '！'")
                self.image_subtitles.spec.at[i, "char"] = "！"
            elif char["char"] == ":":
                if self.verbosity >= 1:
                    print(f"Reassigning char {i} from " f"'{char['char']}' to '：'")
                self.image_subtitles.spec.at[i, "char"] = "："

    def _reconstruct_text(self):
        for i, event in enumerate(self.image_subtitles.events):
            event.text = get_reconstructed_text(
                event.char_spec["char"].values,
                event.char_widths,
                event.char_separations,
            )
            if self.verbosity >= 3:
                print(f"{i:4d} | {event.text}")

    def _validate_chars_interactively(self):
        # Validate all events, CTRL-c to quit
        for i, event in enumerate(self.image_subtitles.events):
            try:
                self._validate_event_interactively(event)
            except KeyboardInterrupt:
                print("\nQuitting subtitle validation")
                break

    def _validate_event_interactively(self, event):
        from difflib import SequenceMatcher

        from colorama import Fore, Style

        # Show user subtitle image and predicted text, and prompt for update
        if not np.all(event.char_spec["confirmed"]):
            event.show()
            print()
        prompt = f"{event.index:4d} | "
        for _, char in event.char_spec.iterrows():
            # TODO: Highlight orange if similar chars previously corrected
            if char["confirmed"] and char["char"] not in self.reassigned_chars:
                prompt += f"{Fore.GREEN}"
            elif char["confirmed"]:
                prompt += f"{Fore.MAGENTA}"
            elif char["char"] in self.reassigned_chars:
                prompt += f"{Fore.RED}"
            else:
                prompt += f"{Fore.WHITE}"
            prompt += f"{char['char']}{Style.RESET_ALL}"
        print(prompt)
        if np.all(event.char_spec["confirmed"]):
            return
        old_text = "".join(event.char_spec["char"])
        new_text = input_prefill(f"     | ", old_text)

        # Lengths are the same, assume no changes to segmentation
        if len(new_text) == len(old_text):
            for event_char_index, (char_index, char) in enumerate(
                event.char_spec.iterrows()
            ):

                # Reassign character
                if new_text[event_char_index] != char["char"]:
                    if self.verbosity >= 1:
                        print(
                            f"Reassigning char {char_index} from "
                            f"'{char['char']}' to "
                            f"'{new_text[event_char_index]}'"
                        )
                    self.reassigned_chars.add(new_text[event_char_index])
                    self.reassigned_chars.add(char["char"])
                    self.image_subtitles.spec.at[char_index, "char"] = new_text[
                        event_char_index
                    ]
                    self.image_subtitles.spec.at[char_index, "confirmed"] = True

                # Confirm character assignment
                elif not char["confirmed"]:
                    if self.verbosity >= 1:
                        print(f"Confirming char {char_index} as " f"'{char['char']}'")
                    self.image_subtitles.spec.at[char_index, "confirmed"] = True

        # Lengths are not the same, merge chars
        else:
            opcodes = SequenceMatcher(a=old_text, b=new_text).get_opcodes()
            for kind, old_start, old_end, new_start, new_end in opcodes:

                # Confirm one or more characters
                if kind == "equal":
                    for char_index, char in event.char_spec.iloc[
                        old_start:old_end
                    ].iterrows():
                        if self.verbosity >= 2:
                            print(
                                f"Confirming char {char_index} as " f"'{char['char']}'"
                            )
                        self.image_subtitles.spec.at[char_index, "confirmed"] = True

                # Replace one or more characters
                elif kind == "replace":

                    # Straight character by character replacement
                    if old_end - old_start == new_end - new_start:
                        # TODO: Handle normal reassingments alongside merges
                        embed(**self.embed_kw)

                    # Merging two characters into one
                    elif old_end - old_start == 2 and new_end - new_start == 1:
                        self.reassigned_chars.add(
                            event.char_spec.iloc[old_start]["char"]
                        )
                        self.reassigned_chars.add(
                            event.char_spec.iloc[old_start + 1]["char"]
                        )
                        self.image_subtitles._merge_chars(
                            event.char_spec.iloc[old_start].name,
                            event.char_spec.iloc[old_start + 1].name,
                            char=new_text[new_start],
                        )
                        self._validate_event_interactively(event)
                        # Subsequent edits handled through recursion
                        break

                    # Merging three characters into one
                    elif old_end - old_start == 3 and new_end - new_start == 1:
                        self.reassigned_chars.add(
                            event.char_spec.iloc[old_start]["char"]
                        )
                        self.reassigned_chars.add(
                            event.char_spec.iloc[old_start + 1]["char"]
                        )
                        self.reassigned_chars.add(
                            event.char_spec.iloc[old_start + 2]["char"]
                        )
                        self.image_subtitles._merge_chars(
                            event.char_spec.iloc[old_start].name,
                            event.char_spec.iloc[old_start + 1].name,
                            event.char_spec.iloc[old_start + 2].name,
                            char=new_text[new_start],
                        )
                        self._validate_event_interactively(event)
                        # Subsequent edits handled through recursion
                        break

                    # Unusual merging
                    else:
                        # TODO: Handle this case
                        embed(**self.embed_kw)

                # Delete one or more characters?
                elif kind == "delete":
                    if old_end - old_start == 1:
                        self.reassigned_chars.add(
                            event.char_spec.iloc[old_start - 1]["char"]
                        )
                        self.reassigned_chars.add(
                            event.char_spec.iloc[old_start]["char"]
                        )
                        self.image_subtitles._merge_chars(
                            event.char_spec.iloc[old_start - 1].name,
                            event.char_spec.iloc[old_start].name,
                            char=new_text[new_start - 1],
                        )
                        self._validate_event_interactively(event)
                        # Subsequent edits handled through recursion
                        break
                    else:
                        # TODO: Handle this case
                        embed(**self.embed_kw)

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs):
        """
        Constructs argument parser.

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__, **kwargs)

        # Input
        parser_input = parser.add_argument_group("input arguments")
        parser_input.add_argument(
            "-if",
            "--infile",
            help="image-based Chinese Hanzi subtitle " "infile",
            metavar="FILE",
            required=True,
        )
        parser_input.add_argument(
            "-rm",
            "--recognition_model",
            help="character recognition model infile",
            metavar="FILE",
        )
        parser_input.add_argument(
            "-sf",
            "--standard",
            dest="standard_infile",
            help="known accurate text-based Chinese "
            "Hanzi subtitle infile for validation "
            "of OCR results",
            metavar="FILE",
        )
        # Operations
        parser_ops = parser.add_argument_group("operation arguments")
        parser_ops.add_argument(
            "-t",
            "--tesseract",
            action="store_true",
            help="use tesseract library for OCR rather "
            "than scinoephile's bespoke model",
        )
        parser_ops.add_argument(
            "-i",
            "--interactive",
            action="store_true",
            help="interactively validate results",
        )

        # Output
        parser_output = parser.add_argument_group("output arguments")
        parser_output.add_argument(
            "-of",
            "--outfile",
            help="text-based Chinese Hanzi subtitle " "outfile",
            metavar="FILE",
        )
        parser_output.add_argument(
            "-o",
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )

        return parser

    # endregion


if __name__ == "__main__":
    Derasterizer.main()