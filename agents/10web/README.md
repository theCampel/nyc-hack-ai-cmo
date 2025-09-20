## 10Web Agent

The 10Web Agent creates AI-powered WordPress websites via the 10Web API. It runs in Coral, listens for mentions, and uses its own tools to provision a site. Default deployment region: `us-central1-c`.

## Responsibility
Given business details (name, description, type), create a website with AI-generated content on 10Web and reply with the website URL and admin credentials.

## Details
- Framework: LangChain
- Tools used: Coral MCP Tools, built-in 10Web tools (HTTP calls from OpenAPI)
- AI model: GPT-4.1 (configurable)
- Docs: See `openapi.yaml` (`/v1/hosting/ai-website` and related)
- License: MIT

## Setup

### 1) Install deps

```bash
cd agents/10web
pip install uv
uv sync
```

### 2) Environment

```bash
export MODEL_API_KEY=...             # LLM key
export MODEL_NAME=gpt-4.1            # optional
export MODEL_PROVIDER=openai         # optional
export MODEL_MAX_TOKENS=16000        # optional
export MODEL_TEMPERATURE=0.3         # optional

export TENWEB_API_KEY=...            # required (10Web x-api-key)
export CORAL_AGENT_ID=tenweb-agent   # any unique ID
export CORAL_SSE_URL=http://localhost:5555/sse/v1/1/1/<session>/sse  # or use CORAL_CONNECTION_URL
```

## Run

```bash
uv run python main.py
```

## Example Instruction (via Interface Agent)

"Create a website for 'Acme Bakery'. Description: Fresh artisan bread and pastries. Type: restaurant."

Expected reply includes:
- Website URL
- Admin URL (wp-admin)
- Username and Password
