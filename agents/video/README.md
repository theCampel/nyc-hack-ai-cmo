## Video Generation Agent

Agent that composites product imagery with a model shot via FAL's Product Holding model (`fal-ai/image-apps-v2/product-holding`), synthesizes narration with ElevenLabs (TTS), and renders the final clip with FAL (`veed/fabric-1.0`). It listens on Coral Server via SSE and exposes a tool `generate_video` the agent can call in response to mentions.

## Capabilities
- Blend the bundled `test.jpeg` + `product.jpeg` assets through the Product Holding model (`fal-ai/image-apps-v2/product-holding`) to produce a marketing-ready hero frame
- Generate MP3 narration from text via ElevenLabs
- Upload generated artifacts to FAL storage
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
- Optional: `PRODUCT_HOLDING_MODEL` (defaults to `fal-ai/image-apps-v2/product-holding`) and `PRODUCT_HOLDING_EXTRA_ARGS` (JSON) for fine-tuning how the product is blended into frame

3) Run locally

```bash
uv run main.py
```

## Tool: generate_video
Inputs:
- `text` (string): text to narrate
- `image_url` (string, optional): background URL override. If omitted, the agent uploads the two bundled 480×640 JPEGs to the Product Holding model and uses the returned image URL (falling back to the raw test image on failure).
- `resolution` (enum): `480p` or `720p`
- `voice_id` (string, optional)
- `wait` (bool): wait for final video or return request_id

Output:
- If `wait=true`, returns a URL string to the MP4 on success
- Else returns `request_id=...`
