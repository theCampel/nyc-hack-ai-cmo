from __future__ import annotations

from pathlib import Path

import fal_client


def upload_file_to_fal(path: str) -> str:
    print(f"[fal_runner] uploading file to FAL: {path}", flush=True)
    url = fal_client.upload_file(path)
    if not url:
        raise RuntimeError("FAL file upload returned empty URL")
    print(f"[fal_runner] uploaded file url: {url}", flush=True)
    return url


# Cache for the hardcoded image upload so we don't re-upload each call.
_HARDCODED_IMAGE_URL: str | None = None


def get_hardcoded_image_url() -> str:
    """Upload the bundled 480x640 JPEG to FAL storage and return its URL.

    The image file lives next to this module as `test.jpeg`. We upload it
    once per process and cache the resulting URL for reuse, mirroring how we
    handle ElevenLabs audio uploads.
    """
    global _HARDCODED_IMAGE_URL
    if _HARDCODED_IMAGE_URL:
        return _HARDCODED_IMAGE_URL

    image_path = Path(__file__).with_name("test.jpeg")
    if not image_path.exists():
        raise FileNotFoundError(f"Hardcoded image not found at {image_path}")

    _HARDCODED_IMAGE_URL = upload_file_to_fal(str(image_path))
    return _HARDCODED_IMAGE_URL


def run_fabric(
    image_url: str,
    audio_url: str,
    resolution: str = "480p",
    wait: bool = True,
) -> dict:
    print(f"[fal_runner] run_fabric(image_url={image_url}, audio_url={audio_url}, resolution={resolution}, wait={wait})", flush=True)
    if wait:
        def on_queue_update(update):
            if isinstance(update, fal_client.InProgress):
                for log in update.logs:
                    print(f"[fal_runner] fal log: {log.get('message', '')}", flush=True)

        result = fal_client.subscribe(
            "veed/fabric-1.0",
            arguments={
                "image_url": image_url,
                "audio_url": audio_url,
                "resolution": resolution,
            },
            with_logs=True,
            on_queue_update=on_queue_update,
        )
        print(f"[fal_runner] subscribe result keys: {list((result or {}).keys())}", flush=True)
        return result or {}

    handler = fal_client.submit(
        "veed/fabric-1.0",
        arguments={
            "image_url": image_url,
            "audio_url": audio_url,
            "resolution": resolution,
        },
        webhook_url=None,
    )
    rid = handler.request_id
    print(f"[fal_runner] submitted request_id={rid}", flush=True)
    return {"request_id": rid}
