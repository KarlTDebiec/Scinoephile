#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of lazy Demucs dependency access."""

from __future__ import annotations

import builtins
from collections.abc import Mapping, Sequence

from pytest import MonkeyPatch, raises

from scinoephile.core.dependencies.transcription import import_demucs_infer_pretrained


def test_demucs_model_loader_requires_transcription_extra(monkeypatch: MonkeyPatch):
    """Test Demucs import errors mention the transcription extra."""
    original_import = builtins.__import__

    def import_without_demucs(
        name: str,
        globals: Mapping[str, object] | None = None,
        locals: Mapping[str, object] | None = None,
        fromlist: Sequence[str] | None = (),
        level: int = 0,
    ) -> object:
        if name.split(".", 1)[0] == "demucs_infer":
            raise ImportError("blocked optional dependency")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_without_demucs)

    with raises(ImportError, match="'transcription' extra"):
        import_demucs_infer_pretrained()
