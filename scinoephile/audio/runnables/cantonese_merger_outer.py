#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable that merges Cantonese subtitles into one."""

from __future__ import annotations

from langchain_core.runnables import Runnable, RunnableConfig

from scinoephile.audio import AudioSeries, AudioSubtitle
from scinoephile.audio.models import MergePayload, TranscriptionPayload
from scinoephile.audio.runnables.cantonese_merger_inner import CantoneseMergerInner
from scinoephile.core import ScinoephileException


class CantoneseMergerOuter(Runnable):
    """Runnable that merges Cantonese subtitles into one."""

    def __init__(self, inner: CantoneseMergerInner):
        self.inner = inner

    def invoke(
        self,
        input: TranscriptionPayload,
        config: RunnableConfig | None = None,
        **kwargs,
    ) -> TranscriptionPayload:
        zhongwen_subs = input["zhongwen_subs"]
        sync_groups = input["sync_groups"]
        yuewen_subs = input["yuewen_subs"]

        merged_yuewen_subs = AudioSeries()
        merged_yuewen_subs.audio = yuewen_subs.audio
        for i, sync_group in enumerate(sync_groups):
            zhongwen_indexes = [i - 1 for i in sync_group[0]]
            yuewen_indexes = [i - 1 for i in sync_group[1]]
            if len(zhongwen_indexes) != 1:
                raise ScinoephileException("Expected exactly one 中文 subtitle.")
            if len(yuewen_indexes) == 0:
                raise ScinoephileException("Expected at least one 粤文 subtitle.")
            zhongwen_sub = zhongwen_subs.events[zhongwen_indexes[0]]
            yat = "　".join(yuewen_subs.events[i].text.strip() for i in yuewen_indexes)
            print(f"Group {i:02d} | 中文: {zhongwen_sub.text} | 粤文: {yat}")
            if len(yuewen_indexes) == 1:
                yuewen_merged = yuewen_subs.events[yuewen_indexes[0]].text.strip()
            else:
                zhongwen = zhongwen_sub.text.strip()
                yuewen = [yuewen_subs.events[i].text.strip() for i in yuewen_indexes]
                payload = MergePayload(zhongwen=zhongwen, yuewen=yuewen)
                yuewen_merged = self.inner.invoke(payload)
                print(
                    f"Group {i:02d} | 中文: {zhongwen_sub.text} | 粤文: {yuewen_merged}"
                )
            merged_yuewen_subs.events.append(
                AudioSubtitle(
                    start=zhongwen_sub.start,
                    end=zhongwen_sub.end,
                    text=yuewen_merged,
                )
            )

        return TranscriptionPayload(
            zhongwen_subs=zhongwen_subs,
            yuewen_segments=input["yuewen_segments"],
            yuewen_subs=merged_yuewen_subs,
            sync_groups=sync_groups,
        )
