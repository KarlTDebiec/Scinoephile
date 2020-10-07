#!/usr/bin/env python
#   scinoephile.core.general.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from inspect import currentframe, getframeinfo
from readline import insert_text, redisplay, set_pre_input_hook
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from IPython import embed

from scinoephile import package_root
from scinoephile.core import SubtitleSeries


################################## FUNCTIONS ##################################
def embed_kw(verbosity: int = 2, **kwargs: Any) -> Dict[str, str]:
    """
    Prepares header for IPython prompt showing current location in code.

    Use ``IPython.embed(**embed_kw())``.

    Args:
        verbosity (int): Level of verbose output
        **kwargs: Additional keyword arguments

    Returns:
        dictionary: Keyword arguments to be passed to IPython.embed
    """
    frame = currentframe()
    if frame is None:
        raise ValueError()
    frameinfo = getframeinfo(frame.f_back)
    file = frameinfo.filename.replace(package_root, "")
    func = frameinfo.function
    number = frameinfo.lineno - 1
    header = ""
    if verbosity >= 1:
        header = f"IPython prompt in file {file}, function {func}," f" line {number}\n"
    if verbosity >= 2:
        header += "\n"
        with open(frameinfo.filename, "r") as infile:
            lines = [
                (i, line)
                for i, line in enumerate(infile)
                if i in range(number - 5, number + 6)
            ]
        for i, line in lines:
            header += f"{i:5d} {'>' if i == number else ' '} " f"{line.rstrip()}\n"

    return {"header": header}


def in_ipython() -> Union[bool, str]:
    """
    Determines if inside IPython prompt.

    Returns:
        str: Type of shell in use
    """
    try:
        shell = str(get_ipython().__class__.__name__)
        if shell == "ZMQInteractiveShell":
            # IPython in Jupyter Notebook
            return shell
        elif shell == "InteractiveShellEmbed":
            # IPython in Jupyter Notebook using IPython.embed
            return shell
        elif shell == "TerminalInteractiveShell":
            # IPython in terminal
            return shell
        else:
            # Other
            return False
    except NameError:
        # Not in IPython
        return False


def input_prefill(prompt: str, prefill: str) -> str:
    """
    Prompts user for input with pre-filled text.

    Does not handle colored prompt correctly

    TODO: Does this block CTRL-D?

    Args:
        prompt (str): Prompt to present to user
        prefill (str): Text to prefill for user

    Returns:
        str: Text inputted by user
    """

    def pre_input_hook() -> None:
        insert_text(prefill)
        redisplay()

    set_pre_input_hook(pre_input_hook)
    result = input(prompt)
    set_pre_input_hook()

    return result


def align_subtitles(
    align: Any, target: Any, sync_pair: Optional[Tuple[int, int]] = None
) -> SubtitleSeries:
    # Process arguments
    align = align.get_dataframe()
    align_starts = align["start"].values
    align_ends = align["end"].values
    target = target.get_dataframe()
    target_starts = target["start"].values
    target_ends = target["end"].values

    # Sync pair of subtitles, if accurate
    if sync_pair is not None:
        adjustment = int(
            ((target_ends[sync_pair[1]] + target_starts[sync_pair[1]]) / 2)
            - ((align_ends[sync_pair[0]] + align_starts[sync_pair[0]]) / 2)
        )
        align_starts += adjustment
        align_ends += adjustment

    #
    align_starts_tiled = np.tile(align_starts, (target_starts.size, 1))
    align_ends_tiled = np.tile(align_ends, (target_ends.size, 1))
    target_starts_tiled = np.transpose(np.tile(target_starts, (align_starts.size, 1)))
    target_ends_tiled = np.transpose(np.tile(target_ends, (align_ends.size, 1)))

    #
    numerator = np.minimum(align_ends_tiled, target_ends_tiled) - np.maximum(
        align_starts_tiled, target_starts_tiled
    )
    numerator[numerator < 0] = 0
    denominator = np.maximum(align_ends_tiled, target_ends_tiled) - np.minimum(
        align_starts_tiled, target_starts_tiled
    )
    overlap = numerator / denominator
    overlapping_pairs = np.squeeze(np.dstack(np.where(overlap > 0)))
    for i in range(target.shape[0]):
        pairs = overlapping_pairs[overlapping_pairs[:, 0] == i]

        # Single overlapping match
        if len(pairs) == 1:
            pair = pairs[0]
            if overlap[pair[0], pair[1]] >= 0.9:
                print(f"{i}, {pair}, {overlap[pair[0], pair[1]]}")
                align.loc[pair[1], ["start", "end"]] = target.loc[
                    pair[0], ["start", "end"]
                ]
        # Two overlapping matches, may be one subtitle in target and two in align
        if len(pairs) == 2:
            pair_1, pair_2 = pairs
            target_midpoint = int(
                (target_ends[pair_1[0]] + target_starts[pair_1[0]]) / 2
            )
            for pair in pairs:
                print(f"{i}, {pair}, {overlap[pair[0], pair[1]]}")
            embed()
    return SubtitleSeries.from_dataframe(align)


def merge_subtitles(upper: Any, lower: Any) -> pd.DataFrame:
    """
    Merges and synchronizes two sets of subtitles.

    Args:
        upper (SubtitleSeries, pandas.DataFrame): Upper subtitles
        lower (SubtitleSeries, pandas.DataFrame): Lower subtitles

    Returns:
        DataFrame: Merged and synchronized subtitles
    """

    def add_event(merged: List[Tuple[int, int, str]]) -> None:
        if start != time:
            if upper_text is None:
                merged += [
                    pd.DataFrame.from_records(
                        [(start, time, lower_text)],
                        columns=["start", "end", "lower text"],
                    )
                ]
            elif lower_text is None:
                merged += [
                    pd.DataFrame.from_records(
                        [(start, time, upper_text)],
                        columns=["start", "end", "upper text"],
                    )
                ]
            else:
                merged += [
                    pd.DataFrame.from_records(
                        [(start, time, upper_text, lower_text)],
                        columns=["start", "end", "upper text", "lower text"],
                    )
                ]

    # Process arguments
    if isinstance(upper, SubtitleSeries):
        upper = upper.get_dataframe()
    if isinstance(lower, SubtitleSeries):
        lower = lower.get_dataframe()

    # Organize transitions
    # TODO: Validate that events within each series do not overlap
    transitions: List[Tuple[int, str, Optional[str]]] = []
    for _, event in upper.iterrows():
        transitions += [
            (event["start"], "upper_start", event["text"]),
            (event["end"], "upper_end", None),
        ]
    for _, event in lower.iterrows():
        transitions += [
            (event["start"], "lower_start", event["text"]),
            (event["end"], "lower_end", None),
        ]
    transitions.sort()

    # Merge events
    merged: List[Tuple[int, int, str]] = []
    start = upper_text = lower_text = None
    for time, kind, text in transitions:
        if kind == "upper_start":
            if start is None:
                # Transition from __ -> C_
                pass
            else:
                # Transition from _E -> CE
                add_event(merged)
            upper_text = text
            start = time
        elif kind == "upper_end":
            add_event(merged)
            upper_text = None
            if lower_text is None:
                # Transition from C_ -> __
                start = None
            else:
                # Transition from CE -> _C
                start = time
        elif kind == "lower_start":
            if start is None:
                # Transition from __ -> _E
                pass
            else:
                # Transition from C_ -> CE
                add_event(merged)
            lower_text = text
            start = time
        elif kind == "lower_end":
            add_event(merged)
            lower_text = None
            if upper_text is None:
                # Transition from _E -> __
                start = None
            else:
                # Transition from CE -> E_
                start = time
    merged_df = pd.concat(merged, sort=False, ignore_index=True)[
        ["upper text", "lower text", "start", "end"]
    ]

    # Synchronize events
    synced_list = [merged_df.iloc[0].copy()]
    for index in range(1, merged_df.shape[0]):
        last = synced_list[-1]
        next = merged_df.iloc[index].copy()
        if last["upper text"] == next["upper text"]:
            if isinstance(last["lower text"], float) and np.isnan(last["lower text"]):
                # Upper started before lower
                last["lower text"] = next["lower text"]
                last["end"] = next["end"]
            elif isinstance(next["lower text"], float) and np.isnan(next["lower text"]):
                # Lower started before upper
                last["end"] = next["end"]
            else:
                # Single upper subtitle given two lower subtitles
                gap = next["start"] - last["end"]
                if gap < 500:
                    # Probably long upper split into two lower
                    last["end"] = next["start"] = last["end"] + (gap / 2)
                # Otherwise, probably upper repeated with different lower
                synced_list += [next]
        elif last["lower text"] == next["lower text"]:
            if isinstance(last["upper text"], float) and np.isnan(last["upper text"]):
                # Lower started before upper
                last["upper text"] = next["upper text"]
                last["end"] = next["end"]
            elif isinstance(next["upper text"], float) and np.isnan(next["upper text"]):
                # Upper started before lower
                if last.end < next["start"]:
                    synced_list += [next]
                else:
                    last["end"] = next["end"]
            else:
                gap = next["start"] - last["end"]
                if gap < 500:
                    # Probably long lower split into two upper
                    last["end"] = next["start"] = last["end"] + (gap / 2)
                # Otherwise, probably lower repeated with different upper
                synced_list += [next]
        else:
            synced_list += [next]
    synced_df = pd.DataFrame(synced_list)

    # Filter very short events
    # TODO: Do this interactively, somewhere else
    synced_df = synced_df.drop(
        index=synced_df[synced_df["end"] - synced_df["start"] < 300].index
    )

    return synced_df


def todo(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Decorator used to annotate unimplemented functions in a useful way."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    return wrapper
