import json
import os
from dataclasses import dataclass
from typing import Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


@dataclass
class Settings:
    fal_key: str | None
    elevenlabs_api_key: str | None
    elevenlabs_voice_id: str | None
    product_holding_model: str | None
    product_holding_extra_args: dict[str, Any]


def get_settings() -> Settings:
    extra_args_raw = os.getenv("PRODUCT_HOLDING_EXTRA_ARGS", "")
    extra_args: dict[str, Any] = {}
    if extra_args_raw:
        try:
            loaded = json.loads(extra_args_raw)
            if isinstance(loaded, dict):
                extra_args = loaded
        except json.JSONDecodeError:
            pass

    return Settings(
        fal_key=os.getenv("FAL_KEY"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
        product_holding_model=os.getenv("PRODUCT_HOLDING_MODEL", "fal-ai/image-apps-v2/product-holding"),
        product_holding_extra_args=extra_args,
    )


def ensure_env_for_fal(settings: Settings) -> None:
    if settings.fal_key and not os.getenv("FAL_KEY"):
        os.environ["FAL_KEY"] = settings.fal_key
