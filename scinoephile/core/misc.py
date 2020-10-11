#!/usr/bin/env python
#   scinoephile.core.misc.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from typing import Any, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd
from IPython import embed

from scinoephile.common import input_prefill, validate_int
from scinoephile.core import SubtitleSeries


################################## FUNCTIONS ##################################
def sync_subtitles(
    mobile: pd.DataFrame, target: pd.DataFrame, mobile_i: int, target_i: int
) -> None:
    adjustment = int(
        np.mean((target.loc[target_i, "start"], target.loc[target_i, "end"]))
        - np.mean((mobile.loc[mobile_i, "start"], mobile.loc[mobile_i, "end"]))
    )

    mobile["start"] += adjustment
    mobile["end"] += adjustment


def align_iteration(
    mobile: pd.DataFrame,
    target: pd.DataFrame,
    aligned: Set[int],
    low_threshold: int = 0.25,
    mid_threshold: int = 0.60,
    high_threshold: int = 0.75,
    interactive: bool = False,
) -> int:
    CURSOR_UP = "\033[F"
    ERASE_LINE = "\033[K"

    def align(mobile_i: int, target_i: int):
        mobile.loc[mobile_i, "start"] = target.loc[target_i, "start"]
        mobile.loc[mobile_i, "end"] = target.loc[target_i, "end"]
        align.n_aligned += 1
        aligned.add(mobile_i)

    def get_confirmation_one(mobile_i: int, target_i: int, overlap: float) -> bool:
        confirmation = "y" if overlap >= low_threshold else "n"
        prompt = get_line(
            target_i,
            mobile_i,
            overlap,
            f"Align '{mobile.loc[mobile_i, 'text']}' to "
            f"'{target.loc[target_i, 'text']}' (y/n)?: ",
        )
        confirmation = input_prefill(prompt, confirmation)
        print(CURSOR_UP + ERASE_LINE + CURSOR_UP)

        return confirmation.lower().startswith("y")

    def get_confirmation_two(
        mobile_0_i: int,
        mobile_1_i: int,
        target_i: int,
        overlap_0: float,
        overlap_1: float,
    ) -> Union[bool, int]:
        confirmation = ""
        if overlap_0 > overlap_1 and overlap_0 >= low_threshold:
            confirmation = mobile_0_i + 1
        elif overlap_1 >= low_threshold:
            confirmation = mobile_1_i + 1
        prompt = get_line(
            target_i, mobile_0_i, overlap_0, f"'{mobile.loc[mobile_0_i, 'text']}'\n",
        ) + get_line(
            target_i,
            mobile_1_i,
            overlap_1,
            f"'{mobile.loc[mobile_1_i, 'text']}'  Align which subtitle to "
            f"'{target.loc[target_i, 'text']}'?: ",
        )
        confirmation = input_prefill(prompt, confirmation)
        try:
            confirmation = validate_int(
                confirmation, choices=(mobile_0_i + 1, mobile_1_i + 1)
            )
        except TypeError:
            confirmation = False
        print(CURSOR_UP + ERASE_LINE + CURSOR_UP + ERASE_LINE + CURSOR_UP)

        return confirmation

    def get_line(target_i: int, mobile_i: int, overlap: float, status: str = ""):
        return f"{target_i + 1:6d}  {mobile_i + 1:6d}  {overlap:7.2f}  {status}"

    def get_overlaps(mobile: pd.DataFrame, target: pd.DataFrame) -> pd.DataFrame:
        mobile_starts = mobile["start"].values
        mobile_ends = mobile["end"].values
        target_starts = target["start"].values
        target_ends = target["end"].values

        mobile_starts_tiled = np.tile(mobile_starts, (target_starts.size, 1))
        mobile_ends_tiled = np.tile(mobile_ends, (target_ends.size, 1))
        target_starts_tiled = np.transpose(
            np.tile(target_starts, (mobile_starts.size, 1))
        )
        target_ends_tiled = np.transpose(np.tile(target_ends, (mobile_ends.size, 1)))

        overlaps = (  # Numerator = First end - Last start
            np.minimum(mobile_ends_tiled, target_ends_tiled)
            - np.maximum(mobile_starts_tiled, target_starts_tiled)
        ) / (  # Denominator = Last end - First start
            np.maximum(mobile_ends_tiled, target_ends_tiled)
            - np.minimum(mobile_starts_tiled, target_starts_tiled)
        )
        overlaps[overlaps < 0] = 0

        return overlaps

    overlaps = get_overlaps(mobile, target)
    overlapping_pairs = np.squeeze(np.dstack(np.where(overlaps > 0)))
    align.n_aligned = 0

    print(f"Target  Mobile  Overlap  Status")
    for target_i in range(target.shape[0]):
        mobile_is = overlapping_pairs[overlapping_pairs[:, 0] == target_i][:, 1]

        # Zero overlapping matches
        if len(mobile_is) == 0:
            print(f"{target_i + 1:6d}                   Zero matches")

        # One overlapping match
        elif len(mobile_is) == 1:
            mobile_i = mobile_is[0]
            overlap = overlaps[target_i, mobile_i]

            # Already aligned
            if overlap == 1.0:
                status = (
                    f"Already aligned '{mobile.loc[mobile_i, 'text']}' to "
                    f"'{target.loc[target_i, 'text']}'"
                )
                aligned.add(mobile_i)

            # Automatically align
            elif overlap >= high_threshold:
                status = (
                    f"Automatically aligned '{mobile.loc[mobile_i, 'text']}' to "
                    f"'{target.loc[target_i, 'text']}' because "
                    f"{overlap:4.2f} ≥ {high_threshold:4.2f}"
                )
                align(mobile_i, target_i)

            # Interactive
            elif overlap >= mid_threshold and interactive:
                if get_confirmation_one(mobile_i, target_i, overlap):
                    status = (
                        f"User aligned '{mobile.loc[mobile_i, 'text']}' to "
                        f"'{target.loc[target_i, 'text']}'"
                    )
                    align(mobile_i, target_i)
                else:
                    status = "User chose not to align"

            # Otherwise, skip
            else:
                status = "Skipping..."

            # Print status
            print(get_line(target_i, mobile_i, overlap, status))

        # Two overlapping matches
        elif len(mobile_is) == 2:
            mobile_0_i, mobile_1_i = mobile_is
            overlap_0 = overlaps[target_i, mobile_0_i]
            overlap_1 = overlaps[target_i, mobile_1_i]

            # Already aligned
            if overlap_0 == 1.0:
                status = (
                    f"Already aligned '{mobile.loc[mobile_0_i, 'text']}' to "
                    f"'{target.loc[target_i, 'text']}'"
                )
                aligned.add(mobile_0_i)
            elif overlap_1 == 1.0:
                status = (
                    f"Already aligned '{mobile.loc[mobile_1_i, 'text']}' to "
                    f"'{target.loc[target_i, 'text']}'"
                )
                aligned.add(mobile_1_i)

            # Automatically align mobile 0 to target
            elif overlap_0 >= high_threshold:
                if overlap_1 < low_threshold:
                    status = (
                        f"Automatically aligned '{mobile.loc[mobile_0_i, 'text']}' to"
                        f"'{target.loc[target_i, 'text']}' because "
                        f"{overlap_0:4.2f} ≥ {high_threshold:4.2f} and "
                        f"{overlap_1:4.2f} < {low_threshold:4.2f}"
                    )
                    align(mobile_0_i, target_i)
                elif mobile_1_i in aligned:
                    status = (
                        f"Automatically aligned '{mobile.loc[mobile_0_i, 'text']}' to"
                        f"'{target.loc[target_i, 'text']}' because "
                        f"{overlap_0:4.2f} ≥ {high_threshold:4.2f} and "
                        f"{mobile_1_i} is already aligned"
                    )
                    align(mobile_0_i, target_i)
                else:
                    status = "Skipping..."
                    print(get_line(target_i, mobile_0_i, overlap_0, "."))
                    print(get_line(target_i, mobile_1_i, overlap_1, status))
                    embed()

            # Automatically align mobile 1 to target
            elif overlap_1 >= high_threshold:
                if overlap_0 < low_threshold:
                    status = (
                        f"Automatically aligned '{mobile.loc[mobile_1_i, 'text']}' to"
                        f"'{target.loc[target_i, 'text']}' because "
                        f"{overlap_1:4.2f} ≥ {high_threshold:4.2f} and "
                        f"{overlap_0:4.2f} < {low_threshold:4.2f}"
                    )
                    align(mobile_1_i, target_i)
                elif mobile_0_i in aligned:
                    status = (
                        f"Automatically aligned '{mobile.loc[mobile_1_i, 'text']}' to"
                        f"'{target.loc[target_i, 'text']}' because "
                        f"{overlap_1:4.2f} ≥ {high_threshold:4.2f} and "
                        f"{mobile_0_i} is already aligned"
                    )
                    align(mobile_1_i, target_i)
                else:
                    status = "In an unexpected state..."
                    print(get_line(target_i, mobile_0_i, overlap_0, "."))
                    print(get_line(target_i, mobile_1_i, overlap_1, status))
                    embed()

            # Interactive
            elif (
                overlap_0 >= mid_threshold or overlap_1 >= mid_threshold
            ) and interactive:
                confirmation = get_confirmation_two(
                    mobile_0_i, mobile_1_i, target_i, overlap_0, overlap_1
                )
                if confirmation == mobile_0_i + 1:
                    status = (
                        f"User aligned '{mobile.loc[mobile_0_i, 'text']}' to "
                        f"'{target.loc[target_i, 'text']}'"
                    )
                    align(mobile_0_i, target_i)
                elif confirmation == mobile_1_i + 1:
                    status = (
                        f"User aligned '{mobile.loc[mobile_1_i, 'text']}' to "
                        f"'{target.loc[target_i, 'text']}'"
                    )
                    align(mobile_1_i, target_i)
                else:
                    status = "User chose not to align"

            # Otherwise, skip
            else:
                status = "Skipping..."

            # print status
            print(get_line(target_i, mobile_0_i, overlap_0, "."))
            print(get_line(target_i, mobile_1_i, overlap_1, status))

        # Move than two overlapping matches
        else:
            for mobile_i in mobile_is:
                overlap = overlaps[target_i, mobile_i]
                print(get_line(target_i, mobile_i, overlap))

    return align.n_aligned


def align_subtitles(
    mobile: SubtitleSeries,
    target: SubtitleSeries,
    sync_pair: Optional[Tuple[int, int]] = None,
) -> pd.DataFrame:
    # Prepare
    mobile = mobile.get_dataframe()
    target = target.get_dataframe()
    if sync_pair is not None:
        sync_subtitles(mobile, target, sync_pair[0], sync_pair[1])
    aligned = set()

    # First set of iterations
    n_aligned = 1
    while n_aligned > 0:
        n_aligned = align_iteration(mobile, target, aligned, 0.25, 0.50, 0.75, False)
        input(f"{0.75:4.2f}, {n_aligned}, {len(aligned)}")

    # Second set of iterations
    n_aligned = 1
    while n_aligned > 0:
        try:
            n_aligned = align_iteration(mobile, target, aligned, 0.25, 0.50, 0.75, True)
        except KeyboardInterrupt:
            print()
            break
        input(f"{0.75:4.2f}, {n_aligned}, {len(aligned)}")

    #     if overlap[t_i, m1_i] > low_threshold:
    #         t_m = int((t_s + t_e) / 2)
    #         overlap_first_half = (min(m0_e, t_m) - max(m0_s, t_s)) / (
    #             max(m0_e, t_m) - min(m0_s, t_s)
    #         )
    #         overlap_second_half = (min(m1_e, t_e) - max(m1_s, t_m)) / (
    #             max(m1_e, t_e) - min(m1_s, t_m)
    #         )
    #         if overlap_first_half >= 0.25 and overlap_second_half >= 0.25:
    #             mobile.loc[m0_i, "start"] = target.loc[t_i, "start"]
    #             mobile.loc[m0_i, "end"] = t_m
    #             mobile.loc[m1_i, "start"] = t_m
    #             mobile.loc[m1_i, "start"] = target.loc[t_i, "end"]
    #         else:
    #             print(
    #                 f"    {overlap_first_half:4.2f} {overlap_second_half:4.2f}"
    #             )
    #             embed()
    #     elif overlap[t_i, m0_i] > high_threshold:
    #         mobile.loc[m0_i, ["start", "end"]] = target.loc[
    #             t_i, ["start", "end"]
    #         ]

    return SubtitleSeries.from_dataframe(mobile)


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
