#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to optical character recognition (OCR)."""

from __future__ import annotations

from logging import error, info, warning

from openai import OpenAIError

from scinoephile.core.blocks import get_blocks_by_pause, get_concatenated_series
from scinoephile.core.pairs import get_pair_blocks_by_pause
from scinoephile.image import ImageSeries
from scinoephile.image.base64 import get_base64_image
from scinoephile.openai import OpenAiService


def get_transcriptions(
    openai_service: OpenAiService,
    series: ImageSeries,
    language: str = "English",
) -> ImageSeries:
    """Get transcriptions of text from images.

    Arguments:
        openai_service: OpenAI service to use
        series: Image series to transcribe
        language: Language of text in images
    Returns:
        Series with transcriptions added
    """
    blocks: list[ImageSeries] = get_blocks_by_pause(series)

    j_offset = 1
    for i, block in enumerate(blocks):
        if i <= -1:
            info(f"Skipping block {i + 1} of {len(blocks)}")
            j_offset += len(block.events)
            continue
        # if i > 19:
        #     break

        info(f"Processing block {i + 1} of {len(blocks)}")
        for j, event in enumerate(block.events):
            info(f"Processing event {j + j_offset}, ({j + 1} / {len(block.events)})")
            image = event.img
            base64_image = get_base64_image(image)

            # Get initial transcription
            if event.text:
                transcription = event.text
            else:
                try:
                    transcription = openai_service.get_transcription(
                        base64_image, language
                    )
                except OpenAIError:
                    error("API connection error; returning results so far")
                    blocks[i] = block
                    return get_concatenated_series(blocks)
                event.text = transcription
            info(f"Initial transcription: {transcription}")

            # Get revised transcription
            rounds = 0
            while True:
                if rounds == 5:
                    warning(
                        "Completed 5 rounds of revision without convergence; "
                        f"using current transcription: {transcription}"
                    )
                    break

                try:
                    revision = openai_service.get_revision(
                        base64_image, transcription, language
                    )
                except OpenAIError:
                    error("API connection error; returning results so far")
                    blocks[i] = block
                    return get_concatenated_series(blocks)
                if revision == transcription:
                    info(f"No further revision of transcription: {transcription}")
                    break
                info(f"Revised transcription: {transcription} -> {revision}")
                event.text = revision
                transcription = revision
                rounds += 1

        # Update blocks
        blocks[i] = block
        j_offset += len(block.events)

    # Prepare output and return
    output = get_concatenated_series(blocks)
    return output


def get_revised_chinese_transcriptions(
    openai_service: OpenAiService,
    simp_series: ImageSeries,
    trad_series: ImageSeries,
    upscale=False,
) -> tuple[ImageSeries, ImageSeries]:
    """Use both Simplified and Traditional Chinese series to revise transcriptions.

    Arguments:
        openai_service: OpenAI service to use
        simp_series: Simplified Chinese image series
        trad_series: Traditional Chinese image series
        upscale: Whether to upscale images to 2000 pixels on the longest side
    Returns:
        Tuple of Simplified and Traditional Chinese series with revised transcriptions
    """
    block_pairs: list[tuple[ImageSeries, ImageSeries]] = get_pair_blocks_by_pause(
        simp_series, trad_series
    )
    simp_blocks = [block_pair[0] for block_pair in block_pairs]
    trad_blocks = [block_pair[1] for block_pair in block_pairs]

    j_offset = 1
    for i, (simp_block, trad_block) in enumerate(zip(simp_blocks, trad_blocks)):
        if i <= -1:
            info(f"Skipping block {i + 1} of {len(block_pairs)}")
            j_offset += len(simp_block.events)
            continue
        # if i > 0:
        #     break

        info(f"Processing block {i + 1} of {len(block_pairs)}")
        for j, (simp_event, trad_event) in enumerate(
            zip(simp_block.events, trad_block.events)
        ):
            info(
                f"Processing event {j + j_offset}, ({j + 1} / {len(simp_block.events)})"
            )
            simp_image = simp_event.img
            trad_image = trad_event.img
            simp_base64_image = get_base64_image(simp_image)
            trad_base64_image = get_base64_image(trad_image)
            simp_transcription = simp_event.text
            trad_transcription = trad_event.text

            # Get revised transcriptions
            rounds = 0
            while True:
                if rounds == 5:
                    warning(
                        "Completed 5 rounds of revision without convergence; "
                        "using current transcriptions: "
                        f"{simp_transcription}, {trad_transcription}"
                    )
                    break

                try:
                    simp_revision, trad_revision = (
                        openai_service.get_chinese_revision_pair(
                            simp_base64_image,
                            simp_transcription,
                            trad_base64_image,
                            trad_transcription,
                        )
                    )
                except OpenAIError:
                    error("API connection error; returning results so far")
                    simp_blocks[i] = simp_block
                    trad_blocks[i] = trad_block
                    return get_concatenated_series(
                        simp_blocks
                    ), get_concatenated_series(trad_blocks)
                if simp_revision == simp_transcription:
                    info(
                        "No further revision of Simplified Chinese transcription: "
                        f"{simp_transcription}"
                    )
                else:
                    info(
                        "Revised Simplified Chinese transcription: "
                        f"{simp_transcription} -> {simp_revision}"
                    )
                    simp_event.text = simp_revision

                if trad_revision == trad_transcription:
                    info(
                        "No further revision of Traditional Chinese transcription: "
                        f"{trad_transcription}"
                    )
                else:
                    info(
                        "Revised Traditional Chinese transcription: "
                        f"{trad_transcription} -> {trad_revision}"
                    )
                    trad_event.text = trad_revision

                if (
                    simp_revision == simp_transcription
                    and trad_revision == trad_transcription
                ):
                    break
                simp_transcription = simp_revision
                trad_transcription = trad_revision
                rounds += 1

        # Update blocks
        simp_blocks[i] = simp_block
        trad_blocks[i] = trad_block
        j_offset += len(simp_block.events)

    # Prepare output and return
    simp_output = get_concatenated_series(simp_blocks)
    trad_output = get_concatenated_series(trad_blocks)
    return simp_output, trad_output
