#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Maps transcript characters to CTC model tokens."""

from __future__ import annotations

from opencc import OpenCC

__all__ = ["get_token_ids"]


def get_token_ids(
    text: str, tokenizer: object, script_conversion_config: str | None
) -> tuple[list[int], list[int]]:
    """Get CTC token IDs and source text indices for supported characters.

    Arguments:
        text: transcription text
        tokenizer: Hugging Face tokenizer
        script_conversion_config: optional OpenCC configuration for model input
    Returns:
        token IDs and original character indices
    """
    # Convert text when the selected model uses a different Chinese script
    converted_text = None
    if script_conversion_config is not None:
        candidate_text = OpenCC(script_conversion_config).convert(text)
        if len(candidate_text) == len(text):
            converted_text = candidate_text

    # Map supported characters to model tokens while retaining source positions
    token_ids: list[int] = []
    char_indices: list[int] = []
    alignment_text_end_idx = len(text.rstrip())
    for char_idx, char in enumerate(text):
        # Align one delimiter per internal whitespace run
        if char.isspace() and (
            char_idx == 0
            or text[char_idx - 1].isspace()
            or char_idx >= alignment_text_end_idx
        ):
            continue
        converted_char = None
        if converted_text is not None:
            converted_char = converted_text[char_idx]
        token_id = _get_token_id(char, converted_char, tokenizer)
        if token_id is None:
            continue
        token_ids.append(token_id)
        char_indices.append(char_idx)
    return token_ids, char_indices


def _get_token_id(
    char: str, converted_char: str | None, tokenizer: object
) -> int | None:
    """Get an aligner token ID for one transcript character.

    Arguments:
        char: transcript character
        converted_char: model-script character corresponding to the transcript
        tokenizer: Hugging Face tokenizer
    Returns:
        token ID, or None when the character cannot be aligned directly
    """
    # Resolve tokenizer metadata and token conversion
    unk_token_id = getattr(tokenizer, "unk_token_id", None)
    convert_tokens_to_ids = getattr(tokenizer, "convert_tokens_to_ids", None)
    if char.isspace():
        word_delimiter_token_id = getattr(tokenizer, "word_delimiter_token_id", None)
        if (
            isinstance(word_delimiter_token_id, int)
            and word_delimiter_token_id != unk_token_id
        ):
            return word_delimiter_token_id

        word_delimiter_token = getattr(tokenizer, "word_delimiter_token", None)
        if isinstance(word_delimiter_token, str) and callable(convert_tokens_to_ids):
            token_id = convert_tokens_to_ids(word_delimiter_token)
            if isinstance(token_id, int) and token_id != unk_token_id:
                return token_id
        return None

    # Build case variants in preference order
    candidates = list(dict.fromkeys((char, char.upper(), char.lower())))

    # Add the model-specific script variant without changing the output text
    if converted_char is not None:
        candidates.extend(
            candidate
            for candidate in (
                converted_char,
                converted_char.upper(),
                converted_char.lower(),
            )
            if candidate not in candidates
        )

    # Return the first variant recognized by the tokenizer
    if not callable(convert_tokens_to_ids):
        return None
    for candidate in candidates:
        token_id = convert_tokens_to_ids(candidate)
        if isinstance(token_id, int) and token_id != unk_token_id:
            return token_id
    return None
