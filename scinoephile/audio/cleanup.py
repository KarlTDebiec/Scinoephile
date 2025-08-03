#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
import io
from warnings import catch_warnings, filterwarnings

import numpy as np
import torch
import torchaudio
from demucs.apply import apply_model
from demucs.pretrained import get_model

with catch_warnings():
    filterwarnings("ignore", category=SyntaxWarning)
    from pydub import AudioSegment


def extract_vocals_from_segment(segment: AudioSegment) -> AudioSegment:
    # Convert to stereo if mono
    if segment.channels == 1:
        segment = segment.set_channels(2)

    # Convert to 32-bit float PCM numpy array in range [-1, 1]
    samples = np.array(segment.get_array_of_samples()).astype(np.float32)
    samples /= np.iinfo(segment.array_type).max
    audio_np = samples.reshape((-1, segment.channels)).T  # Shape: [channels, samples]

    # Convert to torch tensor
    audio_tensor = torch.from_numpy(audio_np)

    # Load Demucs model
    model = get_model("htdemucs")
    model.device = "cuda" if torch.cuda.is_available() else "cpu"

    # Add batch dimension
    audio_tensor = audio_tensor.unsqueeze(0).to(
        model.device
    )  # Shape: [1, channels, samples]

    # Apply Demucs
    sources = apply_model(model, audio_tensor, split=True, progress=False)
    vocals = sources[0][model.sources.index("vocals")]  # Shape: [channels, samples]

    # Convert back to numpy array in int16 range
    vocals_np = vocals.cpu().numpy().T  # Shape: [samples, channels]
    vocals_np = np.clip(vocals_np, -1.0, 1.0)
    vocals_int16 = (vocals_np * 32767).astype(np.int16)

    # Create new AudioSegment from int16 data
    out_buf = io.BytesIO()
    torchaudio.save(
        out_buf, torch.tensor(vocals_int16).T, segment.frame_rate, format="wav"
    )
    out_buf.seek(0)
    vocal_segment = AudioSegment.from_file(out_buf, format="wav")

    vocal_segment = vocal_segment.set_channels(1)
    return vocal_segment
