#!/usr/bin/env python
#   scinoephile.core.misc.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from collections import OrderedDict
from typing import Any, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd

from scinoephile.common import input_prefill, validate_int
from scinoephile.core import SubtitleSeries, get_pinyin


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
    targets_aligned: Set[int],
    mobiles_aligned: Set[int],
    interactive: bool = False,
) -> int:
    CURSOR_UP = "\033[F"
    ERASE_LINE = "\033[K"
    min_cut: int = 0.05
    low_cut: int = 0.25
    diff_cut = 0.40
    high_cut: int = 0.75

    def align(mobile_i: int, target_i: int) -> None:
        mobile.loc[mobile_i, "start"] = target.loc[target_i, "start"]
        mobile.loc[mobile_i, "end"] = target.loc[target_i, "end"]
        align.n_aligned += 1
        targets_aligned.add(target_i)
        mobiles_aligned.add(mobile_i)

    def align_two_target_one_mobile(
        mobile_i: int, target_0_i: int, target_1_i: int
    ) -> None:
        mobile.loc[mobile_i, "start"] = target.loc[target_0_i, "start"]
        mobile.loc[mobile_i, "end"] = target.loc[target_1_i, "end"]
        midpoint = int(
            (target.loc[target_0_i, "start"] + target.loc[target_1_i, "end"]) / 2
        )
        target.loc[target_0_i, "end"] = midpoint
        target.loc[target_0_i, "start"] = midpoint
        align.n_aligned += 1
        targets_aligned.add(target_0_i)
        targets_aligned.add(target_1_i)
        mobiles_aligned.add(mobile_i)

    def align_one_target_two_mobbile():
        pass

    def get_confirmation_one(mobile_i: int, target_i: int, overlap: float) -> bool:
        confirmation = "y" if overlap >= low_cut else "n"
        prompt = get_line(
            target_i,
            mobile_i,
            overlap,
            f"Align '{mobile.loc[mobile_i, 'text']}' to "
            f"'{target.loc[target_i, 'text']}' "
            f"({get_pinyin(target.loc[target_i, 'text'])}) "
            f"(y/n)?: ",
        )
        confirmation = input_prefill(prompt, confirmation)
        print(CURSOR_UP + ERASE_LINE + CURSOR_UP)

        return confirmation.lower().startswith("y")

    def get_confirmation_two_target_one_mobile_merge(
        mobile_i: int, target_0_i: int, target_1_i: int
    ) -> str:
        mobile_text = mobile.loc[mobile_i, "text"]
        target_0_text = target.loc[target_0_i, "text"]
        target_1_text = target.loc[target_1_i, "text"]
        target_0_overlap = overlaps[target_0_i, mobile_i]
        target_1_overlap = overlaps[target_1_i, mobile_i]

        confirmation = "n"
        if np.abs(target_0_overlap - target_1_overlap) < low_cut:
            confirmation = "y"
        prompt = get_line(target_0_i, mobile_i, target_0_overlap)
        prompt += f"'{target_0_text}'\n"
        prompt += get_line(target_1_i, mobile_i, target_1_overlap)
        prompt += f"'{target_1_text}'\n"
        prompt += f"{' ' * 25}Align '{mobile_text}' to these two subtitles?: "

        confirmation = input_prefill(prompt, confirmation)
        print(
            f"{CURSOR_UP}{ERASE_LINE}{CURSOR_UP}{ERASE_LINE}{CURSOR_UP}{ERASE_LINE}"
            f"{CURSOR_UP}"
        )

        return confirmation.lower().startswith("y")

    def get_confirmation_one_target_two_mobile(
        mobile_0_i: int, mobile_1_i: int, target_i: int,
    ) -> Union[bool, int]:
        mobile_0_text = mobile.loc[mobile_0_i, "text"]
        mobile_1_text = mobile.loc[mobile_1_i, "text"]
        target_text = target.loc[target_i, "text"]
        mobile_0_overlap = overlaps[target_i, mobile_0_i]
        mobile_1_overlap = overlaps[target_i, mobile_1_i]

        confirmation = ""
        if mobile_0_overlap > mobile_1_overlap and mobile_0_overlap >= low_cut:
            confirmation = mobile_0_i + 1
        elif mobile_1_overlap >= low_cut:
            confirmation = mobile_1_i + 1
        prompt = get_line(target_i, mobile_0_i, mobile_0_overlap)
        prompt += f"'{mobile_0_text}'\n"
        prompt += get_line(target_i, mobile_1_i, mobile_1_overlap,)
        prompt += f"'{mobile_1_text}'\n"
        prompt += f"{' ' * 25}Align '{target_text}' "
        prompt += f"({get_pinyin(target.loc[target_i, 'text'])}) to which subtitle?: "

        confirmation = input_prefill(prompt, confirmation)
        try:
            confirmation = validate_int(
                confirmation, choices=(mobile_0_i + 1, mobile_1_i + 1)
            )
        except TypeError:
            confirmation = False
        print(
            f"{CURSOR_UP}{ERASE_LINE}{CURSOR_UP}{ERASE_LINE}{CURSOR_UP}{ERASE_LINE}"
            f"{CURSOR_UP}"
        )

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
        overlaps[overlaps < min_cut] = 0

        return overlaps

    overlaps = get_overlaps(mobile, target)
    pairs = np.squeeze(np.dstack(np.where(overlaps > 0)))
    mobile_to_target = OrderedDict()
    for mobile_0_i in range(mobile.shape[0]):
        mobile_to_target[mobile_0_i] = pairs[pairs[:, 1] == mobile_0_i][:, 0]
    target_to_mobile = OrderedDict()
    for target_0_i in range(target.shape[0]):
        target_to_mobile[target_0_i] = pairs[pairs[:, 0] == target_0_i][:, 1]

    align.n_aligned = 0

    print(f"Target  Mobile  Overlap  Status")
    for target_0_i in range(0, 200):
        # for target_0_i in range(target.shape[0]):
        target_0_text = target.loc[target_0_i, "text"]

        # Zero overlapping mobiles
        if target_0_i not in target_to_mobile:
            print(f"{target_0_i + 1:6d}{' ' * 19}'{target_0_text}' does not overlap")
            continue

        mobile_is = target_to_mobile[target_0_i]

        # One overlapping mobile
        if len(mobile_is) == 1:
            mobile_0_i = mobile_is[0]
            mobile_0_text = mobile.loc[mobile_0_i, "text"]
            mobile_0_target_is = mobile_to_target[mobile_0_i]
            mobile_0_overlap = overlaps[target_0_i, mobile_0_i]

            # Already aligned
            if mobile_0_overlap == 1.0:
                status = f"Already aligned '{mobile_0_text}' to '{target_0_text}'"
                targets_aligned.add(target_0_i)
                mobiles_aligned.add(mobile_0_i)

            # This target's single matching mobile also overlaps only this target
            elif len(mobile_0_target_is) == 1:
                status = (
                    f"Automatically aligned '{mobile_0_text}' to '{target_0_text}' "
                    f"because they are a unique pair"
                )
                align(mobile_0_i, target_0_i)

            # This target's single matching mobile overlaps with one other target
            elif len(mobile_0_target_is) == 2:
                target_1_i = mobile_0_target_is[mobile_0_target_is != target_0_i][0]
                target_1_overlap = overlaps[target_1_i, mobile_0_i]
                target_1_text = target.loc[target_1_i, "text"]

                # Automatically align based on process of elimination
                if target_1_i in targets_aligned and target_0_i not in targets_aligned:
                    status = (
                        f"Automatically aligned '{mobile_0_text}' to '{target_0_text}' "
                        f"by process of elimination"
                    )
                    align(mobile_0_i, target_0_i)

                # Automatically align based on threshold
                elif mobile_0_overlap - target_1_overlap >= diff_cut:
                    status = (
                        f"Automatically aligned '{mobile_0_text}' to '{target_0_text}' "
                        f"because {mobile_0_overlap:4.2f} - {target_1_overlap:4.2f} "
                        f"≥ {diff_cut:4.2f}"
                    )
                    align(mobile_0_i, target_0_i)

                # Already aligned
                elif {target_0_i, target_1_i}.issubset(targets_aligned):
                    status = (
                        f"Already aligned '{mobile_0_text}' to both "
                        f"'{target_0_text}' and '{target_1_text}'"
                    )

                # Align two mobile subtitles into this target
                elif np.abs(mobile_0_overlap - target_1_overlap) < low_cut:
                    status = (
                        f"Automatically aligned '{mobile_0_text}' to both "
                        f"'{target_0_text}' and '{target_1_text}' "
                        f"because {mobile_0_overlap:4.2f} - {target_1_overlap:4.2f} "
                        f"= {np.abs(mobile_0_overlap - target_1_overlap):4.2f} "
                        f"< {low_cut:4.2f}"
                    )
                    align_two_target_one_mobile(mobile_0_i, target_0_i, target_1_i)

                # Interactive
                elif interactive:
                    confirmation = get_confirmation_two_target_one_mobile_merge(
                        mobile_0_i, target_0_i, target_1_i
                    )
                    if confirmation:
                        status = (
                            f"User chose to align '{mobile_0_text}' to both "
                            f"'{target_0_text}' and '{target_1_text}'"
                        )
                        align_two_target_one_mobile(mobile_0_i, target_0_i, target_1_i)
                    else:
                        status = (
                            f"User chose not to align '{mobile_0_text}' to both "
                            f"'{target_0_text}' and '{target_1_text}'"
                        )

                # Otherwise, skip
                else:
                    status = (
                        f"Skipping... 1.1 "
                        f"{mobile_0_overlap:4.2f} {target_1_overlap:4.2f} "
                        f"{np.abs(mobile_0_overlap - target_1_overlap):4.2f}"
                    )

            # This target's single matching mobile also overlaps with two other targets
            elif len(mobile_0_target_is) == 3:
                target_1_i = mobile_0_target_is[mobile_0_target_is != target_0_i][0]
                target_1_overlap = overlaps[target_1_i, mobile_0_i]
                target_2_i = mobile_0_target_is[mobile_0_target_is != target_0_i][1]
                target_2_overlap = overlaps[target_2_i, mobile_0_i]

                # Automatically align based on process of elimination
                if {target_1_i, target_2_i}.issubset(targets_aligned):
                    status = (
                        f"Automatically aligned '{mobile_0_text}' to '{target_0_text}' "
                        f"by process of elimination"
                    )
                    align(mobile_0_i, target_0_i)

                # Otherwise, skip
                else:
                    status = (
                        f"Skipping... 1.2 "
                        f"{mobile_0_overlap:4.2f} {target_1_overlap:4.2f} "
                        f"{target_2_overlap:4.2f}"
                    )

            # Otherwise, skip
            else:
                status = "Skipping... 1.3"

            # Print status
            print(get_line(target_0_i, mobile_0_i, mobile_0_overlap, status))

        # Two overlapping mobiles
        elif len(mobile_is) == 2:
            mobile_0_i, mobile_1_i = mobile_is
            mobile_0_text = mobile.loc[mobile_0_i, "text"]
            mobile_1_text = mobile.loc[mobile_1_i, "text"]
            mobile_0_target_is = mobile_to_target[mobile_0_i]
            mobile_1_target_is = mobile_to_target[mobile_1_i]
            mobile_0_overlap = overlaps[target_0_i, mobile_0_i]
            mobile_1_overlap = overlaps[target_0_i, mobile_1_i]

            # Already aligned
            if mobile_0_overlap == 1.0:
                status = f"Already aligned '{mobile_0_text}' to '{target_0_text}'"
                targets_aligned.add(target_0_i)
                mobiles_aligned.add(mobile_0_i)
            elif mobile_1_overlap == 1.0:
                status = f"Already aligned '{mobile_1_text}' to '{target_0_text}'"
                targets_aligned.add(target_0_i)
                mobiles_aligned.add(mobile_1_i)

            # Automatically align mobile 0 to target
            elif mobile_0_overlap - mobile_1_overlap >= diff_cut:
                status = (
                    f"Automatically aligned '{mobile_0_text}' to '{target_0_text}' "
                    f"because {mobile_0_overlap:4.2f} - {mobile_1_overlap:4.2f} "
                    f"≥ {diff_cut:4.2f}"
                )
                align(mobile_0_i, target_0_i)

            # Automatically align mobile 1 to target
            elif mobile_1_overlap - mobile_0_overlap >= diff_cut:
                status = (
                    f"Automatically aligned '{mobile_1_text}' to '{target_0_text}' "
                    f"because {mobile_1_overlap:4.2f} - {mobile_0_overlap:4.2f} "
                    f"≥ {diff_cut:4.2f}"
                )
                align(mobile_1_i, target_0_i)

            # Interactive
            elif interactive:
                confirmation = get_confirmation_one_target_two_mobile(
                    mobile_0_i, mobile_1_i, target_0_i,
                )
                if confirmation == mobile_0_i + 1:
                    status = f"User aligned '{mobile_0_text}' to '{target_0_text}'"
                    align(mobile_0_i, target_0_i)
                elif confirmation == mobile_1_i + 1:
                    status = f"User aligned '{mobile_0_text}' to '{target_0_text}'"
                    align(mobile_1_i, target_0_i)
                else:
                    status = "User chose not to align"

            # Otherwise, skip
            else:
                status = "Skipping... 2"

            # print status
            print(get_line(target_0_i, mobile_0_i, mobile_0_overlap, "."))
            print(get_line(target_0_i, mobile_1_i, mobile_1_overlap, status))

        # Move than two overlapping matches
        else:
            for mobile_i in mobile_is:
                overlap = overlaps[target_0_i, mobile_i]
                print(get_line(target_0_i, mobile_i, overlap))

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
    targets_aligned = set()
    mobiles_aligned = set()

    # First set of iterations
    n_aligned = 1
    while n_aligned > 0:
        n_aligned = align_iteration(mobile, target, targets_aligned, mobiles_aligned)
        input(f"{0.75:4.2f}, {n_aligned}, {len(mobiles_aligned)}")

    # Second set of iterations
    n_aligned = 1
    while n_aligned > 0:
        try:
            n_aligned = align_iteration(
                mobile, target, targets_aligned, mobiles_aligned, True
            )
        except KeyboardInterrupt:
            print()
            break
        input(f"{0.75:4.2f}, {n_aligned}, {len(mobiles_aligned)}")

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
    synced_df = synced_df.dropna()

    return synced_df
