#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLX-Audio tokenizer integration."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import cast

from scinoephile.core.dependencies.transcription import import_mlx_audio_mimo_asr
from scinoephile.core.ml import ModelSpec

__all__ = ["MIMO_AUDIO_TOKENIZER", "use_local_tokenizer"]

MIMO_AUDIO_TOKENIZER = ModelSpec(
    name="mlx-community/MiMo-Audio-Tokenizer",
    revision="6d451ed9a73024b4d33b87afa69e0dfd40d8f306",
)
"""Default MLX MiMo audio-tokenizer specification."""


@contextmanager
def use_local_tokenizer(
    tokenizer: ModelSpec, tokenizer_dir_path: Path
) -> Iterator[None]:
    """Make MLX-Audio use a pre-resolved auxiliary tokenizer directory.

    Arguments:
        tokenizer: auxiliary tokenizer specification
        tokenizer_dir_path: pinned local tokenizer directory
    """
    # Keep MLX-Audio from resolving the manifest's mutable tokenizer remotely
    mimo_asr = import_mlx_audio_mimo_asr()
    get_model_path = cast(Callable[..., Path], mimo_asr.get_model_path)

    def get_local_model_path(
        path_or_hf_repo: str, *args: object, **kwargs: object
    ) -> Path:
        """Resolve the configured tokenizer locally and delegate other models."""
        if path_or_hf_repo == tokenizer.name:
            return tokenizer_dir_path
        return get_model_path(path_or_hf_repo, *args, **kwargs)

    setattr(mimo_asr, "get_model_path", get_local_model_path)
    try:
        yield
    finally:
        setattr(mimo_asr, "get_model_path", get_model_path)
