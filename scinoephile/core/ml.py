#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Machine learning helpers."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from .dependencies.transcription import import_huggingface_hub, import_torch

__all__ = ["ModelSpec", "get_huggingface_snapshot_dir_path", "get_torch_device"]


@dataclass(frozen=True, slots=True)
class ModelSpec:
    """Immutable Hugging Face model specification."""

    name: str
    """Hugging Face model name."""
    revision: str
    """Required immutable model revision."""


_HUGGINGFACE_MODEL_ALLOW_PATTERNS = (
    "*.ark",
    "*.bin",
    "*.jinja",
    "*.json",
    "*.jsonl",
    "*.model",
    "*.npy",
    "*.npz",
    "*.pth",
    "*.py",
    "*.safetensors",
    "*.tar",
    "*.tiktoken",
    "*.txt",
    "*.yaml",
    "*.yml",
)
"""Model asset patterns that exclude repository documentation and metadata."""


def get_huggingface_snapshot_dir_path(
    repo_id: str,
    revision: str | None = None,
    allow_patterns: Sequence[str] | None = None,
) -> Path:
    """Resolve a Hugging Face snapshot locally before allowing network access.

    Arguments:
        repo_id: Hugging Face repository ID
        revision: optional immutable repository revision
        allow_patterns: optional file patterns to include; defaults to model assets
    Returns:
        local snapshot directory path
    """
    huggingface_hub = import_huggingface_hub()
    snapshot_download = cast(Callable[..., str], huggingface_hub.snapshot_download)
    snapshot_kwargs: dict[str, object] = {"repo_id": repo_id}
    if revision is not None:
        snapshot_kwargs["revision"] = revision
    if allow_patterns is None:
        allow_patterns = _HUGGINGFACE_MODEL_ALLOW_PATTERNS
    snapshot_kwargs["allow_patterns"] = tuple(allow_patterns)
    try:
        snapshot_path = snapshot_download(local_files_only=True, **snapshot_kwargs)
    except OSError:
        snapshot_path = snapshot_download(**snapshot_kwargs)
    return Path(snapshot_path)


@cache
def get_torch_device() -> str:
    """Get torch device identifier.

    Returns:
        torch device identifier
    """
    torch = import_torch()
    if torch.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"
