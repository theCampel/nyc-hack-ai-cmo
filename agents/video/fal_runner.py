from __future__ import annotations

from pathlib import Path
import base64
import os
import tempfile
from typing import Any, Optional, Tuple

import fal_client


DEFAULT_PRODUCT_HOLDING_PROMPT = "Blend the product naturally into the scene without making it the main focus."


def upload_file_to_fal(path: str) -> str:
    print(f"[fal_runner] uploading file to FAL: {path}", flush=True)
    url = fal_client.upload_file(path)
    if not url:
        raise RuntimeError("FAL file upload returned empty URL")
    print(f"[fal_runner] uploaded file url: {url}", flush=True)
    return url


_STATIC_ASSET_URL_CACHE: dict[str, str] = {}


def _get_static_asset_path(filename: str) -> Path:
    path = Path(__file__).with_name(filename)
    if not path.exists():
        raise FileNotFoundError(f"Static asset not found at {path}")
    return path


def _get_static_asset_url(filename: str) -> str:
    cached = _STATIC_ASSET_URL_CACHE.get(filename)
    if cached:
        return cached

    url = upload_file_to_fal(str(_get_static_asset_path(filename)))
    _STATIC_ASSET_URL_CACHE[filename] = url
    return url


def get_hardcoded_image_url() -> str:
    """Return the cached FAL URL for the bundled `test.jpeg` image."""

    return _get_static_asset_url("test.jpeg")


def get_product_image_url() -> str:
    """Return the cached FAL URL for the bundled `product.jpeg` image."""

    return _get_static_asset_url("product.jpeg")


def _looks_like_url(value: str) -> bool:
    return isinstance(value, str) and value.startswith(("http://", "https://", "s3://", "gs://"))


def _mime_to_extension(mime: Optional[str]) -> str:
    if not mime:
        return ".png"
    mapping = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/webp": ".webp",
    }
    return mapping.get(mime.lower(), ".png")


def _decode_data_uri(value: str) -> Optional[Tuple[bytes, Optional[str]]]:
    if not value or not value.startswith("data:"):
        return None
    header, _, data = value.partition(",")
    if not data:
        return None
    mime = None
    if ";" in header:
        mime = header.split(";", 1)[0].split(":", 1)[-1]
    elif header.startswith("data:"):
        mime = header.split(":", 1)[-1]
    try:
        decoded = base64.b64decode(data, validate=False)
    except Exception:
        return None
    return decoded, mime


def _decode_base64_blob(value: str) -> Optional[Tuple[bytes, Optional[str]]]:
    if not value or len(value) < 80:
        return None
    try:
        decoded = base64.b64decode(value, validate=True)
    except Exception:
        return None
    return decoded, None


def _extract_image_artifacts(payload: Any) -> Tuple[Optional[str], Optional[Tuple[bytes, Optional[str]]], Optional[str]]:
    if payload is None:
        return None, None, None

    if isinstance(payload, str):
        data_uri = _decode_data_uri(payload)
        if data_uri:
            return None, data_uri, None
        if _looks_like_url(payload):
            return payload, None, None
        if os.path.exists(payload):
            return None, None, payload
        decoded = _decode_base64_blob(payload)
        if decoded:
            return None, decoded, None
        return None, None, None

    if isinstance(payload, dict):
        for key in ("image_url", "url", "image", "images", "src", "signed_url"):
            if key in payload:
                url, blob, path = _extract_image_artifacts(payload[key])
                if url or blob or path:
                    return url, blob, path

        if "base64" in payload and isinstance(payload["base64"], str):
            decoded = _decode_base64_blob(payload["base64"])
            if decoded:
                mime = payload.get("content_type") or payload.get("mime_type")
                data, _ = decoded
                return None, (data, mime), None

        if "path" in payload and isinstance(payload["path"], str) and os.path.exists(payload["path"]):
            return None, None, payload["path"]

        if "file_path" in payload and isinstance(payload["file_path"], str) and os.path.exists(payload["file_path"]):
            return None, None, payload["file_path"]

    if isinstance(payload, (list, tuple)):
        for item in payload:
            url, blob, path = _extract_image_artifacts(item)
            if url or blob or path:
                return url, blob, path

    return None, None, None


def _save_bytes_to_temp(data: bytes, suffix: str) -> Path:
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as fp:
        fp.write(data)
    return Path(tmp_path)


def run_product_holding(
    *,
    model_id: Optional[str] = None,
    model_image_path: Optional[str | Path] = None,
    product_image_path: Optional[str | Path] = None,
    person_image_url: Optional[str] = None,
    product_image_url: Optional[str] = None,
    extra_arguments: Optional[dict[str, Any]] = None,
    wait: bool = True,
) -> dict[str, Any]:
    model_name = model_id or os.getenv("PRODUCT_HOLDING_MODEL", "fal-ai/image-apps-v2/product-holding")
    if not model_name:
        raise RuntimeError("Product Holding model is not configured; set PRODUCT_HOLDING_MODEL")

    # Handle person image - prioritize URL over path
    if person_image_url:
        person_url = person_image_url
    elif model_image_path:
        person_url = upload_file_to_fal(str(model_image_path))
    else:
        person_url = get_hardcoded_image_url()

    # Handle product image - prioritize URL over path
    if product_image_url:
        product_url = product_image_url
    elif product_image_path:
        product_url = upload_file_to_fal(str(product_image_path))
    else:
        product_url = get_product_image_url()

    arguments: dict[str, Any] = {
        "person_image_url": person_url,
        "product_image_url": product_url,
    }

    prompt = DEFAULT_PRODUCT_HOLDING_PROMPT
    if extra_arguments:
        merged = dict(extra_arguments)
        merged.pop("person_image_url", None)
        merged.pop("product_image_url", None)
        override = merged.pop("prompt", None)
        if isinstance(override, str) and override.strip():
            prompt = override
        arguments.update(merged)

    arguments.setdefault("prompt", prompt)

    print(
        f"[fal_runner] run_product_holding(model={model_name}, person_url={person_url}, product_url={product_url}, wait={wait})",
        flush=True,
    )

    if wait:
        def on_queue_update(update):
            if isinstance(update, fal_client.InProgress):
                for log in getattr(update, "logs", []) or []:
                    print(f"[fal_runner] product holding log: {log.get('message', '')}", flush=True)

        result = fal_client.subscribe(
            model_name,
            arguments=arguments,
            with_logs=True,
            on_queue_update=on_queue_update,
        )
    else:
        handler = fal_client.submit(
            model_name,
            arguments=arguments,
            webhook_url=None,
        )
        rid = handler.request_id
        print(f"[fal_runner] run_product_holding submitted request_id={rid}", flush=True)
        return {
            "request_id": rid,
            "model_image_url": person_url,
            "product_image_url": product_url,
        }

    print(
        f"[fal_runner] run_product_holding result keys: {list((result or {}).keys())}",
        flush=True,
    )

    urls: list[str] = []
    url, blob, local_path = _extract_image_artifacts(result)
    if url:
        urls.append(url)

    if isinstance(result, dict):
        images = result.get("images")
        if isinstance(images, (list, tuple)):
            for item in images:
                if isinstance(item, dict):
                    i_url = item.get("url")
                    if isinstance(i_url, str):
                        urls.append(i_url)

    uploaded_url: Optional[str] = urls[0] if urls else None
    temp_path: Optional[Path] = None

    if not uploaded_url and blob:
        data, mime = blob
        temp_path = _save_bytes_to_temp(data, _mime_to_extension(mime))
        uploaded_url = upload_file_to_fal(str(temp_path))

    elif not uploaded_url and local_path:
        uploaded_url = upload_file_to_fal(local_path)

    if temp_path is not None:
        try:
            temp_path.unlink(missing_ok=True)
        except Exception:
            pass

    return {
        "image_url": uploaded_url,
        "source_image_url": url,
        "source_local_path": local_path,
        "model_image_url": person_url,
        "product_image_url": product_url,
        "raw_result": result,
    }


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
