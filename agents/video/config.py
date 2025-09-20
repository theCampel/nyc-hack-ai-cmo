import os
from dataclasses import dataclass

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


def get_settings() -> Settings:
    return Settings(
        fal_key=os.getenv("FAL_KEY"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
    )


def ensure_env_for_fal(settings: Settings) -> None:
    if settings.fal_key and not os.getenv("FAL_KEY"):
        os.environ["FAL_KEY"] = settings.fal_key

