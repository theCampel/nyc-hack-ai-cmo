import urllib.parse
from dotenv import load_dotenv
import os, json, asyncio, traceback, time, random, string
import requests
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import StructuredTool


def get_tools_description(tools):
    return "\n".join(
        f"Tool: {tool.name}, Schema: {json.dumps(tool.args).replace('{', '{{').replace('}', '}}')}"
        for tool in tools
    )

async def create_agent(coral_tools, agent_tools):
    coral_tools_description = get_tools_description(coral_tools)
    agent_tools_description = get_tools_description(agent_tools)
    combined_tools = coral_tools + agent_tools
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are the 10Web agent. You listen for mentions and create AI-powered WordPress websites via your 10Web tools, then report results back clearly with links and credentials.

            Use EXACT tool names from the lists below. Follow these steps:
            1. Call coral_wait_for_mentions (timeoutMs: 60000) to receive instructions. Keep threadId and senderId from the mention event.
            2. If the instruction asks to create a website, extract: business_name, business_description, business_type (optional), region (optional). Defaults: business_type="business", region="us-central1-c".
            3. Call create_ai_website with those fields. If business_description or business_name is missing, ask a clarifying question via coral_send_message first and wait again.
            4. Parse the tool result (text may include a trailing raw=JSON) to extract website_url, admin_url, admin_username, admin_password. If website_url is missing but website_id exists, inform the user and include website_id and any error.
            4.1. If you have an email (from TENWEB_AUTOLOGIN_EMAIL env or by asking the sender), call generate_autologin_url to include a one-click admin login link that does not need a password.
            5. Compose a concise response including these fields explicitly (include autologin if available):
               - Website URL: <website_url>
               - Admin URL: <admin_url>
               - Username: <admin_username>
               - Password: <admin_password>
               - Autologin URL: <autologin_url> (if available)
            6. Use coral_send_message with: threadId=<threadId>, mentions=[<senderId>], content=<your composed response>.
            7. If any error occurs, send a brief error summary with any available details using coral_send_message to the same thread/sender.
            8. Wait for 2 seconds and repeat from step 1.

            Coral tools available: {coral_tools_description}
            Your tools available: {agent_tools_description}
            """
        ),
        ("placeholder", "{agent_scratchpad}")
    ])

    model = init_chat_model(
        model=os.getenv("MODEL_NAME", "gpt-4.1"),
        model_provider=os.getenv("MODEL_PROVIDER", "openai"),
        api_key=os.getenv("MODEL_API_KEY"),
        temperature=os.getenv("MODEL_TEMPERATURE", "0.1"),
        max_tokens=os.getenv("MODEL_MAX_TOKENS", "8000"),
        base_url=os.getenv("MODEL_BASE_URL", None)
    )
    agent = create_tool_calling_agent(model, combined_tools, prompt)
    return AgentExecutor(agent=agent, tools=combined_tools, verbose=True, handle_parsing_errors=True)

async def main():

    runtime = os.getenv("CORAL_ORCHESTRATION_RUNTIME", None)
    if runtime is None:
        load_dotenv()

    # Support either CORAL_CONNECTION_URL (full connection URL incl. query) or
    # CORAL_SSE_URL (base SSE endpoint where we append query params).
    conn_url = os.getenv("CORAL_CONNECTION_URL")
    sse_base = os.getenv("CORAL_SSE_URL")
    agentID = os.getenv("CORAL_AGENT_ID")

    if conn_url:
        CORAL_SERVER_URL = conn_url
    else:
        coral_params = {
            "agentId": agentID,
            "agentDescription": "An agent that can create AI-generated WordPress sites on 10Web (defaults to us-central1-c)",
        }
        query_string = urllib.parse.urlencode(coral_params)
        if not sse_base:
            raise ValueError("Set CORAL_CONNECTION_URL or CORAL_SSE_URL env var for Coral Server connection")
        sep = "&" if ("?" in sse_base) else "?"
        CORAL_SERVER_URL = f"{sse_base}{sep}{query_string}"
    print(f"Connecting to Coral Server: {CORAL_SERVER_URL}")

    timeout = float(os.getenv("TIMEOUT_MS", "300000"))
    client = MultiServerMCPClient(
        connections={
            "coral": {
                "transport": "sse",
                "url": CORAL_SERVER_URL,
                "timeout": timeout,
                "sse_read_timeout": timeout,
            }
        }
    )

    print("Coral Server Connection Established")

    coral_tools = await client.get_tools(server_name="coral")
    agent_tools = tenweb_tools()

    print(f"Coral tools count: {len(coral_tools)} and 10Web tools count: {len(agent_tools)}")

    agent_executor = await create_agent(coral_tools, agent_tools)

    while True:
        try:
            print("Starting new agent invocation")
            await agent_executor.ainvoke({"agent_scratchpad": []})
            print("Completed agent invocation, restarting loop")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error in agent loop: {str(e)}")
            print(traceback.format_exc())
            await asyncio.sleep(5)

# ---------------------
# 10Web Tools (inline)
# ---------------------

API_BASE_URL = "https://api.10web.io"
DEFAULT_REGION = "us-central1-c"


def _require_api_key() -> str | None:
    return os.getenv("TENWEB_API_KEY")


def _generate_random_subdomain() -> str:
    adjectives = [
        "amazing", "awesome", "brilliant", "creative", "dynamic",
        "elegant", "fantastic", "gorgeous", "innovative", "magical",
    ]
    nouns = [
        "site", "web", "studio", "hub", "space",
        "digital", "online", "portal", "platform", "zone",
    ]
    return f"{random.choice(adjectives)}-{random.choice(nouns)}-{random.randint(1,9999)}"



def _generate_secure_password() -> str:
    specials = "!@#$%^&*"
    chars = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice(specials),
    ]
    pool = string.ascii_letters + string.digits + specials
    chars += [random.choice(pool) for _ in range(8)]
    random.shuffle(chars)
    return "".join(chars)


class CreateAIWebsiteArgs(BaseModel):
    business_name: str = Field(..., description="Name of the business/website")
    business_description: str = Field(..., description="Description of the business for AI content")
    business_type: str = Field("business", description="Type of business (e.g., restaurant, agency, blog, ecommerce)")
    subdomain: str | None = Field(None, description="Subdomain to use; auto-generated if not provided")
    region: str = Field(DEFAULT_REGION, description="Deployment region; defaults to us-central1-c")
    admin_username: str = Field("admin", description="Admin username for the WP site")
    admin_password: str | None = Field(None, description="Admin password; if omitted a secure password is generated")
    is_demo: int = Field(0, description="1 to create a demo site that auto-expires; else 0")
    demo_domain_delete_after_days: int | None = Field(None, description="If demo=1, number of days before deletion (1-30)")


def _post_create_ai_website(payload: dict, api_key: str) -> dict:
    url = f"{API_BASE_URL}/v1/hosting/ai-website"
    resp = requests.post(url, headers={"x-api-key": api_key, "Content-Type": "application/json"}, data=json.dumps(payload))
    resp.raise_for_status()
    return resp.json()


def _get_account_websites(api_key: str) -> dict:
    url = f"{API_BASE_URL}/v1/account/websites"
    resp = requests.get(url, headers={"x-api-key": api_key})
    resp.raise_for_status()
    return resp.json()


def tenweb_create_ai_website(
    business_name: str,
    business_description: str,
    business_type: str = "business",
    subdomain: str | None = None,
    region: str = DEFAULT_REGION,
    admin_username: str = "admin",
    admin_password: str | None = None,
    is_demo: int = 0,
    demo_domain_delete_after_days: int | None = None,
) -> str:
    api_key = _require_api_key()
    if not api_key:
        return "ERROR: TENWEB_API_KEY not set"

    if not subdomain:
        subdomain = _generate_random_subdomain()
    if not admin_password:
        admin_password = _generate_secure_password()
    if not region:
        region = DEFAULT_REGION

    payload = {
        "subdomain": subdomain,
        "region": region,
        "site_title": business_name,
        "admin_username": admin_username,
        "admin_password": admin_password,
        "business_type": business_type or "business",
        "business_name": business_name,
        "business_description": business_description,
        "is_demo": int(is_demo or 0),
    }
    if payload["is_demo"] == 1 and demo_domain_delete_after_days:
        payload["demo_domain_delete_after_days"] = int(demo_domain_delete_after_days)

    try:
        result = _post_create_ai_website(payload, api_key)
        website_id = result.get("website_id")
        website_url = result.get("website_url")

        # If URL not ready, poll account websites until available (no timeout)
        if not website_url and website_id:
            poll_interval = float(os.getenv("TENWEB_POLL_INTERVAL_SEC", "5"))
            while True:
                try:
                    listing = _get_account_websites(api_key)
                    items = listing.get("data") or listing.get("websites") or []
                    for item in items:
                        try:
                            if int(item.get("id", -1)) == int(website_id):
                                site_url = item.get("site_url") or item.get("url")
                                if site_url:
                                    website_url = site_url
                                    break
                        except Exception:
                            continue
                    if website_url:
                        break
                except Exception:
                    pass
                time.sleep(poll_interval)

        admin_url = (website_url + "/wp-admin") if website_url else None
        summary = [
            "Website created via 10Web:",
            f"- Website ID: {website_id}",
            f"- Website URL: {website_url}" if website_url else "- Website URL: (still generating)",
            f"- Admin URL: {admin_url}" if admin_url else "- Admin URL: (still generating)",
            f"- Username: {admin_username}",
            f"- Password: {admin_password}",
        ]
        raw = {
            "status": "ok",
            "request": {
                "subdomain": subdomain,
                "region": region,
                "admin_username": admin_username,
            },
            "result": result,
            "derived": {"website_url": website_url, "admin_url": admin_url},
        }
        # Optionally generate auto-login link if email is provided via env
        autologin_email = os.getenv("TENWEB_AUTOLOGIN_EMAIL")
        if autologin_email and website_id and website_url:
            try:
                auto = _generate_autologin_token(website_id, website_url)
                token = auto.get("token") or auto.get("data", {}).get("token")
                if token:
                    autologin_url = f"{website_url}/wp-admin/?twb_wp_login_token={token}&email={urllib.parse.quote(autologin_email)}"
                    summary.append(f"- Autologin URL (5 min valid): {autologin_url}")
                    raw["derived"]["autologin_url"] = autologin_url
            except Exception:
                pass

        return "\n".join(summary) + "\n\nraw=" + json.dumps(raw)
    except requests.HTTPError as he:
        details = he.response.text if he.response is not None else str(he)
        return (
            "ERROR creating website via 10Web.\n"
            f"- HTTP: {he.response.status_code if he.response else 'unknown'}\n"
            f"- Details: {details}"
        )
    except Exception as e:
        return f"ERROR creating website via 10Web: {str(e)}"


class WebsiteIdArgs(BaseModel):
    website_id: int = Field(..., description="10Web website ID")


def tenweb_get_account_websites() -> str:
    api_key = _require_api_key()
    if not api_key:
        return "ERROR: TENWEB_API_KEY not set"
    try:
        data = _get_account_websites(api_key)
        return json.dumps(data)
    except Exception as e:
        return f"ERROR fetching account websites: {str(e)}"


def tenweb_get_website_user_info(website_id: int) -> str:
    api_key = _require_api_key()
    if not api_key:
        return "ERROR: TENWEB_API_KEY not set"
    url = f"{API_BASE_URL}/v1/hosting/websites/{website_id}/user_info"
    try:
        resp = requests.get(url, headers={"x-api-key": api_key})
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return f"ERROR fetching user_info for website {website_id}: {str(e)}"


def tenweb_get_website_instance_info(website_id: int) -> str:
    api_key = _require_api_key()
    if not api_key:
        return "ERROR: TENWEB_API_KEY not set"
    url = f"{API_BASE_URL}/v1/hosting/websites/{website_id}/instance-info"
    try:
        resp = requests.get(url, headers={"x-api-key": api_key})
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return f"ERROR fetching instance-info for website {website_id}: {str(e)}"


class SubdomainCheckArgs(BaseModel):
    subdomain: str = Field(..., description="Subdomain to check availability")


def tenweb_check_subdomain(subdomain: str) -> str:
    api_key = _require_api_key()
    if not api_key:
        return "ERROR: TENWEB_API_KEY not set"
    url = f"{API_BASE_URL}/v1/hosting/websites/subdomain/check?subdomain={urllib.parse.quote(subdomain)}"
    try:
        resp = requests.get(url, headers={"x-api-key": api_key})
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return f"ERROR checking subdomain {subdomain}: {str(e)}"


def tenweb_generate_subdomain() -> str:
    api_key = _require_api_key()
    if not api_key:
        return "ERROR: TENWEB_API_KEY not set"
    url = f"{API_BASE_URL}/v1/hosting/websites/subdomain/generate"
    try:
        resp = requests.get(url, headers={"x-api-key": api_key})
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return f"ERROR generating subdomain: {str(e)}"


class AutoLoginArgs(BaseModel):
    website_id: int = Field(..., description="10Web website ID")
    website_url: str = Field(..., description="Base website URL (e.g., https://mysite.10web.club)")
    email: str = Field(..., description="Email to use for autologin (existing admin or will create one)")


def _generate_autologin_token(website_id: int, website_url: str) -> dict:
    api_key = _require_api_key()
    if not api_key:
        raise ValueError("TENWEB_API_KEY not set")
    admin_url = f"{website_url.rstrip('/')}/wp-admin"
    url = f"{API_BASE_URL}/v1/account/websites/{website_id}/single?admin_url={urllib.parse.quote(admin_url)}"
    resp = requests.get(url, headers={"x-api-key": api_key})
    resp.raise_for_status()
    try:
        return resp.json()
    except Exception:
        return {"raw": resp.text}


def tenweb_generate_autologin_url(website_id: int, website_url: str, email: str) -> str:
    """Return a one-click autologin URL for the WP admin, valid for ~5 minutes."""
    try:
        data = _generate_autologin_token(website_id, website_url)
        token = data.get("token") or (data.get("data") or {}).get("token")
        if token:
            autologin_url = f"{website_url.rstrip('/')}/wp-admin/?twb_wp_login_token={token}&email={urllib.parse.quote(email)}"
            return json.dumps({
                "status": "ok",
                "autologin_url": autologin_url,
                "note": "Token is single-use and expires in ~5 minutes",
            })
        return json.dumps({"status": "error", "message": "Token not found", "raw": data})
    except requests.HTTPError as he:
        return json.dumps({
            "status": "error",
            "http": he.response.status_code if he.response else None,
            "details": he.response.text if he.response is not None else str(he),
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def tenweb_tools():
    return [
        StructuredTool.from_function(
            name="create_ai_website",
            description=(
                "Create an AI-generated WordPress website on 10Web. "
                "Required: business_name, business_description. Optional: business_type, subdomain, "
                "region (defaults to 'us-central1-c'), admin_username (default 'admin'), admin_password (auto-generated), "
                "is_demo (0 or 1), demo_domain_delete_after_days (1-30 when is_demo=1)."
            ),
            func=tenweb_create_ai_website,
            args_schema=CreateAIWebsiteArgs,
        ),
        StructuredTool.from_function(
            name="generate_autologin_url",
            description=(
                "Generate a one-click admin autologin URL for a website (no password needed). "
                "Required: website_id, website_url, email (via TENWEB_AUTOLOGIN_EMAIL env or pass to agent)."
            ),
            func=tenweb_generate_autologin_url,
            args_schema=AutoLoginArgs,
        ),
        StructuredTool.from_function(
            name="tenweb_get_account_websites",
            description="List all websites for the 10Web account (raw JSON).",
            func=tenweb_get_account_websites,
        ),
        StructuredTool.from_function(
            name="tenweb_get_website_user_info",
            description="Get user/db/sftp info for a website by ID (raw JSON).",
            func=tenweb_get_website_user_info,
            args_schema=WebsiteIdArgs,
        ),
        StructuredTool.from_function(
            name="tenweb_get_website_instance_info",
            description="Get instance info (IP, region) for a website by ID (raw JSON).",
            func=tenweb_get_website_instance_info,
            args_schema=WebsiteIdArgs,
        ),
        StructuredTool.from_function(
            name="tenweb_check_subdomain",
            description="Check if a subdomain is available.",
            func=tenweb_check_subdomain,
            args_schema=SubdomainCheckArgs,
        ),
        StructuredTool.from_function(
            name="tenweb_generate_subdomain",
            description="Generate a random available subdomain via API.",
            func=tenweb_generate_subdomain,
        ),
    ]

if __name__ == "__main__":
    asyncio.run(main())
