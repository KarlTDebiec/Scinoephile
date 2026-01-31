#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OCR character validator."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import Any

import numpy as np
import paddle
import paddle.inference as paddle_infer
from huggingface_hub import snapshot_download
from PIL import Image

from scinoephile.core.text import whitespace_chars
from scinoephile.image.bbox import Bbox
from scinoephile.image.drawing import get_img_with_white_bg
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

__all__ = ["CharValidator"]

logger = getLogger(__name__)


class CharValidator:
    """OCR character validator."""

    def __init__(
        self,
        model_name: str = "saudadez/rec_chinese_char",
        paddle_model_dir: Path | str | None = None,
        hf_cache_dir: Path | str | None = None,
        predictor_config_kwargs: dict[str, Any] | None = None,
    ):
        """Initialize.

        Arguments:
            model_name: Hugging Face model name or local directory
            paddle_model_dir: local directory containing PaddleOCR model artifacts
            hf_cache_dir: directory used for Hugging Face model caching
            predictor_config_kwargs: extra keyword arguments applied to
                paddle.inference.Config when possible
        """
        self.model_name = model_name
        self._paddle_model_dir = Path(paddle_model_dir) if paddle_model_dir else None
        self._hf_cache_dir = Path(hf_cache_dir) if hf_cache_dir else None
        self._predictor_config_kwargs = predictor_config_kwargs or {}
        logger.info(f"Loading character recognition model {self.model_name}")
        self._model_root = self._resolve_model_root()
        self._model_dir = self._find_paddleocr_artifacts_dir(self._model_root)
        self._char_list = self._load_char_list(self._model_root)
        self._predictor = self._load_predictor()

    def _resolve_model_root(self) -> Path:
        """Resolve the directory containing model artifacts."""
        if self._paddle_model_dir is not None:
            return self._paddle_model_dir

        logger.info(f"Downloading Hugging Face model {self.model_name}")
        return Path(
            snapshot_download(
                repo_id=self.model_name,
                cache_dir=str(self._hf_cache_dir) if self._hf_cache_dir else None,
            )
        )

    @staticmethod
    def _find_paddleocr_artifacts_dir(snapshot_dir: Path) -> Path:
        """Find the directory containing PaddleOCR inference artifacts.

        Arguments:
            snapshot_dir: directory returned by Hugging Face snapshot_download
        Returns:
            directory containing inference.pdmodel and inference.pdiparams
        Raises:
            FileNotFoundError: If inference artifacts cannot be located
        """
        pdmodel_candidates = sorted(snapshot_dir.rglob("inference.pdmodel"))
        pdiparams_candidates = sorted(snapshot_dir.rglob("inference.pdiparams"))

        if not pdmodel_candidates or not pdiparams_candidates:
            raise FileNotFoundError(
                "Could not locate PaddleOCR inference artifacts under "
                f"{snapshot_dir}; expected inference.pdmodel and inference.pdiparams"
            )

        # Prefer directories that have both artifacts
        candidate_dirs = {
            path.parent
            for path in pdmodel_candidates
            if (path.parent / "inference.pdiparams").exists()
        }
        if len(candidate_dirs) == 1:
            return next(iter(candidate_dirs))
        if len(candidate_dirs) > 1:
            # Prefer paths that look like recognition-only models
            preferred = [
                d
                for d in sorted(candidate_dirs)
                if "rec" in d.as_posix().lower() and "det" not in d.as_posix().lower()
            ]
            return preferred[0] if preferred else sorted(candidate_dirs)[0]

        # Fallback: pick the first pdmodel's parent
        return pdmodel_candidates[0].parent

    @staticmethod
    def _load_char_list(model_root: Path) -> list[str]:
        """Load recognition character list.

        Arguments:
            model_root: directory containing rec_custom_keys.txt
        Returns:
            list of characters (without CTC blank)
        """
        candidates = sorted(model_root.rglob("rec_custom_keys.txt"))
        if not candidates:
            raise FileNotFoundError(
                f"Could not locate rec_custom_keys.txt under {model_root}"
            )
        chars = [line.rstrip("\n") for line in candidates[0].read_text().splitlines()]
        return [c for c in chars if c]

    def _load_predictor(self) -> paddle_infer.Predictor:
        """Load Paddle inference predictor for character recognition."""
        model_file = self._model_dir / "inference.pdmodel"
        params_file = self._model_dir / "inference.pdiparams"

        config = paddle_infer.Config(str(model_file), str(params_file))
        config.disable_glog_info()
        config.switch_ir_optim(True)

        if paddle.device.is_compiled_with_cuda():
            config.enable_use_gpu(100, 0)
        else:
            config.disable_gpu()

        for name, value in self._predictor_config_kwargs.items():
            method = getattr(config, name, None)
            if callable(method):
                if isinstance(value, (tuple, list)):
                    method(*value)
                else:
                    method(value)

        return paddle_infer.create_predictor(config)

    def validate(
        self,
        series: ImageSeries,
        stop_at_idx: int | None = None,
    ) -> ImageSeries:
        """Validate all characters in an image series using ML.

        Arguments:
            series: image series to validate
            stop_at_idx: stop validating at this index
        Returns:
            image series (unchanged, validation is for logging only)
        """
        if stop_at_idx is None:
            stop_at_idx = len(series) - 1

        messages = []
        for sub_idx, sub in enumerate(series.events):
            if sub_idx > stop_at_idx:
                break
            sub_messages, n_validated = self._validate_sub(sub, sub_idx)
            messages.extend(sub_messages)

        for message in messages:
            logger.warning(message)

        return series

    def _validate_sub(self, sub: ImageSubtitle, sub_idx: int) -> tuple[list[str], int]:
        """Validate all characters in a subtitle.

        Arguments:
            sub: subtitle to validate
            sub_idx: subtitle index for logging
        Returns:
            tuple of (validation messages, number of characters validated)
        """
        if sub.bboxes is None:
            return ([f"Sub {sub_idx:4d} | No bboxes; run BboxValidator first"], 0)

        messages = []
        validated_chars = 0

        expected_chars = [
            char
            for char in sub.text_with_newline
            if char not in whitespace_chars and char != "\n"
        ]
        if len(expected_chars) != len(sub.bboxes):
            messages.append(
                f"Sub {sub_idx:4d} | Char/bbox mismatch: "
                f"{len(expected_chars)} non-whitespace chars vs "
                f"{len(sub.bboxes)} bboxes"
            )

        text_bounds = self._get_text_bounds(sub.img)
        expanded_bboxes = self._expand_bboxes(sub.bboxes, text_bounds, sub.img.size)

        # Validate each bbox/character pair
        for bbox_idx, bbox in enumerate(expanded_bboxes):
            if bbox_idx >= len(expected_chars):
                break
            expected_char = expected_chars[bbox_idx]
            is_valid, predicted_char, _ = self._validate_character(
                sub.img, bbox, expected_char
            )
            validated_chars += 1

            if not is_valid:
                messages.append(
                    f"Sub {sub_idx:4d} | Bbox {bbox_idx:3d} | "
                    f"expected='{expected_char}', predicted='{predicted_char}'"
                )

        return messages, validated_chars

    def _validate_character(
        self, img: Image.Image, bbox: Bbox, expected_char: str
    ) -> tuple[bool, str, float]:
        """Validate a character using ML model.

        Arguments:
            img: full subtitle image
            bbox: bounding box for the character to validate
            expected_char: the expected character from OCR
        Returns:
            tuple of (is_valid, predicted_char, confidence).
            Note: confidence is currently a binary value (1.0 for match, 0.0 for
            mismatch). A more sophisticated confidence score would require accessing
            the model's logits, which is not currently implemented.
        """
        return self._validate_character_paddle_infer(img, bbox, expected_char)

    @staticmethod
    def _decode_ctc_greedy(
        probs: np.ndarray,
        char_list: list[str],
        blank_idx: int = 0,
    ) -> tuple[str, float]:
        """Greedy CTC decode.

        Arguments:
            probs: probability array with shape (T, C) or (1, T, C)
            char_list: list of characters (without CTC blank)
            blank_idx: index of blank label in CTC outputs
        Returns:
            tuple of (decoded text, confidence)
        """
        if probs.ndim == 3:
            probs = probs[0]
        if probs.ndim != 2:
            raise ValueError(f"Expected probs with ndim=2 or 3; got {probs.ndim}")

        best_indices = np.argmax(probs, axis=1).astype(int)
        best_scores = np.max(probs, axis=1).astype(float)

        decoded_chars: list[str] = []
        chosen_scores: list[float] = []
        prev = None
        for idx, score in zip(best_indices, best_scores, strict=False):
            if idx in (blank_idx, prev):
                prev = idx
                continue
            char_idx = idx - 1 if idx > blank_idx else idx
            if 0 <= char_idx < len(char_list):
                decoded_chars.append(char_list[char_idx])
                chosen_scores.append(float(score))
            prev = idx

        decoded = "".join(decoded_chars)
        confidence = max(chosen_scores) if chosen_scores else 0.0
        return decoded, confidence

    def _validate_character_paddle_infer(
        self, img: Image.Image, bbox: Bbox, expected_char: str
    ) -> tuple[bool, str, float]:
        """Validate a character using Paddle inference recognition.

        Arguments:
            img: full subtitle image
            bbox: bounding box for the character to validate
            expected_char: the expected character from OCR
        Returns:
            tuple of (is_valid, predicted_char, confidence).
        """
        char_img = self._prepare_single_char_image(img, bbox)

        arr = np.asarray(char_img, dtype=np.float32)
        bgr = arr[..., ::-1] / 255.0
        normalized = (bgr - 0.5) / 0.5
        chw = np.transpose(normalized, (2, 0, 1))
        input_tensor = np.expand_dims(chw, axis=0).astype(np.float32, copy=False)

        input_name = self._predictor.get_input_names()[0]
        input_handle = self._predictor.get_input_handle(input_name)
        input_handle.reshape(input_tensor.shape)
        input_handle.copy_from_cpu(input_tensor)
        self._predictor.run()

        output_name = self._predictor.get_output_names()[0]
        output_handle = self._predictor.get_output_handle(output_name)
        probs = output_handle.copy_to_cpu()
        text, score = self._decode_ctc_greedy(probs, self._char_list)

        predicted_char = text[:1] if text else ""
        is_valid = predicted_char == expected_char

        logger.info(
            f"Char validation: expected='{expected_char}', "
            f"predicted='{predicted_char}', is_valid={is_valid}"
        )
        return is_valid, predicted_char, score

    @staticmethod
    def _get_text_bounds(img: Image.Image) -> Bbox:
        """Get bounds of non-transparent pixels in a subtitle image.

        Arguments:
            img: subtitle image
        Returns:
            bounds of text pixels, or full image bounds if none found
        """
        arr = np.asarray(img)
        height, width = arr.shape[0], arr.shape[1]

        if arr.ndim == 3 and arr.shape[2] in (2, 4):
            alpha = arr[..., -1]
            mask = alpha > 0
        elif arr.ndim == 2:
            mask = arr > 0
        else:
            mask = np.any(arr != 0, axis=-1)

        ys, xs = np.where(mask)
        if len(xs) == 0 or len(ys) == 0:
            return Bbox(x1=0, x2=width, y1=0, y2=height)

        return Bbox(
            x1=int(xs.min()),
            x2=int(xs.max() + 1),
            y1=int(ys.min()),
            y2=int(ys.max() + 1),
        )

    @staticmethod
    def _expand_bboxes(
        bboxes: list[Bbox],
        text_bounds: Bbox,
        img_size: tuple[int, int],
    ) -> list[Bbox]:
        """Expand per-character bboxes to full subtitle extents.

        This assumes a single-line subtitle, and that the bbox list is in reading
        order (left-to-right).

        Arguments:
            bboxes: original bboxes (typically centered on each character)
            text_bounds: overall bounds of the subtitle's text pixels
            img_size: image size in pixels (width, height)
        Returns:
            expanded bboxes
        """
        img_width, img_height = img_size
        if not bboxes:
            return []

        expanded: list[Bbox] = []
        for i, bbox in enumerate(bboxes):
            if i == 0:
                x1 = text_bounds.x1
            else:
                prev = bboxes[i - 1]
                x1 = int(round((prev.x2 + bbox.x1) / 2))

            if i == len(bboxes) - 1:
                x2 = text_bounds.x2
            else:
                nxt = bboxes[i + 1]
                x2 = int(round((bbox.x2 + nxt.x1) / 2))

            x1 = max(0, min(x1, img_width - 1))
            x2 = max(x1 + 1, min(x2, img_width))
            y1 = max(0, min(text_bounds.y1, img_height - 1))
            y2 = max(y1 + 1, min(text_bounds.y2, img_height))

            expanded.append(Bbox(x1=x1, x2=x2, y1=y1, y2=y2))

        return expanded

    @staticmethod
    def _prepare_single_char_image(img: Image.Image, bbox: Bbox) -> Image.Image:
        """Extract a character crop and resize to 48x48.

        Arguments:
            img: full subtitle image
            bbox: expanded bbox for a single character
        Returns:
            48x48 RGB image on a white background
        """
        crop = img.crop((bbox.x1, bbox.y1, bbox.x2, bbox.y2))
        crop_white_bg = get_img_with_white_bg(crop)
        crop_rgb = crop_white_bg.convert("RGB")

        return crop_rgb.resize((48, 48), resample=Image.Resampling.LANCZOS)
