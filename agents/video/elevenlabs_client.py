from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

import requests

ELEVEN_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


class ElevenLabsError(RuntimeError):
    pass


def synthesize_speech_to_file(
    text: str,
    api_key: str,
    voice_id: Optional[str] = None,
    output_format: str = "mp3_44100_128",
    model_id: str = "eleven_multilingual_v2",
) -> Path:
    if not api_key:
        raise ElevenLabsError("Missing ELEVENLABS_API_KEY")

    voice = voice_id or os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    url = ELEVEN_TTS_URL.format(voice_id=voice)

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    params = {"output_format": output_format}
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }

    resp = requests.post(url, headers=headers, params=params, json=payload, stream=True, timeout=60)
    if resp.status_code != 200:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise ElevenLabsError(f"ElevenLabs TTS failed ({resp.status_code}): {detail}")

    suffix = ".mp3" if "mp3" in (output_format or "").lower() else ".audio"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as fp:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                fp.write(chunk)
        tmp_path = Path(fp.name)

    return tmp_path

