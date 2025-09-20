from __future__ import annotations

import os
from typing import Optional, Literal

from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

from config import get_settings, ensure_env_for_fal
from elevenlabs_client import synthesize_speech_to_file, ElevenLabsError
from fal_runner import upload_file_to_fal, run_fabric, get_hardcoded_image_url


class GenerateVideoArgs(BaseModel):
    text: str = Field(..., description="Text to synthesize with ElevenLabs")
    image_url: Optional[str] = Field(
        default=None,
        description=(
            "Image URL used as the video background. If omitted, the agent "
            "uploads its bundled 480x640 JPEG to FAL and uses that."
        ),
    )
    resolution: Literal["480p", "720p"] = Field(
        default="480p",
        description="Video resolution; one of: 480p, 720p",
    )
    voice_id: Optional[str] = Field(
        default=None,
        description="Optional ElevenLabs voice ID (overrides env)",
    )
    wait: bool = Field(
        default=True,
        description="If true, wait for video and return final URL; otherwise return request_id",
    )


def _generate_video_impl(
    text: str,
    image_url: Optional[str] = None,
    resolution: str = "480p",
    voice_id: Optional[str] = None,
    wait: bool = True,
) -> str:
    settings = get_settings()
    ensure_env_for_fal(settings)

    print(
        f"[video.generate_video] env: FAL_KEY={'yes' if settings.fal_key else 'no'}, ELEVENLABS_API_KEY={'yes' if settings.elevenlabs_api_key else 'no'}, voice_id={(voice_id or settings.elevenlabs_voice_id)}",
        flush=True,
    )

    # Resolve image_url: if not provided, upload our bundled JPEG to FAL.
    if not image_url:
        try:
            image_url = get_hardcoded_image_url()
        except Exception as e:
            print(f"[video.generate_video] failed to get hardcoded image url: {e}", flush=True)
            return f"ERROR: Failed to upload bundled image to FAL: {e}"
    print(f"[video.generate_video] using image_url={image_url}", flush=True)

    if not settings.elevenlabs_api_key:
        return "ERROR: ELEVENLABS_API_KEY is not set"

    # ElevenLabs only (no fallback)
    try:
        print("[video.generate_video] synthesizing audio via ElevenLabs...", flush=True)
        audio_path = synthesize_speech_to_file(
            text=text,
            api_key=settings.elevenlabs_api_key,
            voice_id=voice_id or settings.elevenlabs_voice_id,
            output_format="mp3_44100_128",
        )
        print(f"[video.generate_video] audio_path={audio_path}", flush=True)
    except ElevenLabsError as e:
        print(f"[video.generate_video] ElevenLabs failed: {e}", flush=True)
        return (
            "ERROR: ElevenLabs TTS failed. Ensure the key has text_to_speech permission and the voice is accessible. "
            f"Detail: {e}"
        )

    print("[video.generate_video] uploading audio to FAL storage...", flush=True)
    audio_url = upload_file_to_fal(str(audio_path))
    print(f"[video.generate_video] audio_url={audio_url}", flush=True)

    print("[video.generate_video] submitting veed/fabric-1.0 job...", flush=True)
    try:
        result = run_fabric(
            image_url=image_url,
            audio_url=audio_url,
            resolution=resolution,
            wait=wait,
        )
    except Exception as e:
        print(f"[video.generate_video] FAL job submission failed: {e}", flush=True)
        return f"ERROR: FAL video job failed: {e}"
    print(f"[video.generate_video] fal_result keys={list((result or {}).keys())}", flush=True)

    if wait:
        video = (result or {}).get("video", {})
        url = video.get("url")
        if url:
            print(f"[video.generate_video] success video_url={url}", flush=True)
            return url
        print(f"[video.generate_video] no video url in result: {result}", flush=True)
        return f"No video URL returned. Full result: {result}"
    else:
        rid = result.get('request_id') if isinstance(result, dict) else None
        print(f"[video.generate_video] submitted request_id={rid}", flush=True)
        return f"request_id={rid}"


def get_video_tools() -> list[StructuredTool]:
    tool = StructuredTool.from_function(
        func=_generate_video_impl,
        name="generate_video",
        description=(
            "Generate a narrated video from text using ElevenLabs (TTS) and FAL veed/fabric-1.0. "
            "Inputs: text, image_url, resolution (480p|720p), optional voice_id, wait (bool)."
        ),
        args_schema=GenerateVideoArgs,
        return_direct=False,
    )
    return [tool]
