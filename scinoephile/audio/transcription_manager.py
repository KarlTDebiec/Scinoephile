#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages audio transcription."""

from __future__ import annotations

import time
from pathlib import Path
from platform import system

import torch
import torchaudio
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, GenerationConfig


class TranscriptionManager:
    """Manages audio transcription."""

    def __init__(self):
        """Initialize."""
        model_name = "khleeloo/whisper-large-v3-cantonese"
        self.device = torch.device("cpu")
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            use_safetensors=True,
            attn_implementation="sdpa",
        ).to(self.device)

        # Optional: force language = Cantonese
        self.forced_decoder_ids = self.processor.get_decoder_prompt_ids(
            language="yue", task="transcribe"
        )

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


if __name__ == "__main__":
    # For testing purposes, instantiate the TranscriptionManager
    mgr = TranscriptionManager()
    if system() == "Windows":
        infile = Path(
            r"C:\Users\karls\Code\ScinoephileProjects\scinoephile_projects\data"
            r"\Movies\My Life as McDull\output\yue-Hans_audio"
            r"\0001-0033_00048792-00158875.wav"
        )
    elif system() == "Darwin":
        infile = Path(
            "/Users/karldebiec/Code/ScinoephileProjects/scinoephile_projects/data"
            "/Movies/My Life as McDull/output/yue-Hans_audio"
            "/0001-0033_00048792-00158875.wav"
        )
    start_time = time.time()
    text = mgr.transcribe_file(infile)
    elapsed = time.time() - start_time

    print(f"Transcription:\n{text}")
    print(f"\nElapsed time: {elapsed:.2f} seconds")