#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages audio transcription."""

from __future__ import annotations

import time
from logging import info
from pathlib import Path
from platform import system

import numpy as np
import torch
import torchaudio
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, GenerationConfig

from scinoephile.audio import AudioSeries, AudioSubtitle
from scinoephile.common.file import get_temp_directory_path
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.common.typing import PathLike
from scinoephile.common.validation import validate_input_directory, validate_input_file
from pydub import AudioSegment


class TranscriptionManager:
    """Manages audio transcription."""

    def __init__(
        self,
        input_dir_path: PathLike,
    ):
        """Initialize.

        Arguments:
            input_dir_path: Directory containing audio series to transcribe
        """
        self.series_dir_path = validate_input_directory(input_dir_path)
        self.series_path = validate_input_file(
            self.series_dir_path / f"{self.series_dir_path.name}.srt"
        )
        self.series = AudioSeries.load(input_dir_path)

        # Select device
        self.device = torch.device("cpu")
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
            info("Using MPS device for Apple Silicon")

        # Prepare model and processor
        self.model_name = "khleeloo/whisper-large-v3-cantonese"
        self.processor = AutoProcessor.from_pretrained(self.model_name)
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_name,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            use_safetensors=True,
            attn_implementation="sdpa",
        ).to(self.device)
        self.forced_decoder_ids = self.processor.get_decoder_prompt_ids(
            language="yue", task="transcribe"
        )

    def transcribe(self) -> None:
        """Transcribe all audio blocks in the loaded series."""
        for i, (block_audio, (start_idx, end_idx, _, _)) in enumerate(
            zip(self.series.block_audio, self.series.block_specs), 1
        ):
            info(f"Transcribing block {i}: subtitles {start_idx} to {end_idx}")
            block_events = self.series.events[start_idx - 1 : end_idx]
            self._transcribe_block(block_audio, block_events)

    def _transcribe_block(self, block_audio, block_events: list[AudioSubtitle]) -> None:
        """Transcribe a single block of audio and assign text to events."""
        with get_temp_directory_path() as temp_dir:
            temp_path = temp_dir / "block.wav"
            block_audio.export(temp_path, format="wav")
            text = self.transcribe_file(temp_path)

        # Naively split transcription across events
        words = text.split()
        n_events = len(block_events)
        chunk_size = max(1, len(words) // n_events)

        for i, event in enumerate(block_events):
            start = i * chunk_size
            end = (i + 1) * chunk_size if i < n_events - 1 else len(words)
            event.text = " ".join(words[start:end])

    def transcribe_file(self, wav_path: Path) -> str:
        waveform, sr = torchaudio.load(wav_path)
        y = waveform.numpy()

        inputs = self.processor(
            y, sampling_rate=sr, return_tensors="pt", return_attention_mask=True
        ).to(self.device)

        # Create generation config with forced decoder ids
        generation_config = GenerationConfig.from_pretrained(self.model.name_or_path)
        generation_config.forced_decoder_ids = self.processor.get_decoder_prompt_ids(
            language="yue", task="transcribe"
        )

        # Generate transcription
        with torch.no_grad():
            output = self.model.generate(
                inputs.input_features,
                attention_mask=inputs.attention_mask,
                generation_config=generation_config,
                return_dict_in_generate=True,
            )

        # Decode output
        text = self.processor.batch_decode(output.sequences, skip_special_tokens=True)[
            0
        ]
        return text

    @staticmethod
    def audiosegment_to_tensor(audio: AudioSegment) -> tuple[torch.Tensor, int]:
        """Convert pydub AudioSegment to a torch.Tensor and sample rate."""
        samples = np.array(audio.get_array_of_samples())
        if audio.channels > 1:
            samples = samples.reshape((-1, audio.channels)).T  # shape: (channels, time)
        else:
            samples = samples[np.newaxis, :]  # shape: (1, time)

        tensor = torch.from_numpy(samples).float() / (1 << (8 * audio.sample_width - 1))
        return tensor, audio.frame_rate


# if __name__ == "__main__":
#     set_logging_verbosity(2)
#     mgr = TranscriptionManager()
#     if system() == "Windows":
#         infile = Path(
#             r"C:\Users\karls\Code\ScinoephileProjects\scinoephile_projects\data"
#             r"\Movies\My Life as McDull\output\yue-Hans_audio"
#             r"\0001-0033_00048792-00158875.wav"
#         )
#     elif system() == "Darwin":
#         infile = Path(
#             "/Users/karldebiec/Code/ScinoephileProjects/scinoephile_projects/data"
#             "/Movies/My Life as McDull/output/yue-Hans_audio"
#             "/0001-0033_00048792-00158875.wav"
#         )
#     start_time = time.time()
#     text = mgr.transcribe_file(infile)
#     elapsed = time.time() - start_time
#
#     print(f"Transcription:\n{text}")
#     print(f"\nElapsed time: {elapsed:.2f} seconds")
