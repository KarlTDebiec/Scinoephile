#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Maps transcript text to CTC tokenizer IDs."""

from __future__ import annotations

__all__ = ["get_token_ids"]


def get_token_ids(
    text: str, tokenizer: object, model_text: str | None = None
) -> tuple[list[int], list[int]]:
    """Get CTC token IDs and source text indices for supported characters.

    Arguments:
        text: transcription text
        tokenizer: Hugging Face tokenizer
        model_text: transcript converted to the model tokenizer's script
    Returns:
        token IDs and original character indices
    """
    token_ids: list[int] = []
    char_indices: list[int] = []
    alignment_text_end_idx = len(text.rstrip())
    for char_idx, char in enumerate(text):
        if char.isspace() and (
            char_idx == 0
            or text[char_idx - 1].isspace()
            or char_idx >= alignment_text_end_idx
        ):
            continue
        model_char = None
        if model_text is not None:
            model_char = model_text[char_idx]
        token_id = _get_token_id(char, model_char, tokenizer)
        if token_id is None:
            continue
        token_ids.append(token_id)
        char_indices.append(char_idx)
    return token_ids, char_indices


def _get_token_id(char: str, model_char: str | None, tokenizer: object) -> int | None:
    """Get a model token ID for one transcript character.

    Arguments:
        char: transcript character
        model_char: model-script character corresponding to the transcript
        tokenizer: Hugging Face tokenizer
    Returns:
        token ID, or None when the character cannot be aligned directly
    """
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

    candidates = [char, char.upper(), char.lower()]
    if model_char is not None:
        candidates.extend([model_char, model_char.upper(), model_char.lower()])

    if not callable(convert_tokens_to_ids):
        return None
    for candidate in dict.fromkeys(candidates):
        token_id = convert_tokens_to_ids(candidate)
        if isinstance(token_id, int) and token_id != unk_token_id:
            return token_id
    return None
