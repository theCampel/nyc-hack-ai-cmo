## Video Generation Agent

Agent that generates narrated videos using ElevenLabs (TTS) and FAL (`veed/fabric-1.0`). It listens on Coral Server via SSE and exposes a tool `generate_video` the agent can call in response to mentions.

## Capabilities
- Generate MP3 from text via ElevenLabs
- Upload audio to FAL storage
- Invoke `veed/fabric-1.0` to produce a video (480p/720p)

## Setup

1) Install dependencies (uses uv)

```bash
uv pip install --upgrade pip
uv sync
```

2) Environment variables (see `.env_sample`)
- `CORAL_SSE_URL` and `CORAL_AGENT_ID` for Coral Server connection
- `FAL_KEY` for FAL API authentication
- `ELEVENLABS_API_KEY` for ElevenLabs TTS
- Optional: `ELEVENLABS_VOICE_ID` (defaults to Rachel)

3) Run locally

```bash
uv run main.py
```

## Tool: generate_video
Inputs:
- `text` (string): text to narrate
- `image_url` (string, optional): image background URL. If omitted, the agent uploads its bundled 480x640 JPEG to FAL and uses that.
- `resolution` (enum): `480p` or `720p`
- `voice_id` (string, optional)
- `wait` (bool): wait for final video or return request_id

Output:
- If `wait=true`, returns a URL string to the MP4 on success
- Else returns `request_id=...`
