#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for syncing bilingual subtitles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import openai
import torch
import torchaudio
from langchain_core.runnables import Runnable, RunnableConfig
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, GenerationConfig

from scinoephile.audio import AudioSeries
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.testing import test_data_root

bluray_root = Path("/Volumes/Backup/Video/Disc")


class LocalWhisperTranscriber(Runnable):
    def __init__(self, model_name: str = "khleeloo/whisper-large-v3-cantonese"):
        self.device = self._select_device()
        self.model_name = model_name
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

    def _select_device(self):
        if torch.cuda.is_available():
            return torch.device("cuda")
        elif torch.backends.mps.is_available():
            return torch.device("mps")
        else:
            return torch.device("cpu")

    def invoke(
        self,
        input: Any,  # noqa: A002
        config: RunnableConfig | None = None,
        **kwargs,
    ) -> str:
        audio_block = input

        # Export audio block to a temp WAV file
        with get_temp_file_path(suffix=".wav") as temp_audio_path:
            audio_block.audio.export(temp_audio_path, format="wav")
            waveform, sr = torchaudio.load(temp_audio_path)
            waveform = waveform.numpy()

        # Preprocess and transcribe
        inputs = self.processor(
            waveform, sampling_rate=sr, return_tensors="pt", return_attention_mask=True
        ).to(self.device)

        generation_config = GenerationConfig.from_pretrained(self.model_name)
        generation_config.forced_decoder_ids = self.forced_decoder_ids

        with torch.no_grad():
            output = self.model.generate(
                inputs.input_features,
                attention_mask=inputs.attention_mask,
                generation_config=generation_config,
                return_dict_in_generate=True,
            )

        text = self.processor.batch_decode(output.sequences, skip_special_tokens=True)[
            0
        ]
        return text


class OpenAITranscriber(Runnable):
    def __init__(self, model: str = "gpt-4o-transcribe", language: str = "yue"):
        self.model = model
        self.language = language
        self.client = openai.OpenAI()

    def invoke(
        self,
        input: Any,  # noqa: A002
        config: RunnableConfig | None = None,
        **kwargs,
    ) -> str:
        audio_block = input

        with get_temp_file_path(suffix=".mp3") as temp_audio_path:
            audio_block.audio.export(temp_audio_path, format="mp3")

            with open(temp_audio_path, "rb") as f:
                transcript = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=f,
                    language=self.language,
                    response_format="text",
                )

        return transcript


if __name__ == "__main__":
    test_input_dir = test_data_root / "mlamd" / "input"
    test_output_dir = test_data_root / "mlamd" / "output"
    title = Path(__file__).parent.name
    set_logging_verbosity(2)

    # Cantonese
    subtitle_path = test_output_dir / "zho-Hans" / "zho-Hans.srt"
    video_path = bluray_root / "My Life as Mcdull.mkv"
    # yue_hans = AudioSeries.load(subtitle_path, video_path=video_path, audio_track=0)
    # yue_hans.save(test_output_dir / "yue-Hans_audio")
    yue_hans = AudioSeries.load(test_output_dir / "yue-Hans_audio")

    openai_transcriber = OpenAITranscriber(model="whisper-1", language="zh")
    whisper_transcriber = LocalWhisperTranscriber(
        # model_name="khleeloo/whisper-large-v3-cantonese"
        model_name="alvanlii/whisper-small-cantonese"
    )

    for i, block in enumerate(yue_hans.blocks, start=1):
        print(f"\n🧱 Block {i}: {block}")
        print("🔊 Audio:", block.audio)
        # openai_transcription = openai_transcriber.invoke(block)
        # print("📝 OpenAI Transcription:", openai_transcription)
        whisper_transcription = whisper_transcriber.invoke(block)
        print("📝 Whisper Transcription:", whisper_transcription)
        break
